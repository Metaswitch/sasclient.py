from . import _client

class Message(object):
    """
    Message that can be sent to SAS
    """

    def serialize(self):
        """
        Convert the python message into a serialized string conforming to the VPED protocol. Should be overridden by
        subclasses.

        :return: Serialized version of the message
        """
        return str(self)  # Obviously not final implementation

    def send(self):
        """
        Add self to the message queue.
        """
        _client.send(self)


class Init(Message):
    """
    SAS initialization message. We don't expect users of this library to use this directly
    """
    pass


class TrailAssoc(Message):
    pass


class Event(Message):
    pass


class Marker(Message):
    pass


class Heartbeat(Message):
    pass
