import threading
import messages


class MessageSender(threading.Thread):
    """
    The thread which does work on the message queue.
    """

    def __init__(self, stopper, queue, system_name, system_type, resource_identifier, sas_address):
        super(MessageSender, self).__init__()
        self._stopper = stopper
        self._queue = queue
        self._system_name = system_name
        # etc.

    def run(self):
        """
        Picks an item off the queue, calls message.serialize() on it, and sends it.
        If there's not been any messages sent for a while, then send a heartbeat.
        If the queue has been terminated (via _stopper), then stop.
        Maintains the connection - if the connection is down then reconnect using connect()
        """
        while not self._stopper.is_set():
            message = self._queue.get()  # TODO: Add a timeout to this, and send a heartbeat if no message for a second
            message.serialize()
            # send the message

            self._queue.task_done()

        self.disconnect()

    def connect(self):
        """
        Connects to the SAS. This involves sending an Init message.
        :return:
        """
        # Create the socket

        # Send the Init message
        init = messages.Init()
        # Add the info, or maybe put it in the constructor
        init.serialize()
        # send it

        # did it succeed?
        return True  # TODO: or false if failed

    def disconnect(self):
        pass
