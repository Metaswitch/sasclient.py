# @file main.py
# Copyright (C) 2015  Metaswitch Networks Ltd

import Queue
import threading
import logging
from metaswitch.sasclient import sender

# The default SAS port, at the moment not configurable
DEFAULT_SAS_PORT = 6761

# The number of messages to queue if no value is provided.
MINIMUM_QUEUE_LENGTH = 100
DEFAULT_QUEUE_LENGTH = 10000

logger = logging.getLogger(__name__)


class Client(object):
    def __init__(self,
                 system_name,
                 system_type,
                 resource_identifier,
                 sas_address,
                 start=True,
                 queue_length=DEFAULT_QUEUE_LENGTH):
        """
        Constructs the client and the message queue.
        :param system_name: The system name
        :param system_type: The system type, e.g. "ellis", "homer"
        :param resource_identifier: Identifier of the resource bundle, e.g.
                                    org.projectclearwater.20151201
        :param sas_address: The hostname or IP address of the SAS server to communicate with, (no
                            port)
        :param start: Whether the SAS client should start immediately
        :param queue_length: The maximum number of messages to queue for sending to SAS
        """
        queue_length = max(queue_length, MINIMUM_QUEUE_LENGTH)
        self._queue = Queue.Queue(maxsize=queue_length)
        self._stopper = None
        self._worker = None
        self._discarding = None

        self._system_name = system_name
        self._system_type = system_type
        self._resource_identifier = resource_identifier
        self._sas_address = sas_address

        if start:
            self.start()

    def start(self):
        """
        Start the sasclient. This should only be called once since the latest call to stop().
        Spins up the thread to do the work, and connects to the SAS server.
        """
        if self._worker is not None:
            # We already had a worker. start must have been called twice consecutively. Try to
            # recover.
            self.stop()

        logger.info("Starting SAS client")
        self._stopper = threading.Event()
        self._discarding = threading.Event()
        self._worker = sender.MessageSender(
            self._stopper,
            self._queue,
            self._discarding,
            self._system_name,
            self._system_type,
            self._resource_identifier,
            self._sas_address,
            DEFAULT_SAS_PORT)
        self._worker.setDaemon(True)

        # Make the initial connection.
        self._worker.connect()

        # Start the message sender worker thread.
        self._worker.start()

    def stop(self):
        """
        Stop the worker thread, closing the connection, and remove references to thread-related
        objects. Queued messages will be left on the queue until the queue is garbage collected, or
        the queue is reused and the messages are sent.
        The worker thread is a daemon, so it isn't usually necessary to call this, but it is
        preferred.
        """
        logger.info("Stopping SAS client")
        self._stopper.set()
        self._worker.join()
        if not self._queue.empty():
            logger.warn("SAS client was stopped with messages still on the queue")

        self._worker = None
        self._stopper = None
        self._discarding = None

    def send(self, message):
        logger.debug("Queueing message for sending:\n%s", str(message))
        try:
            self._queue.put(message, block=False)
        except Queue.Full:
            # The message queue is full.  Inform the worker that it will need
            # to start discarding messages.
            if not self._discarding.is_set():
                logger.error("The message queue is full.  Messages queued for sending to SAS will "
                             "be discarded")
                self._discarding.set()


class Trail(object):
    next_trail = 1
    next_trail_lock = threading.Lock()

    def __init__(self):
        with Trail.next_trail_lock:
            self._trail = Trail.next_trail
            Trail.next_trail += 1

    def get_trail_id(self):
        return self._trail


class TestClient(object):
    """
    Fake implementation of the Client, to be used by the user in unit tests.
    """
    def __init__(self):
        self.message_queue = []

    def start(self):
        pass

    def stop(self):
        pass

    def send(self, message):
        self.message_queue.append(message)
