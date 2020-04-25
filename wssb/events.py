"""
This script handles the processing of events on the server for all plugins and server core
Help for all functionality of this script is available in the documentation
"""

from enum import Enum, auto

class Events(Enum):
    """
    Defines an enum listing all types of valid events on the server
    These event types can be used within plugins and within core
    """
    ### CONDITIONAL HANDLERS ###
    SERVER_START = auto()
    
    USER_AUTH_ATTEMPT = auto()
    USER_DISCONNECT = auto()

    ### RESPONSE-BASED HANDLERS ###
    USER_AUTHENTICATED = auto()

class EventHandler():
    """
    Defines an event handler that can be registered to the server event list
    """
    def __init__(self, type, action):
        """
        Constructor for Event
        Type is an Events enum object
        """
        self.type, self.action, self.attributes = type, action, {}

    def __str__(self):
        """
        String conversion for Event
        """
        return "Event of type " + self.type.name

    def __getitem__(self, key):
        """
        Get item definition for Event
        """
        if key in self.attributes:
            return self.attributes[key]
        return None
