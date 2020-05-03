"""
This script creates the server object and processes incoming requests
Help for all functionality of this script is available in the documentation
"""

import logging
import asyncio
import websockets
import signal
import json
import traceback

from wssb import config
from wssb import plugins
from wssb import users
from wssb import views
from wssb.events import Events

quiet_mode = False
stop = None

def get_target_conns(response, socket):
    resp = response["response"]
    target = response["target"]
    target_conns = []
    if target == None:
        return []
    if target.mode == "ALL":
        for user in users.connected():
            target_conns += user._sockets
    elif target.mode == "SOURCE":
        target_conns = [socket]
    else:
        for target_user in target.users:
            for online_user in users.connected():
                if target_user != None and target_user.name == online_user.name:
                    target_conns += online_user._sockets
        for target_group in target.groups:
            for online_user in users.connected():
                if target_group != None and online_user.belongs_to(target_group):
                    for conn in online_user._sockets:
                        if conn not in target_conns:
                            target_conns.append(conn)
    return target_conns

async def run_server(socket, path):
    """
    Handles the behaviour of the main Websocket server thread (main function)
    """
    global quiet_mode, stop

    authenticated = False
    session_user = None

    try:
        while True:
            data = await socket.recv()
            packets = views.parse_packet(data)
            for request in packets:
                if request["type"] != None and request["type"] == "request":
                    if not authenticated and request["code"] != None and request["code"] != "auth":
                        await socket.send(views.format_packet(views.error("WSSB_USER_NOT_AUTHENTICATED", "You have not yet been authenticated!")))
                        break
                    response = views.process(session_user, request, socket, quiet_mode)
                    if response == None:
                        # Trigger plugin event handler for custom commands
                        responses = plugins.handle(request, session_user)
                        for response in responses:
                            target_conns = get_target_conns(response, socket)
                            for conn in target_conns:
                                await conn.send(views.format_packet(response["response"]))
                        if len(responses) == 0:
                            await socket.send(views.format_packet(views.error("WSSB_REQUEST_CODE_NOT_FOUND", "The request code given could not be found in any core or plugin features.")))
                    elif type(response) == dict and "wssb_authenticated" in response:
                        # Authenticate user
                        authenticated = True
                        session_user = response["user"]
                        users.register_socket(session_user.name, socket)
                        users.connected_sockets.add(socket)
                        await socket.send(views.format_packet(views.success("WSSB_USER_AUTHENTICATED", "You are now logged in!")))
                        for plugin_response in response["plugin_responses"]:
                            target_conns = get_target_conns(plugin_response, socket)
                            for conn in target_conns:
                                await conn.send(views.format_packet(plugin_response["response"]))
                    else:
                        # Check for core flagged actions
                        if "to_close" in response:
                            for sock in response["to_close"]:
                                await sock.send(views.format_packet(views.info("WSSB_USER_KICKED", response["close_reason"])))
                                await sock.close()

                        if "target" in response:
                            target_conns = get_target_conns(response, socket)
                            for conn in target_conns:
                                await conn.send(views.format_packet(response["response"]))
                        else:
                            await socket.send(views.format_packet(response))

                        if "stop" in response:
                            if response["stop"]:
                                logging.info("[SERVER] " + session_user.name + " is closing the server")
                                if not quiet_mode:
                                    print("[SERVER] " + session_user.name + " is closing the server")
                                plugins.trigger_handlers(Events.SERVER_STOP, None)
                                stop.set_result(0)
    except Exception as e:
        # Exceptions to ignore when printing can be added to the conn_excp blacklist
        conn_excp = (
            websockets.exceptions.ConnectionClosedOK,
        )
        if type(e) not in conn_excp and not quiet_mode:
            print(traceback.format_exc())
    finally:
        if session_user != None:
            users.connected_sockets.remove(socket)
            plugins.trigger_handlers(Events.USER_DISCONNECT, { "user": session_user, "socket": socket })
            users.unregister_socket(session_user.name, socket)
            logging.info("[SERVER] User '" + session_user.name + "' has disconnected.")
            if not quiet_mode:
                print("[SERVER] User '" + session_user.name + "' has disconnected.")

async def start_core(address, port, stop):
    async with websockets.serve(run_server, address, port):
        await stop

def start(quiet):
    """
    Starts the main application WebSocket server
    """
    global quiet_mode, stop
    quiet_mode = quiet

    # Autogenerate the plugins folder
    plugins.autogen_folder(quiet)

    # Load server config
    if config.load_global_config():
        logging.info("[SERVER] Loaded server configuration file successfully")
        if not quiet:
            print("[SERVER] Loaded server configuration file successfully")
    else:
        if not quiet:
            print("[SERVER] Could not load server configuration file")
        logging.error("[SERVER] Could not load server configuration file")

    # Load all plugins
    if not plugins.load_all(quiet):
        return

    # Load all users
    config.load_users_config()
    config.load_groups_config()
    users.reload_all()

    # Trigger server start event handlers
    if not plugins.trigger_conditional_handlers(Events.SERVER_START, None):
        return

    # Load server information from config
    address = config.global_config()["GENERAL"]["server_address"]
    port = int(config.global_config()["GENERAL"]["server_port"])

    # Start the server
    logging.info("[SERVER] Starting WebSocket server on " + address + ":" + str(port))
    if not quiet:
        print("[SERVER] Starting WebSocket server on " + address + ":" + str(port))

    loop = asyncio.get_event_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    loop.run_until_complete(start_core(address, port, stop))

    logging.info("[SERVER] Server closed")
    if not quiet_mode:
        print("[SERVER] Server closed")
