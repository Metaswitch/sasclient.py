import Queue
import threading
import logging
from metaswitch.sasclient import sender

# The default SAS port, at the moment not configurable
DEFAULT_SAS_PORT = 6761

logger = logging.getLogger(__name__)


class Client(object):
    def __init__(self, system_name, system_type, resource_identifier, sas_address, start=True):
        """
        Constructs the client and the message queue.
        Start the sasclient. This should only be called once since the latest call to stop().
        :param system_name: The system name.
        :param system_type: The system type, e.g. "ellis", "homer"
        :param resource_identifier: Identifier of the resource bundle, e.g. org.projectclearwater.20151201
        :param sas_address: The hostname or IP address of the SAS server to communicate with, (no port).
        :param start: Whether the SAS client should start immediately
        """
        self._queue = Queue.Queue()
        self._stopper = None
        self._worker = None

        self._system_name = system_name
        self._system_type = system_type
        self._resource_identifier = resource_identifier
        self._sas_address = sas_address

        if start:
            self.start()

    def start(self):
        """
        Spins up the thread to do the work, and connects to the SAS server.
        :return:
        """
        logger.info("Starting SAS client")
        if self._worker:
            # We already had a worker. start must have been called twice consecutively. Try to recover.
            self.stop()

        self._stopper = threading.Event()
        self._worker = sender.MessageSender(self._stopper, self._queue, self._system_name, self._system_type,
                                            self._resource_identifier, self._sas_address, DEFAULT_SAS_PORT)
        self._worker.setDaemon(True)

        # Make the initial connection.
        self._worker.connect()

        # Start the message sender worker thread.
        self._worker.start()

    def stop(self):
        """
        Stop the worker thread, closing the connection, and remove references to thread-related objects. Queued messages
        will be left on the queue until the queue is garbage collected, or the queue is reused and the messages are
        sent.
        The worker thread is a daemon, so it isn't usually necessary to call this, but it is preferred.
        """
        logger.info("Stopping SAS client")
        self._stopper.set()
        self._worker.join()
        if not self._queue.empty():
            logger.warn("SAS client was stopped with messages still on the queue")

        self._worker = None
        self._stopper = None

    def send(self, message):
        self._queue.put(message)


class Trail(object):
    next_trail = 1
    next_trail_lock = threading.Lock()

    def __init__(self):
        self._trail = Trail.next_trail

        Trail.next_trail_lock.acquire()
        Trail.next_trail += 1
        Trail.next_trail_lock.release()

    def get_trail_id(self):
        return self._trail
