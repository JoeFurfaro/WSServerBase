"""
This script handles the loading, processing, and managing of installed server plugins
Help for all functionality of this script is available in the documentation
"""

import logging
import pathlib
import os
import importlib.util
import inspect

import pathlib
import os

from wssb import events

class WSSBPlugin():
    """
    Defines an abstract plugin that can be extended to create custom WSSBPlugins
    """
    def __init__(self, name, version_str, quiet):
        """
        Constructor for WSSBPlugin
        Autogenerates plugin data folder
        """
        self.name, self.version_str, self.quiet = name.lower(), version_str, quiet
        self.handlers = []
        self.routes = {}

        env_root = str(pathlib.Path(__file__).parent.parent.absolute())
        if not os.path.exists(env_root + "/plugins/" + name.lower()):
            os.mkdir(env_root + "/plugins/" + name.lower())

        self.path = env_root + "/plugins/" + name.lower() + "/"

    def __str__(self):
        """
        String conversion for WSSBPlugin
        """
        return self.name + " version " + self.version_str

    def get_events(self, type):
        """
        Returns a list of register events matching the given type (should be an Events enum object)
        """
        return [e for e in self.events if e.type == type]

    def add_route(self, request_name, view):
        """
        Adds a specific view that a request should be routed to
        Request names must be unique per plugin
        """
        self.routes[request_name] = view

    def process_request(self, request, user):
        """
        Processes a command by routing it to the correct view
        """
        if request["code"] in self.routes:
            return self.routes[request["code"]]({"request": request, "user": user})
        return None

    def qprint(self, s):
        """
        Prints a message if quiet mode is disabled
        """
        if not self.quiet:
            print(s)

    def info(self, s):
        """
        Logs an informative plugin message
        """
        logging.info("[" + self.name + "] " + s)
        self.qprint("[" + self.name + "] " + s)

    def warning(self, s):
        """
        Logs an warning plugin message
        """
        logging.warning("[" + self.name + "] " + s)
        self.qprint("[" + self.name + "] " + s)

    def warning(self, s):
        """
        Logs an error plugin message
        """
        logging.warning("[" + self.name + "] " + s)
        self.qprint("[" + self.name + "] " + s)

    def register_handler(self, handler):
        """
        Registers an event handler
        """
        self.handlers.append(handler)

    def register_handlers(self, handlers):
        """
        Registers a group of event handlers
        """
        for handler in handlers:
            self.register_handler(handler)

    def resp(self, response, target):
        return { "response": response, "target": target }

plugins = []

def trigger_conditional_handlers(type, context):
    """
    Triggers all plugin conditional event handlers that match the type given
    """
    global plugins

    results = []

    for plugin in plugins:
        for handler in plugin.handlers:
            if handler.type == type:
                results.append(handler.action(context))

    return all(results)

def trigger_handlers(type, context):
    """
    Triggers all non-conditional plugin event handlers that match the type given
    """
    global plugins

    responses = []
    for plugin in plugins:
        for handler in plugin.handlers:
            if handler.type == type:
                response = handler.action(context)
                if response != None:
                    responses.append(response)

    return responses

def handle(request, user):
    """
    Attempts to route a request to all custom plugins
    """
    responses = []
    for plugin in plugins:
        response = plugin.process_request(request, user)
        if response != None:
            responses.append(response)
    return responses

def get():
    """
    Returns a list of all loaded plugins
    """
    global plugins
    return plugins

def load_all(quiet):
    """
    Attempts to load all RDK3Plugins available in the plugins directory
    """
    global plugins
    plugins_folder = str(pathlib.Path(__file__).parent.parent.absolute()) + "/plugins/"
    for file_name in os.listdir(plugins_folder):
        if file_name.endswith(".py"):
            plugin_path = plugins_folder + file_name
            spec = importlib.util.spec_from_file_location("wssb.plugins", plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            plugin_class = None
            for name, cls in inspect.getmembers(module):
                if inspect.isclass(cls) and issubclass(cls, WSSBPlugin):
                    plugins.append(cls(quiet))

def autogen_folder(quiet):
    """
    Autogenerates the plugins folder if it does not exist
    """
    env_root = str(pathlib.Path(__file__).parent.parent.absolute())
    if not os.path.exists(env_root + "/plugins"):
        os.mkdir(env_root + "/plugins")
        logging.info("[SERVER] Autogenerated plugins folder")
        if not quiet:
            print("[SERVER] Autogenerated plugins folder")
        return True
    return False
