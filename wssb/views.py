"""
This script handles the processing of all core WSSB commands from clients
Help for all functionality of this script is available in the documentation
"""

import logging
import json

from wssb.events import Events
from wssb import plugins
from wssb import users

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

def error(error_code, message):
    """
    Generates an error response packet
    """
    return { "type": "response", "status": "error", "code": error_code, "message": message }

def success(success_code, message):
    """
    Generates a success response packet
    """
    return { "type": "response", "status": "success", "code": success_code, "message": message }

def info(info_code, message):
    """
    Generates an info response packet
    """
    return { "type": "response", "status": "info", "code": info_code, "message": message }

def process(request, socket, quiet):
    """
    Process a core request from client
    Return None if no request matches are found
    """

    if request["code"] == "auth":
        return view_auth(request, socket, quiet)

    return None

def view_auth(request, socket, quiet):
    """
    Identifies and authenticates a user
    """
    if request["user_name"] != None:
        user = users.find_user(request["user_name"])
        if user != None:
            if plugins.trigger_conditional_handlers(Events.USER_AUTH_ATTEMPT, { "request": request, "user": user }):
                users.connected.append(user)
                plugin_responses = plugins.trigger_handlers(Events.USER_AUTHENTICATED, { "user": user })
                logging.info("[SERVER] User '" + request["user_name"] + "' has been added to the list of connected users.")
                if not quiet:
                    print("[SERVER] User '" + request["user_name"] + "' has been added to the list of connected users.")
                return { "user": user, "plugin_responses": plugin_responses }
            else:
                return None
        else:
            return error("WSSB_AUTH_USER_NOT_FOUND", "The user name specified does not exist on the server.")
    else:
        return error("WSSB_AUTH_INVALID_SYNTAX", "Invalid packet syntax.")
