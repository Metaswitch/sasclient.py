import threading
import socket
import time
import Queue
import logging

from metaswitch.sasclient import messages

MIN_RECONNECT_WAIT_TIME = 100
MAX_RECONNECT_WAIT_TIME = 5000


# TODO logging
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
        while not self._stopper.is_set():
            # Try to get a message off of the queue. After a second, give up and move through the loop.
            try:
                message = self._queue.get(True, 1)
            except Queue.Empty:
                # No message for a second, send a heartbeat
                logging.debug("Sending heartbeat")
                self._sas_sock.sendall(messages.Heartbeat().serialize())
            # TODO: other exceptions?

            # Send the message
            try:
                self._sas_sock.sendall(message.serialize())
                logging.debug("Trying to send message:\n" + str(message.serialize()))
            except Exception as e:
                # TODO: add exception types. This could fail because the socket isn't open.
                # Failed to send message. Reconnect, put the message back on the queue, and try again.
                logging.debug("Failed to send message. Error:\n" + str(e))
                self.reconnect()
                self._queue.put(message)
            finally:
                logging.debug("Successfully sent message")
                self._queue.task_done()

        self.disconnect()

    def connect(self):
        """
        Connects to the SAS. This involves sending an Init message, which is sent immediately and bypasses the queue.
        """
        self._sas_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect. This is blocking indefinitely, but this is fine because without a connection there is nothing else to
        # do.
        logging.debug("Connecting to: " + str(self._sas_address) + ":" + str(self._sas_port))
        self._sas_sock.connect((self._sas_address, self._sas_port))
        # TODO: catch this exception somewhere.
        # except IOError as e:
        #     print "An I/O error occurred whilst opening socket to {0} on port {1}. Error is: {2}".format(self._sas_address, self._sas_port, e)
        # except (socket.herror, socket.gaierror) as e:
        #     print "An address error occurred whilst opening socket to {0} on port {1}. Error is: {2}".format(self._sas_address, self._sas_port, e)
        # else

        # Send the Init message, bypassing the queue.
        logging.debug("Sending init message")
        init = messages.Init(self._system_name, self._system_type, self._resource_identifier)
        self._sas_sock.sendall(init.serialize())
        # TODO: catch this exception somewhere

        # Connection is successful. Reset the time to wait between reconnects.
        logging.debug("Successfully connected")
        self._reconnect_wait = MIN_RECONNECT_WAIT_TIME

    def disconnect(self):
        logging.debug("Disconnecting")
        self._sas_sock.shutdown(socket.SHUT_RDWR)
        self._sas_sock.close()
        # TODO: catch this exception

    def reconnect(self):
        # If our connection is being rejected, don't spam the SAS with attempts. Use exponential back-off.
        reconnect_wait = self._reconnect_wait
        self._reconnect_wait = min(reconnect_wait * 2, MAX_RECONNECT_WAIT_TIME)
        logging.debug("Sleeping for " + str(reconnect_wait) + " seconds before reconnecting")
        time.sleep(reconnect_wait)

        self.disconnect()
        self.connect()
        # TODO: catch these exceptions
