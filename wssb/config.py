"""
This script handles generating, loading, and updating configuration values
Help for all functionality of this script is available in the documentation
"""

import configparser
import pathlib
import os
import logging

class Config():
    """
    Defines an object for storing configuration data
    """
    def __init__(self, path, required={}):
        """
        Constructor for Config
        """
        self.path, self.required = path, required

    def load(self):
        """
        Loads the config from file
        """
        return self.reload()

    def reload(self):
        """
        Reloads the config from file
        """
        if os.path.exists(self.path):
            self.config = configparser.ConfigParser()
            self.config.read(self.path)
            return True
        else:
            self.config = None
        return False

    def is_loaded(self):
        """
        Returns True if the configuration has been loaded successfully from file
        """
        return self.config != None

    def reset(self):
        """
        Resets the config file by deleting it and autogenerating a clean version using the autogen function
        """
        if os.path.exists(self.path):
            os.remove(self.path)

        return self.autogen()

    def __getitem__(self, key):
        """
        Get item definition for config
        """
        if key in self.config:
            return self.config[key]
        return None

    def autogen(self):
        """
        Autogenerates a configuration file in the path given
        Adds required default sections and options if they are not already defined in the config
        """
        if not os.path.exists(self.path):
            with open(self.path, "w") as config_file:
                config_file.write("; Default configuration creation in progress...")

        self.config = configparser.ConfigParser()
        self.config.read(self.path)

        for section in self.required.keys():
            if not self.config.has_section(section):
                self.config[section] = {}
            for key in self.required[section].keys():
                if not self.config.has_option(section, key):
                    self.config[section][key] = self.required[section][key]

        with open(self.path, "w") as config_file:
            self.config.write(config_file)
            return True

        return False

# Stores the global config in memory
global_conf = None
groups_conf = None

def load_global_config():
    """
    Loads and returns the global server configuration object
    """
    global global_conf
    env_root = str(pathlib.Path(__file__).parent.parent.absolute())
    fields = {
        "GENERAL": {
            "server_address": "localhost",
            "server_port": "8765" ,
        },
    }
    global_conf = Config(env_root + "/server.ini", required=fields)
    global_conf.autogen()
    return global_conf.load()

def load_groups_config():
    """
    Loads and returns the global server groups configuration object
    """
    global groups_conf
    env_root = str(pathlib.Path(__file__).parent.parent.absolute())
    global_conf = Config(env_root + "/groups.ini")
    global_conf.autogen()
    return global_conf.load()

def global_config():
    """
    Loads the global configuration
    """
    global global_conf
    return global_conf
