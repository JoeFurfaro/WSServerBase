"""
This script creates the server object and processes incoming requests
Help for all functionality of this script is available in the documentation
"""

import logging
import asyncio
import websockets
from rdk3 import config

async def run_server(socket, path):
    """
    Handles the behaviour of the main Websocket server thread
    """
    msg = await socket.recv()
    print(msg)
    await socket.send("test!");


def start(quiet):
    """
    Starts the main application WebSocket server
    """
    config.autogen(quiet)
    config.load(quiet)

    address = config.get("GENERAL", "server_address")
    port = int(config.get("GENERAL", "server_port"))

    if not quiet:
        print("Starting RDK3 WebSocket server on " + address + ":" + str(port))

    server = websockets.serve(run_server, address, port)

    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()
