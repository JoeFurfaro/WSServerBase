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
    SERVER_START = auto()
    SERVER_STOP = auto()

    USER_AUTH_ATTEMPT = auto()

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

    def is_a(type):
        """
        Return True if event type matches the type given
        """
        return self.type == type

    def __getitem__(self, key):
        """
        Get item definition for Event
        """
        if key in self.attributes:
            return self.attributes[key]
        return None
