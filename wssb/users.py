"""
This script handles actions relating to users, groups, and permissions
Help for all functionality of this script is available in the documentation
"""

from wssb import config

registered_users = [] # Stores all users registered in users.ini
registered_groups = [] # Stores all groups registered in groups.ini

connected = [] # Stores all currently connected users

class Group():
    """
    Defines a group object who has permissions and users
    """
    def __init__(self, name, permissions=[]):
        """
        Constructor for Group
        """
        self.name, self.permissions = name, permissions

    def has_permission(self, p):
        """
        Returns True if Group has the given permission
        """
        return any([perm_is_child(perm, p) for perm in self.permissions])

class User():
    """
    Defines a user object who has groups and permissions
    """
    def __init__(self, name, address="", groups=[], permissions=[]):
        """
        Constructor for User
        """
        self.name, self.address, self.groups, self.permissions = name, address, groups, permissions

    def has_permission(self, p):
        """
        Returns True if User has the given permission
        """
        if any([perm_is_child(perm, p) for perm in self.permissions]):
            return True
        for group in self.groups:
            if group.has_permission(p):
                return True
        return False

    def belongs_to(self, g):
        """
        Returns True if user belongs to the given group
        """
        return g in self.groups

def reload_all():
    """
    Reloads all users, groups, and permissions from file
    """
    global registered_users, registered_groups

    if config.users_config().reload() and config.groups_config().reload():
        for group in config.groups_config().sections():
            group_permissions = config.parse_safe_csv(config.groups_config()[group]["permissions"])
            registered_groups.append(Group(group, group_permissions))
        for user in config.users_config().sections():
            user_groups = config.parse_safe_csv(config.users_config()[user]["groups"])
            groups = []
            for group in user_groups:
                for group2 in registered_groups:
                    if group == group2.name:
                        groups.append(group2)
            user_permissions = config.parse_safe_csv(config.users_config()[user]["permissions"])
            user_address = config.users_config()[user]["socket_address"]
            registered_users.append(User(user, user_address, groups, user_permissions))
    else:
        return False

def find_user(user_name):
    """
    Finds a registered user by name
    Returns None if the user does not exist
    """
    global registered_users
    for user in registered_users:
        if user.name == user_name:
            return user
    return None

def perm_is_child(parent, child):
    """
    Returns true if the given child permission is a valid child of the given parents
    """
    return child.startswith(parent)

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
        config.users_config().set_section(user_name, { "permissions": "", "groups": "", "socket_address": "" })
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

def remove_user_from_group(user_name, group_name):
    """
    Removes a user from the specified group
    """
    if config.users_config().has_section(user_name):
        if config.groups_config().has_section(group_name):
            groups = config.parse_safe_csv(config.users_config()[user_name]["groups"])
            if group_name not in groups:
                return -3
            groups.remove(group_name)
            config.users_config().set(user_name, "groups", config.list_to_csv(groups))
            config.users_config().save()
            return True
        else:
            return -2
    else:
        return -1

def add_group_permissions(group_name, perms):
    """
    Adds a permission string to a group
    """
    if config.groups_config().has_section(group_name):
        old_perms = config.parse_safe_csv(config.groups_config()[group_name]["permissions"])
        new_perms = config.parse_safe_csv(perms)
        if all([perm not in old_perms for perm in new_perms]):
            config.groups_config().set(group_name, "permissions", config.append_csv(config.groups_config()[group_name]["permissions"], perms))
            config.groups_config().save()
            return True
        else:
            return -2
    else:
        return -1

def remove_group_permissions(group_name, perms):
    """
    Adds a permission string to a group
    """
    if config.groups_config().has_section(group_name):
        old_perms = config.parse_safe_csv(config.groups_config()[group_name]["permissions"])
        rem_perms = config.parse_safe_csv(perms)
        if all([perm in old_perms for perm in rem_perms]):
            for perm in rem_perms:
                old_perms.remove(perm)
            config.groups_config().set(group_name, "permissions", config.list_to_csv(old_perms))
            config.groups_config().save()
            return True
        else:
            return -2
    else:
        return -1

def add_user_permissions(user_name, perms):
    """
    Adds a permission string to a user
    """
    if config.users_config().has_section(user_name):
        old_perms = config.parse_safe_csv(config.users_config()[user_name]["permissions"])
        new_perms = config.parse_safe_csv(perms)
        if all([perm not in old_perms for perm in new_perms]):
            config.users_config().set(user_name, "permissions", config.append_csv(config.users_config()[user_name]["permissions"], perms))
            config.users_config().save()
            return True
        else:
            return -2
    else:
        return -1

def remove_user_permissions(user_name, perms):
    """
    Adds a permission string to a user
    """
    if config.users_config().has_section(user_name):
        old_perms = config.parse_safe_csv(config.users_config()[user_name]["permissions"])
        rem_perms = config.parse_safe_csv(perms)
        if all([perm in old_perms for perm in rem_perms]):
            for perm in rem_perms:
                old_perms.remove(perm)
            config.users_config().set(user_name, "permissions", config.list_to_csv(old_perms))
            config.users_config().save()
            return True
        else:
            return -2
    else:
        return -1
