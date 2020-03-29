"""
This script handles the loading, processing, and managing of installed server plugins
Help for all functionality of this script is available in the documentation
"""

import logging
import pathlib
import os
import importlib.util
import inspect

from rdk3 import events

def autogen_folder(quiet):
    """
    Autogenerates the plugins folder if it does not exist
    """
    env_root = str(pathlib.Path(__file__).parent.parent.absolute())
    if not os.path.exists(env_root + "/plugins"):
        os.mkdir(env_root + "/plugins")
        logging.info("Autogenerated plugins folder")
        if not quiet:
            print("Autogenerated plugins folder")
        return True
    return False

class RDK3Plugin():
    """
    Defines an abstract plugin that can be extended to create custom RDK3Server plugins
    """
    def __init__(self, name, version_str, quiet):
        """
        Constructor for RDK3Plugin
        """
        self.name, self.version_str, self.quiet = name, version_str, quiet
        self.handlers = []

    def __str__(self):
        """
        String conversion for RDK3Plugin
        """
        return self.name + " version " + self.version_str

    def get_events(type):
        """
        Returns a list of register events matching the given type (should be an Events enum object)
        """
        return [e for e in self.events if e.type == type]

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

plugins = []

def trigger_handlers(type):
    """
    Triggers all plugin event handlers that match the type given
    """
    global plugins
    for plugin in plugins:
        for handler in plugin.handlers:
            if handler.type == type:
                handler.action()

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
            spec = importlib.util.spec_from_file_location("rdk3.plugins", plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            plugin_class = None
            for name, cls in inspect.getmembers(module):
                if inspect.isclass(cls) and issubclass(cls, RDK3Plugin):
                    plugins.append(cls(quiet))