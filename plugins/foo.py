"""
This file outlines an example WSSB plugin implementation
"""
from wssb import plugins
from wssb.events import Events
from wssb.events import EventHandler
from wssb import views
from wssb.views import Target
from wssb import config

class FooPlugin(plugins.WSSBPlugin):
    """
    Defines a test plugin used as an example of the plugin creation format
    """
    def __init__(self, quiet):
        """
        Constructor for FooPlugin
        """
        PLUGIN_NAME = "foo"
        PLUGIN_VERSION = "1.0.0"

        # Initialize the plugin superclass
        super().__init__(PLUGIN_NAME, PLUGIN_VERSION, quiet)

        # Setup plugin event handlers
        self.setup_handlers()

    def setup_handlers(self):
        """
        Simulates the creation and registration of simple event handlers
        """
        event_handlers = [
            EventHandler(Events.SERVER_START, self.on_start),
            EventHandler(Events.USER_AUTHENTICATED, self.on_auth)
        ]
        self.register_handlers(event_handlers)

    def on_start(self, context):
        """
        Example event handler for handling server startup
        """
        self.info("Plugin started successfully!")

        # Set-up a default configuration file arrangement
        default_config = {
            "section_1": {
                "option_1": "True",
                "option_2": "False",
            },
            "section_2": {
                "option_3": "3",
                "option_4": "test",
            },
        }

        self.config = config.Config(self.path + "foo.ini", default_config) # <--- Create the configuration object
        self.config.autogen() # <--- Autogenerate and load the configuration file

        self.add_route("foo", self.view_foo)

        return True # <--- This will allow the server to start

    def on_auth(self, context):
        """
        Example event handler for sending a welcome on authentication
        """
        user = context["user"]
        response = views.info("FOO_WELCOME", "Hello " + user.name + "! FOO welcomes YOU!")
        return self.resp(response, Target.source())

    def view_foo(self, context):
        """
        Example event handler for processing custom requests
        """
        request = context["request"] # <--- Gets packet dictionary object
        user = context["user"] # <--- Gets the user that sent the request

        if request["code"] == "foo": # <--- Custom request code
            # Set up a custom response packet
            response = {
                "type": "response", # <--- Should always use "response" type when responding to client
                "status": "success", # <--- Can be "success", "info", "warning", "error"
                "code": "FOO_EXAMPLE", # <--- Can be any value, should be unique to plugin to help client distinguish response
                "custom_component": "my custom value", # <--- You can add unlimited custom keys to response
            }

        return self.resp(response, Target.source()) # <--- Format and send the response packet to the user
