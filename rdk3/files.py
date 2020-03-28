"""
This script handles general File I/O actions used in the environment
Help for all functionality of this script is available in the documentation
"""

import pathlib
import os
import logging

def reset_log_file(quiet):
    """
    Resets the log file by deleting it
    """
    env_root = str(pathlib.Path(__file__).parent.parent.absolute())
    if os.path.exists(env_root + "/server.log"):
        os.remove(env_root + "/server.log")
        logging.info("Log file reset successfully")
        if not quiet:
            print("Log file reset successfully")
        return True
    return False
