import Queue, threading
import sender


class Client(object):
    def __init__(self, system_name, system_type, resource_identifier, sas_address):
        """
        Sets up the message queue and spawns a worker thread to maintain the connection and do the work.
        """
        self._queue = Queue.Queue()
        self._stopper = threading.Event()
        self._worker = sender.MessageSender(self._stopper, self._queue, system_name, system_type, resource_identifier, sas_address)
        self._worker.setDaemon(True)
        self._worker.start()



    def stop(self):
        """
        Stop the worker thread, closing the connection. Queued messages will be dropped.
        The worker thread is a daemon, so it isn't usually necessary to call this, but a user can if they like.
        """
        self._stopper.set()
        self._queue.join()
        self._worker.join()

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