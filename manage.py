"""
This script allows local network administrator to configure, test and manage WebSocketServer
Help for all functionality of this script is available in the documentation
"""

import argparse
import logging
import sys

from wssb import config
from wssb import files
from wssb import core
from wssb import users

logging.basicConfig(filename="server.log", level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

parser = argparse.ArgumentParser()

action_choices = [
    "runserver",
    "resetlog",
    "resetcfg",
    "groups",
    "users",
]

parser.add_argument("action", help="The WebSocketServer manager action to run", choices=action_choices)

parser.add_argument("-q", "--quiet", help="Silences program output", action="store_true")
parser.add_argument("-a", "--add", help="Object adding mode", action="store_true")
parser.add_argument("-r", "--remove", help="Object removing mode", action="store_true")
parser.add_argument("-l", "--list", help="List object mode", action="store_true")
parser.add_argument("-g", "--group", help="Identifies the name of a group", nargs=1)
parser.add_argument("-u", "--user", help="Identifies the name of a user", nargs=1)
parser.add_argument("-p", "--perms", help="Identifies a permissions string", nargs=1)

args = parser.parse_args()

if args.action == "runserver":
    core.start(args.quiet)

elif args.action == "resetlog":
    files.reset_log_file(args.quiet)

elif args.action == "resetcfg":
    config.load_global_config()
    if config.global_config().reset():
        if not args.quiet:
            print("[SERVER] Server configuration file reset successfully")
    else:
        if not args.quiet:
            print("[SERVER] Failed to reset server configuration file")

elif args.action == "groups":

    config.load_groups_config()
    config.load_users_config()

    if args.list and not args.quiet:
        for group in config.groups_config().sections():
            print(group, end=" ")
        print()

    elif args.group == None:
        if not args.quiet:
            print("[SERVER] Group name not specified")

    elif args.add:
        group_name = args.group[0].strip()
        if not config.validate(group_name) and not args.quiet:
            print("[SERVER] You cannot use any of \" , \' \\n in the group name")
            sys.exit()

        if args.user != None:
            result = users.add_user_to_group(args.user[0], group_name)
            if result == True:
                if not args.quiet:
                    print("[SERVER] User '" + args.user[0] + "' added to group '" + group_name + "' successfully")
            elif result == -1:
                if not args.quiet:
                    print("[SERVER] User '" + args.user[0] + "' does not exist")
            elif result == -2:
                if not args.quiet:
                    print("[SERVER] Group '" + group_name + "' does not exist")
            elif result == -3:
                if not args.quiet:
                    print("[SERVER] User '" + args.user[0] + "' is already in group '" + group_name + "'")
        elif args.perms != None:
            # Add permissions to group
            pass
        else:
            # Add group
            if users.add_group(group_name):
                if not args.quiet:
                    print("[SERVER] Group '" + group_name + "' added successfully")
            else:
                if not args.quiet:
                    print("[SERVER] Group '" + group_name + "' already exists")

    elif args.remove:
        group_name = args.group[0]

        if args.user != None:
            # Remove user from group
            pass
        elif args.perms != None:
            # Remove permissions from group
            pass
        else:
            # Remove group
            if users.remove_group(group_name):
                if not args.quiet:
                    print("[SERVER] Group '" + group_name + "' removed successfully")
            else:
                if not args.quiet:
                    print("[SERVER] Group '" + group_name + "' does not exist")

    else:
        groups_config = config.groups_config()
        if groups_config.has_section(args.group[0]) and not args.quiet:
            print("\tPermissions(s): " + groups_config[args.group[0]]["permissions"])
        else:
            if not args.quiet:
                print("[SERVER] Group '" + args.group[0] + "' does not exist")

elif args.action == "users":

    config.load_groups_config()
    config.load_users_config()

    if args.list and not args.quiet:
        for user in config.users_config().sections():
            print(user, end=" ")
        print()

    elif args.user == None:
        if not args.quiet:
            print("[SERVER] User name not specified")

    elif args.add:

        user_name = args.user[0].strip()
        if not config.validate(user_name) and not args.quiet:
            print("[SERVER] You cannot use any of \" , \' \\n in the user name")
            sys.exit()

        if args.perms != None:
            # Add permission to user
            pass
        else:
            # Add new user
            if users.add_user(user_name):
                if not args.quiet:
                    print("[SERVER] User '" + user_name + "' added successfully")
            else:
                if not args.quiet:
                    print("[SERVER] User '" + user_name + "' already exists")

    elif args.remove:

        user_name = args.user[0]

        if args.perms != None:
            # Add permission to user
            pass
        else:
            # Add new user
            if users.remove_user(user_name):
                if not args.quiet:
                    print("[SERVER] User '" + user_name + "' removed successfully")
            else:
                if not args.quiet:
                    print("[SERVER] User '" + user_name + "' does not exist")

    else:
        users_config = config.users_config()
        if users_config.has_section(args.user[0]) and not args.quiet:
            print("\tGroup(s): " + users_config[args.user[0]]["groups"])
            print("\tPermissions(s): " + users_config[args.user[0]]["permissions"])
        else:
            if not args.quiet:
                print("[SERVER] User '" + args.user[0] + "' does not exist")
