import Queue
import threading

from src.metaswitch.sasclient import sender


class Client(object):
    def __init__(self, system_name, system_type, resource_identifier, sas_address, sas_port, interface_version, protocol_version):
        """
        Sets up the message queue and spawns a worker thread to maintain the connection and do the work.
        """
        self._queue = Queue.Queue()
        self._stopper = threading.Event()
        self._worker = sender.MessageSender(self._stopper, self._queue, system_name, system_type, resource_identifier, sas_address, sas_port)
        self._worker.setDaemon(True)
        self.start()

    def start(self):
        # Make the initial connection.
        self._worker.connect()

        # Start the message sender worker thread.
        self._worker.start()

    def stop(self):
        """
        Stop the worker thread, closing the connection. Queued messages will be left on the queue until the queue
        is garbage collected, or the queue is reused and the messages are sent.
        The worker thread is a daemon, so it isn't usually necessary to call this, but it is preferred.
        """
        self._stopper.set()
        self._worker.join()
        if self._queue.empty():
            # TODO: log that the queue exited successfully, with no messages left
            pass
        else:
            # TODO: log that the queue exited with messages still on.
            pass

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
