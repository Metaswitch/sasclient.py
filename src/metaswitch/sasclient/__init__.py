from metaswitch.sasclient.main import Client

_client = None

# The default SAS port, at the moment not configurable
DEFAULT_SAS_PORT = 6761


def init(system_name, system_type, resource_identifier, sas_address):
    """
    """
    global _client
    if _client is not None:
        _client.start()
    else:
        _client = Client(system_name, system_type, resource_identifier, sas_address, DEFAULT_SAS_PORT)


def stop():
    """
    Stop the SAS client, dropping all unsent messages, and wait for this to be finished.
    """
    global _client
    _client.stop()


def send():
    """
    Put a message on the queue
    """
    global _client
    _client.send()
