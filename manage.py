"""
This script allows local network administrator to configure, test and manage RDK3Server
Help for all functionality of this script is available in the documentation
"""

import argparse
import logging

from rdk3 import config
from rdk3 import files
from rdk3 import core

logging.basicConfig(filename="server.log", level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

parser = argparse.ArgumentParser()

parser.add_argument("action", help="The RDK3Server action to run", choices=["runserver", "resetlog", "resetcfg"])
parser.add_argument("-p", "--port", help="Specifies the port of the server (overrides config)", type=int)
parser.add_argument("-q", "--quiet", help="Silences program output", action="store_true")

args = parser.parse_args()

"""
POSSIBLE ACTIONS:
    - runserver
    - resetlog
    - resetcfg
"""

if args.action == "runserver":
    core.start(args.quiet)

elif args.action == "resetlog":
    files.reset_log_file(args.quiet)

elif args.action == "resetcfg":
    config.reset(args.quiet)

#config.config_autogen(args.quiet)
