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
        self.config = None

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

    def remove_section(self, section):
        """
        Removes a config section
        """
        self.config.remove_section(section)

    def set_section(self, section, value):
        """
        Sets the value of a config section
        """
        self.config[section] = value

    def set(self, section, option, value):
        """
        Sets the value of a config option
        """
        if not self.has_section(section):
            self.config[section] = {}
        self.config[section][option] = value

    def has_section(self, section):
        """
        Returns True if section exists in config
        """
        return self.config.has_section(section)

    def has_option(self, section, option):
        """
        Returns True if option exists in config
        """
        return self.config.has_option(section, option)

    def sections(self):
        """
        Returns a list of config sections
        """
        return self.config.sections()

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

    def save(self):
        """
        Writes the configuration data to file
        """
        with open(self.path, "w") as config_file:
            self.config.write(config_file)
            return True
        return False

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
users_conf = None

def load_global_config():
    """
    Loads the global server configuration object
    """
    global global_conf
    env_root = str(pathlib.Path(__file__).parent.parent.absolute())
    fields = {
        "GENERAL": {
            "server_address": "localhost",
            "server_port": "8765",
        },
    }
    global_conf = Config(env_root + "/server.ini", required=fields)
    global_conf.autogen()
    return global_conf.load()

def load_groups_config():
    """
    Loads the global server groups configuration object
    """
    global groups_conf
    env_root = str(pathlib.Path(__file__).parent.parent.absolute())
    groups_conf = Config(env_root + "/groups.ini")
    groups_conf.autogen()
    return groups_conf.load()

def load_users_config():
    """
    Loads the global server users configuration object
    """
    global users_conf
    env_root = str(pathlib.Path(__file__).parent.parent.absolute())
    users_conf = Config(env_root + "/users.ini")
    users_conf.autogen()
    return users_conf.load()

def global_config():
    """
    Loads the global configuration
    """
    global global_conf
    return global_conf

def groups_config():
    """
    Loads the global groups configuration
    """
    global groups_conf
    return groups_conf

def users_config():
    """
    Loads the global users configuration
    """
    global users_conf
    return users_conf

def parse_safe_csv(s):
    """
    Parses a list of comma separated values that does not contain additional commas
    """
    return s.split(",")

def list_to_csv(l):
    """
    Joins a list of strings by commas
    """
    return ",".join(l)

def validate(s):
    """
    Validates a string for config insertion
    """
    return not ("," in s or "\"" in s or "\'" in s or "\n" in s or " " in s or s[0] == "%")

def validate_permission_string(s):
    """
    Validates a permission string for config insertion
    """
    return not ("\"" in s or "\'" in s or "\n" in s or " " in s)

def append_csv(l, s):
    """
    Appends a single string to a comma separated string
    """
    if l == "":
        return s
    return l + "," + s
