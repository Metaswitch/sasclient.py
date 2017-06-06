# @file sender.py
# Copyright (C) 2015  Metaswitch Networks Ltd

import threading
import socket
import Queue
import logging
import traceback

from metaswitch.sasclient import messages

MIN_RECONNECT_WAIT_TIME = 0.1
MAX_RECONNECT_WAIT_TIME = 5
CONNECTION_TIMEOUT = 10

logger = logging.getLogger(__name__)


class MessageSender(threading.Thread):
    """
    The thread which does work on the message queue.
    """

    def __init__(
            self,
            stopper,
            queue,
            system_name,
            system_type,
            resource_identifier,
            sas_address,
            sas_port):
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
        self._connected = False

    def run(self):
        """
        Picks an item off the queue, calls message.serialize() on it, and sends it.
        If there's not been any messages sent for a while, then send a heartbeat.
        If the queue has been terminated (via _stopper), then stop.
        Maintains the connection - if the connection is down then reconnect using connect()
        """
        try:
            while not self._stopper.is_set():
                if not self._connected:
                    # Try to reconnect and have another go at the loop.
                    self.reconnect()
                    continue

                # Try to get a message off of the queue.  If there's nothing there after a second,
                # send a heartbeat.
                try:
                    message = self._queue.get(True, 1)
                    self._queue.task_done()
                except Queue.Empty:
                    message = messages.Heartbeat()

                # Send the message.  If we fail, we'll want to reconnect.
                if not self.send_message(message):
                    logger.debug("Failed to send a message, flag that we need to reconnect")
                    self._connected = False

            self.disconnect()
            self._connected = False

        except Exception as e:
            # Ensure that we record any unexpected exceptions in the logs.  We also print out
            # the error, in order to still produce diagnosable output when we're hitting
            # exceptions in the logging library.
            details = traceback.format_exc()
            error = (
                "ERROR - Hit exception in SAS sender thread!  SAS logs will no longer be made.\n{}"
            ).format(details)
            print(error)
            logger.error(error)
            raise e

    def connect(self):
        """
        Connects to the SAS. This involves sending an Init message, which is sent immediately and
        bypasses the queue.
        If this fails, immediately call reconnect()
        """
        # Connect. This has a long timeout, but this is fine because without a connection there is
        # nothing else to do. If this fails, then we'll notice when we try to send the heartbeat,
        # which will prompt the reconnect.
        try:
            logger.info("Connecting to: %s:%s", self._sas_address, self._sas_port)
            self._sas_sock = socket.create_connection((self._sas_address, self._sas_port),
                                                      CONNECTION_TIMEOUT)
        except IOError as e:
            logger.error(
                "An I/O error occurred whilst opening socket to %s on port %s: %s",
                self._sas_address,
                self._sas_port,
                str(e))
        else:
            # Send the Init message, bypassing the queue.
            init = messages.Init(self._system_name, self._system_type, self._resource_identifier)
            if self.send_message(init):
                # Connection is successful. Reset the time to wait between reconnects.
                logger.debug("Successfully connected")
                self._reconnect_wait = MIN_RECONNECT_WAIT_TIME
                self._connected = True

    def disconnect(self):
        logger.debug("Disconnecting")
        # It's possible that the socket doesn't even exist yet, so we have nothing to do.
        if self._sas_sock is None:
            return
        try:
            self._sas_sock.shutdown(socket.SHUT_RDWR)
            self._sas_sock.close()
        except Exception as e:
            # Ignore errors that occur while trying to close a socket.  If the
            # connection has gone away, we don't have anything more to do.
            logger.debug("Hit error closing socket - ignore: %s", str(e))

    def send_message(self, message):
        """
        Sends a message on the socket
        :param message: Message to send
        :return: boolean success
        """
        heartbeat = isinstance(message, messages.Heartbeat)

        if not heartbeat:
            logger.debug("Sending message:\n%s", str(message))

        msg_array = message.serialize()
        try:
            self._sas_sock.sendall(msg_array)

            if not heartbeat:
                logger.debug("Successfully sent message")

            return True
        except IOError as e:
            logger.error("An I/O error occurred whilst sending message to %s on port %s: %s",
                         self._sas_address, self._sas_port, str(e))
            return False
        except socket.timeout as e:
            logger.error("Socket timeout occurred whilst sending message to %s on port %s: %s",
                         self._sas_address, self._sas_port, str(e))
            return False

    def reconnect(self):
        logger.debug("Attempting to reconnect.")
        self.disconnect()

        # If our connection is being rejected, don't spam the SAS with attempts. Use exponential
        # back-off.
        reconnect_wait = self._reconnect_wait
        self._reconnect_wait = min(reconnect_wait * 2, MAX_RECONNECT_WAIT_TIME)

        # Interruptible sleep. Returns False if it reaches the timeout, and True if it was
        # interrupted.
        if not self._stopper.wait(reconnect_wait):
            self.connect()
