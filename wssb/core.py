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
from wssb import cmds
from wssb.events import Events

quiet_mode = False

def format_packet(x):
    """
    Formats a dictionary or list of dictionaries into a packet string in JSON format to be sent
    """
    if type(x) in (list, dict):
        return json.dumps(x)
    return None

def parse_packet(x):
    """
    Parses a JSON packet string into a dictionary object or list of dictionary objects
    TODO: Should validate contents and integrity in the future
    """
    if type(x) == str:
        parsed = json.loads(x)
        if type(parsed) == dict:
            return [parsed]
        return parsed
    return None

async def run_server(socket, path):
    """
    Handles the behaviour of the main Websocket server thread (main function)
    """
    global quiet_mode

    while True:
        data = await socket.recv()
        packets = parse_packet(data)
        for packet in packets:
            if packet["type"] == "cmd":
                response = cmds.process(packet, socket, quiet_mode)
                if response == None:
                    # Try running plugin commands
                    pass
                else:
                    await socket.send(format_packet(response))

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
    if not plugins.trigger_handlers(Events.SERVER_START, None):
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
