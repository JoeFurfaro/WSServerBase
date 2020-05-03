"""
This plugin implements required passwords for users and groups
"""
from wssb import plugins
from wssb.events import Events
from wssb.events import EventHandler
from wssb import config
from wssb import users

class PasswordsPlugin(plugins.WSSBPlugin):

    def __init__(self, quiet):

        PLUGIN_NAME = "passwords"
        PLUGIN_VERSION = "1.0.0"
        PLUGIN_AUTHOR = "Joe Furfaro"
        DEPENDENCIES = []

        super().__init__(PLUGIN_NAME, PLUGIN_VERSION, PLUGIN_AUTHOR, DEPENDENCIES, quiet)

        self.setup_handlers()

    def setup_handlers(self):
        event_handlers = [
            EventHandler(Events.SERVER_START, self.on_start),
            EventHandler(Events.USER_AUTH_ATTEMPT, self.on_auth_attempt)
        ]
        self.register_handlers(event_handlers)

    def process_command(self, args):
        self.on_start(None)

        if args[0] == "enable":
            if len(args) == 2:
                if users.group_exists(args[1]):
                    self.groups_config.set_section(args[1], {})
                    self.groups_config.save()
                    self.info("Passwords enabled for group \'" + args[1] + "\'")
                else:
                    self.error("Could not find group \'" + args[1] + "\'")
            else:
                self.error("Invalid syntax")
        elif args[0] == "disable":
            if len(args) == 2:
                if users.group_exists(args[1]):
                    if self.groups_config.has_section(args[1]):
                        self.groups_config.remove_section(args[1])
                        self.groups_config.save()
                    self.info("Passwords disabled for group \'" + args[1] + "\'")
                else:
                    self.error("Could not find group \'" + args[1] + "\'")
            else:
                self.error("Invalid syntax")
        elif args[0] == "set":
            if len(args) == 3:
                if users.exists(args[1]):
                    self.passwords_config.set(args[1], "password", args[2])
                    self.passwords_config.save()
                    self.info("Password set successully for user \'" + args[1] + "\'")
                else:
                    self.error("Could not find user \'" + args[1] + "\'")
            else:
                self.error("Invalid syntax")
        elif args[0] == "reset":
            self.groups_config.reset()
            self.groups_config.save()
            self.passwords_config.reset()
            self.passwords_config.save()
            self.info("All plugin data reset successully")
        else:
            self.error("Command not found")

    def on_start(self, context):
        self.groups_config = config.Config(self.path + "groups_enabled.ini", {})
        self.groups_config.autogen()

        self.passwords_config = config.Config(self.path + "passwords.ini", {})
        self.passwords_config.autogen()

        if context != None:
            self.info("Passwords loaded successully")

        return True

    def on_auth_attempt(self, context):
        user = context["user"]
        request = context["request"]

        # Allow valid sessions without authenticating password
        sessions_instance = plugins.find("sessions")
        if sessions_instance != None:
            return "session_id" in request and sessions_instance.is_valid(request["session_id"])

        needs_auth = False
        for group in user.groups:
            if self.groups_config.has_section(group.name):
                needs_auth = True
        if needs_auth:
            if self.passwords_config.has_section(user.name):
                if "password" in request:
                    if request["password"] == self.passwords_config[user.name]["password"]:
                        return True
            return False

        return True
