"""
This script handles the processing of all core WSSB commands from clients
Help for all functionality of this script is available in the documentation
"""

import logging

from wssb.events import Events
from wssb import plugins
from wssb import users

def generr(error_code, message):
    """
    Generates an error response packet
    """
    return { "type": "response", "status": "error", "code": error_code, "message": message }

def gensuc(success_code, message):
    """
    Generates a success response packet
    """
    return { "type": "response", "status": "success", "code": success_code, "message": message }


def process(cmd, socket, quiet):
    """
    Process a core command from client
    Return None if no command matches are found
    Returns False if expected plugin response
    """

    if cmd["name"] == "identify":
        return cmd_identify(cmd, socket, quiet)

    return None

def cmd_identify(cmd, socket, quiet):
    """
    Identifies and authenticates a user
    """
    if cmd["user_name"] != None:
        user = users.find_user(cmd["user_name"])
        if user != None:
            if plugins.trigger_handlers(Events.USER_AUTH_ATTEMPT, { "command": cmd, "socket": socket, "user": user }):
                if user not in users.connected:
                    users.connected.add(user)
                    logging.info("[SERVER] User '" + cmd["user_name"] + "' has been added to the list of connected users")
                    if not quiet:
                        print("[SERVER] User '" + cmd["user_name"] + "' has been added to the list of connected users")
                    return gensuc("wssb_s0", "You are now logged in!")
                else:
                    return generr("wssb_e1", "You are already connected to the server!")
            else:
                return False
        else:
            return generr("wssb_e2", "The user name specified does not exist on the server")
    else:
        return generr("wssb_e0", "Invalid packet syntax")
