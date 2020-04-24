"""
This script creates the server object and processes incoming requests
Help for all functionality of this script is available in the documentation
"""

import logging
import asyncio
import websockets
import json

from wssb import config
from wssb import plugins
from wssb import users
from wssb import views
from wssb.events import Events

quiet_mode = False

async def run_server(socket, path):
    """
    Handles the behaviour of the main Websocket server thread (main function)
    """
    global quiet_mode

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
                    response = views.process(request, socket, quiet_mode)
                    if response == None:
                        # Trigger plugin event handler for custom commands
                        responses = plugins.handle(request, session_user)
                        for response in responses:
                            await socket.send(views.format_packet(response))
                        if len(responses) == 0:
                            await socket.send(views.format_packet(views.error("WSSB_REQUEST_CODE_NOT_FOUND", "The request code given could not be found in any core or plugin features.")))
                    elif type(response) == dict:
                        # Authenticate user
                        authenticated = True
                        session_user = response["user"]
                        await socket.send(views.format_packet(views.success("WSSB_USER_AUTHENTICATED", "You are now logged in!")))
                        for plugin_response in response["plugin_responses"]:
                            await socket.send(views.format_packet(plugin_response))
                    else:
                        await socket.send(views.format_packet(response))
    except Exception as e:
        print(e)
    finally:
        if session_user != None:
            if plugins.trigger_conditional_handlers(Events.USER_DISCONNECT, { "user": session_user }):
                users.connected.remove(session_user)
                logging.info("[SERVER] User '" + session_user.name + "' has disconnected.")
                if not quiet_mode:
                    print("[SERVER] User '" + session_user.name + "' has disconnected.")

def start(quiet):
    """
    Starts the main application WebSocket server
    """
    global quiet_mode
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
    plugins.load_all(quiet)

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

    server = websockets.serve(run_server, address, port)

    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()
