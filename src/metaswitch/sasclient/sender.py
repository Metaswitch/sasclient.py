import threading
import socket
import time
import Queue
import logging

from metaswitch.sasclient import messages

MIN_RECONNECT_WAIT_TIME = 0.1
MAX_RECONNECT_WAIT_TIME = 5

logger = logging.getLogger(__name__)


# TODO some exceptions
# TODO may want to have the normal connect time out
class MessageSender(threading.Thread):
    """
    The thread which does work on the message queue.
    """

    def __init__(self, stopper, queue, system_name, system_type, resource_identifier, sas_address, sas_port):
        super(MessageSender, self).__init__()

        # Objects that the thread runs on
        self._stopper = stopper
        self._queue = queue

        # Information needed for Init message
        self._system_name = system_name
        self._system_type = system_type
        self._resource_identifier = resource_identifier

        # Connection information
        self._sas_address = sas_address
        self._sas_port = sas_port
        self._sas_sock = None
        self._reconnect_wait = MIN_RECONNECT_WAIT_TIME

    def run(self):
        """
        Picks an item off the queue, calls message.serialize() on it, and sends it.
        If there's not been any messages sent for a while, then send a heartbeat.
        If the queue has been terminated (via _stopper), then stop.
        Maintains the connection - if the connection is down then reconnect using connect()
        """
        message = None
        while not self._stopper.is_set():
            # If we're not retrying a message, try to get a message off of the queue. After a second, give up and move
            # through the loop.
            if message is None:
                try:
                    message = self._queue.get(True, 1)
                except Queue.Empty:
                    # No message for a second, send a heartbeat
                    logger.debug("SAS: Sending heartbeat")
                    self._sas_sock.sendall(messages.Heartbeat().serialize())
                # TODO: other exceptions?

            # Send the message
            if message is not None:
                try:
                    self._sas_sock.sendall(message.serialize())
                    logger.debug("SAS: Sending message of type " + str(message.msg_type) + ":\n" +
                                  str(message.serialize()))
                except Exception as e:
                    # TODO: add exception types. This could fail because the socket isn't open.
                    # Failed to send message. Reconnect and try again next iteration with the same message.
                    logger.debug("SAS: Failed to send message. Error:\n" + str(e))
                    self.reconnect()
                else:
                    self._queue.task_done()
                    message = None

        self.disconnect()

    def connect(self):
        """
        Connects to the SAS. This involves sending an Init message, which is sent immediately and bypasses the queue.
        """
        self._sas_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect. This is blocking indefinitely, but this is fine because without a connection there is nothing else to
        # do. If this fails, then we'll notice when we try to send the heartbeat, which will prompt the reconnect.
        try:
            logger.debug("SAS: Connecting to: " + str(self._sas_address) + ":" + str(self._sas_port))
            self._sas_sock.connect((self._sas_address, self._sas_port))
        except IOError as e:
            logger.error("SAS: An I/O error occurred whilst opening socket to {0} on port {1}. Error is: {2}".format(self._sas_address, self._sas_port, str(e)))
        except (socket.herror, socket.gaierror) as e:
            logger.error("SAS: An address error occurred whilst opening socket to {0} on port {1}. Error is: {2}".format(self._sas_address, self._sas_port, str(e)))
        else:

            # Send the Init message, bypassing the queue.
            init = messages.Init(self._system_name, self._system_type, self._resource_identifier)
            self._sas_sock.sendall(init.serialize())
            # TODO: catch this exception somewhere

            # Connection is successful. Reset the time to wait between reconnects.
            self._reconnect_wait = MIN_RECONNECT_WAIT_TIME

    def disconnect(self):
        logger.debug("SAS: Disconnecting")
        self._sas_sock.shutdown(socket.SHUT_RDWR)
        self._sas_sock.close()
        # TODO: catch this exception

    def reconnect(self):
        # If our connection is being rejected, don't spam the SAS with attempts. Use exponential back-off.
        reconnect_wait = self._reconnect_wait
        self._reconnect_wait = min(reconnect_wait * 2, MAX_RECONNECT_WAIT_TIME)
        time.sleep(reconnect_wait)

        self.disconnect()
        self.connect()
        # TODO: catch these exceptions
