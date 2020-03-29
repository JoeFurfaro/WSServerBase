"""
This script handles actions relating to users, groups, and permissions
Help for all functionality of this script is available in the documentation
"""

from wssb import config

def add_group(group_name):
    """
    Adds a new group to the global groups file if it does not exist
    """
    if not config.groups_config().has_section(group_name):
        config.groups_config().set_section(group_name, { "permissions": "" })
        config.groups_config().save()
        return True
    return False

def remove_group(group_name):
    """
    Removes a group from the global groups file if the group exists
    """
    if config.groups_config().has_section(group_name):
        config.groups_config().remove_section(group_name)
        config.groups_config().save()
        return True
    return False

def add_user(user_name):
    """
    Adds a new user to the global users file if it does not exist
    """
    if not config.users_config().has_section(user_name):
        config.users_config().set_section(user_name, { "permissions": "", "groups": "" })
        config.users_config().save()
        return True
    return False

def remove_user(user_name):
    """
    Removes a user from the global users file if the user exists
    """
    if config.users_config().has_section(user_name):
        config.users_config().remove_section(user_name)
        config.users_config().save()
        return True
    return False

def add_user_to_group(user_name, group_name):
    """
    Adds a user to the specified group
    """
    if config.users_config().has_section(user_name):
        if config.groups_config().has_section(group_name):
            groups = config.parse_safe_csv(config.users_config()[user_name]["groups"])
            if group_name in groups:
                return -3
            config.users_config().set(user_name, "groups", config.append_csv(config.users_config()[user_name]["groups"], group_name))
            config.users_config().save()
            return True
        else:
            return -2
    else:
        return -1
