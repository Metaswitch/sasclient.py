# @file sender.py
# Copyright (C) 2015  Metaswitch Networks Ltd

import threading
import socket
import time
import Queue
import logging

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
        # Connecting shouldn't take more than 10 seconds.
        socket.setdefaulttimeout(CONNECTION_TIMEOUT)
        self._connected = False

    def run(self):
        """
        Picks an item off the queue, calls message.serialize() on it, and sends it.
        If there's not been any messages sent for a while, then send a heartbeat.
        If the queue has been terminated (via _stopper), then stop.
        Maintains the connection - if the connection is down then reconnect using connect()
        """
        message = None
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
                self._connected = False

        self.disconnect()

    def connect(self):
        """
        Connects to the SAS. This involves sending an Init message, which is sent immediately and
        bypasses the queue.
        If this fails, immediately call reconnect()
        """
        self._sas_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect. This is blocking indefinitely, but this is fine because without a connection
        # there is nothing else to do. If this fails, then we'll notice when we try to send the
        # heartbeat, which will prompt the reconnect.
        try:
            logger.info("Connecting to: %s:%s", self._sas_address, self._sas_port)
            self._sas_sock.connect((self._sas_address, self._sas_port))
        except IOError as e:
            logger.error(
                "An I/O error occurred whilst opening socket to %s on port %s. Error is: %s",
                self._sas_address,
                self._sas_port,
                str(e))
        except (socket.herror, socket.gaierror) as e:
            logger.error(
                "An address error occurred whilst opening socket to %s on port %s. Error is: %s",
                self._sas_address,
                self._sas_port,
                str(e))
        else:
            # Send the Init message, bypassing the queue. Don't reconnect
            init = messages.Init(self._system_name, self._system_type, self._resource_identifier)
            if self.send_message(init):
                # Connection is successful. Reset the time to wait between reconnects.
                self._reconnect_wait = MIN_RECONNECT_WAIT_TIME
                self._connected = True

    def disconnect(self):
        logger.info("Disconnecting")
        self._sas_sock.shutdown(socket.SHUT_RDWR)
        self._sas_sock.close()
        self._connected = False

    def send_message(self, message):
        """
        Sends a message on the socket
        :param message: Message to send
        :return: boolean success
        """
        if not isinstance(message, messages.Heartbeat):
            logger.debug("Sending message:\n%s", str(message))

        msg_array = message.serialize()
        try:
            self._sas_sock.sendall(msg_array)
            return True
        except Exception as e:
            # TODO: Find out what these exceptions are
            logger.error("Failed to send message. Error: $s\n$s", str(type(e)), str(e))
            return False

    def reconnect(self):
        self.disconnect()

        # If our connection is being rejected, don't spam the SAS with attempts. Use exponential
        # back-off.
        reconnect_wait = self._reconnect_wait
        self._reconnect_wait = min(reconnect_wait * 2, MAX_RECONNECT_WAIT_TIME)
        time.sleep(reconnect_wait)

        self.connect()
