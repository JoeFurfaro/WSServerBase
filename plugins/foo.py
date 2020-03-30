"""
This file outlines an example WSSB plugin implementation
"""

from wssb import plugins
from wssb.events import Events
from wssb.events import EventHandler
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
        self.config.autogen() # <---- Autogenerate and load the configuration file

        return True # <--- This will allow the server to start
