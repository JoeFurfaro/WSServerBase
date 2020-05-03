"""
This script handles the processing of all core WSSB commands from clients
Help for all functionality of this script is available in the documentation
"""

import logging
import json

from wssb.events import Events
from wssb import plugins
from wssb import users
from wssb import config

class Target():
    """
    This class defines a response routing target
    """
    def __init__(self, users=[], groups=[]):
        """
        Initializes a response router target object
        """
        self.mode = "ADDRESS"
        self.users, self.groups = users, groups

    def all():
        """
        Generates a target object to all connected users
        """
        all_target = Target()
        all_target.mode = "ALL"
        return all_target

    def source():
        """
        Generates a target object to the request source user
        """
        source_target = Target()
        source_target.mode = "SOURCE"
        return source_target

    def user(user):
        """
        Generates a target object that targets a certain user
        """
        if type(user) == str:
            user_obj = users.find_user(user)
            return Target(users=[user_obj]) if user_obj != None else None
        return Target(users=[user])

    def group(group):
        """
        Generates a target object that targets a certain group
        """
        if type(group) == str:
            group_obj = users.find_group(group)
            return Target(groups=[group_obj]) if group_obj != None else None
        return Target(groups=[group_obj])


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

def resp(response, target, to_close=[], close_reason="You have been kicked from the server!", stop=False):
    """
    Generates a response targetted at the given target
    """
    return { "response": response, "target": target, "to_close": to_close, "close_reason": close_reason, "stop": stop }

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

def process(session_user, request, socket, quiet):
    """
    Process a core request from client
    Return None if no request matches are found
    """
    if request["code"] == "auth":
        return view_auth(session_user, request, socket, quiet)
    elif request["code"] == "reloadcfg":
        return view_reloadcfg(session_user, request, quiet)
    elif request["code"] == "reloadusers":
        return view_reloadusers(session_user, request, quiet)
    elif request["code"] == "reloadplugins":
        return view_reloadplugins(session_user, request, quiet)
    elif request["code"] == "reload":
        return view_reload(session_user, request, quiet)
    elif request["code"] == "stop":
        return view_stop(session_user, request, quiet)

    return None

def view_auth(session_user, request, socket, quiet):
    """
    Identifies and authenticates a user
    """
    if session_user != None:
        return error("WSSB_ALREADY_AUTHENTICATED", "You have already been authenticated.")
    if request["user_name"] != None:
        user = users.find_user(request["user_name"])
        if user != None:
            if plugins.trigger_conditional_handlers(Events.USER_AUTH_ATTEMPT, { "request": request, "user": user, "socket": socket }):
                plugin_responses = plugins.trigger_handlers(Events.USER_AUTHENTICATED, { "user": user, "socket": socket })
                logging.info("[SERVER] User '" + request["user_name"] + "' has been added to the list of connected users.")
                if not quiet:
                    print("[SERVER] User '" + request["user_name"] + "' has been added to the list of connected users.")
                return { "wssb_authenticated": True, "user": user, "plugin_responses": plugin_responses }
            else:
                return error("WSSB_AUTH_FAILED", "User authentication failed!")
        else:
            return error("WSSB_AUTH_USER_NOT_FOUND", "The user name specified does not exist on the server.")
    else:
        return error("WSSB_AUTH_INVALID_SYNTAX", "Invalid packet syntax.")

def view_stop(session_user, request, quiet):
    """
    Stops the server cleanly
    """
    if session_user.has_permission("wssb.stop"):
        return resp(success("WSSB_STOPPING_SERVER", "Shutting down server now..."), Target.source(), stop=True)
    return resp(error("WSSB_ACCESS_DENIED", "You do not have permission to stop the server!"), Target.source())

def view_reload(session_user, request, quiet):
    """
    Reloads the global server config and the user services module
    """
    if session_user.has_permission("wssb.reload"):
        cfg_resp = view_reloadcfg(session_user, request, quiet)
        users_resp = view_reloadusers(session_user, request, quiet)
        plugins_resp = view_reloadplugins(session_user, request, quiet)
        logging.info("[SERVER] The server has been reloaded by \'" + session_user.name + "\'")
        if not quiet:
            print("[SERVER] The server has been reloaded by \'" + session_user.name + "\'")
        return resp(success("WSSB_RELOADED", "The server has been reloaded successfully!"), Target.source(), to_close=users_resp["to_close"], stop=plugins_resp["stop"])

    return resp(error("WSSB_ACCESS_DENIED", "You do not have permission to reload the server!"), Target.source())


def view_reloadplugins(session_user, request, quiet):
    """
    Reloads all plugins
    """
    if session_user.has_permission("wssb.reload.plugins"):
        plugins.trigger_handlers(Events.SERVER_STOP, None)
        if plugins.reload_all(quiet):
            logging.info("[SERVER] The server plugins have been reloaded by \'" + session_user.name + "\'")
            if not quiet:
                print("[SERVER] The server plugins have been reloaded by \'" + session_user.name + "\'")
            return resp(success("WSSB_PLUGINS_RELOADED", "Server plugins have been reloaded successfully!"), Target.source())
        else:
            return resp(error("WSSB_PLUGIN_RELOAD_FAILURE", "Could not reload server plugins"), None, stop=True)
    return resp(error("WSSB_ACCESS_DENIED", "You do not have permission to reload the server plugins!"), Target.source())


def view_reloadcfg(session_user, request, quiet):
    """
    Reloads the global server config
    """
    if session_user.has_permission("wssb.reload.cfg"):
        config.global_config().reload()
        logging.info("[SERVER] The global config has been reloaded by \'" + session_user.name + "\'")
        if not quiet:
            print("[SERVER] The global config has been reloaded by \'" + session_user.name + "\'")
        return resp(success("WSSB_CONFIG_RELOADED", "Global config has been reloaded successfully!"), Target.source())
    return resp(error("WSSB_ACCESS_DENIED", "You do not have permission to reload the global config!"), Target.source())

def view_reloadusers(session_user, request, quiet):
    """
    Reloads the user services module (including groups)
    """
    if session_user.has_permission("wssb.reload.users"):
        users.reload_all()
        sockets_to_close = []
        for socket in users.connected_sockets:
            if not users.socket_is_registered(socket):
                sockets_to_close.append(socket)
        logging.info("[SERVER] User services have been reloaded by \'" + session_user.name + "\'")
        if not quiet:
            print("[SERVER] User services have been reloaded by \'" + session_user.name + "\'")
        return resp(success("WSSB_USERS_RELOADED", "User services have been reloaded successfully!"), Target.source(), to_close=sockets_to_close)
    return resp(error("WSSB_ACCESS_DENIED", "You do not have permission to reload user services!"), Target.source())
