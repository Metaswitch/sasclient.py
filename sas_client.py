import Queue, threading
import sender


class Client(object):
    def __init__(self, system_name, system_type, resource_identifier, sas_address):
        """
        Sets up the message queue and spawns a worker thread to maintain the connection and do the work.
        :return:
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
        :return:
        """
        self._stopper.set()
        self._queue.join()
        self._worker.join()
