from wssb import plugins
from wssb.events import Events
from wssb.events import EventHandler

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

        # Initialize the RDK3Plugin superclass
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

    def on_start(self):
        """
        Example event handler for handling server startup
        """
        self.info("Plugin started successfully!")

        return True # <--- This will allow the server to start
