"""
This script handles generating, loading, and updating configuration values
Help for all functionality of this script is available in the documentation
"""

import configparser
import pathlib
import os
import logging

cfg = None

def get(section, option):
    global cfg
    
    if cfg == None:
        return None
    if cfg.has_option(section, option):
        return cfg[section][option]
    else:
        return None

def load(quiet):
    """
    Loads the config file into default cfg variable
    """
    global cfg

    env_root = str(pathlib.Path(__file__).parent.parent.absolute())

    if os.path.exists(env_root + "/rdk3.ini"):
        cfg = configparser.ConfigParser()
        cfg.read(env_root + "/rdk3.ini")

        logging.info("Loaded configuration file successfully")
        if not quiet:
            print("Loaded configuration file successfully")
    else:
        logging.error("Failed to load config")
        if not quiet:
            print("Failed to load config")

def autogen(quiet):
    """
    Autogenerates the RDK3Server configuration file "rdk3.ini" in the environment root
    Adds required default sections and options if they are not already defined in the config
    """
    env_root = str(pathlib.Path(__file__).parent.parent.absolute())

    if not os.path.exists(env_root + "/rdk3.ini"):
        with open(env_root + "/rdk3.ini", "w") as config_file:
            config_file.write("; Default RDK3Server configuration creation in progress...")
            logging.info("Automatically generated default configuration file")
            if not quiet:
                print("Automatically generated default configuration file")

    config = configparser.ConfigParser()
    config.read(env_root + "/rdk3.ini")

    # [GENERAL SECTION]
    if not config.has_section("GENERAL"):
        config["GENERAL"] = {}

    # server_address option
    if not config.has_option("GENERAL", "server_address"):
        config["GENERAL"]["server_address"] = "localhost"

    # server_port option
    if not config.has_option("GENERAL", "server_port"):
        config["GENERAL"]["server_port"] = "8765"

    with open(env_root + "/rdk3.ini", "w") as config_file:
        config.write(config_file)
        load(False)
        return True

    return False

def reset(quiet):
    """
    Resets the config file by deleting it and autogenerating a clean version using the autogen function
    """
    env_root = str(pathlib.Path(__file__).parent.parent.absolute())
    if os.path.exists(env_root + "/rdk3.ini"):
        os.remove(env_root + "/rdk3.ini")
    if autogen(True):
        logging.info("Config reset successfully")
        if not quiet:
            print("Config reset successfully")
            return True
    print("Could not reset config file")
    return False
