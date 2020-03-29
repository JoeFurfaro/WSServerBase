"""
This script creates the server object and processes incoming requests
Help for all functionality of this script is available in the documentation
"""

import logging
import asyncio
import websockets

from rdk3 import config
from rdk3 import plugins
from rdk3.events import Events

async def run_server(socket, path):
    """
    Handles the behaviour of the main Websocket server thread (main function)
    """
    msg = await socket.recv()
    print(msg)
    await socket.send("test!");

def format_packet(x):
    """
    Formats a dictionary or list of dictionaries into a packet string in JSON format to be sent
    """
    if type(d) in (list, dict):
        return json.dumps(x)
    return None

def parse_packet(x):
    """
    Parses a JSON packet string into a dictionary object or list of dictionary objects
    """
    if type(x) == str:
        return js.loads(x)
    return None

def start(quiet):
    """
    Starts the main application WebSocket server
    """
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

    # Trigger server start event handlers
    plugins.trigger_handlers(Events.SERVER_START)

    # Load server information from config
    address = config.global_config()["GENERAL"]["server_address"]
    port = int(config.global_config()["GENERAL"]["server_port"])

    # Start the server
    logging.info("[SERVER] Starting RDK3 WebSocket server on " + address + ":" + str(port))
    if not quiet:
        print("[SERVER] Starting RDK3 WebSocket server on " + address + ":" + str(port))

    server = websockets.serve(run_server, address, port)

    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()
