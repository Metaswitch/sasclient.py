from .messages import Event, Marker, TrailAssoc
from .main import Client

_client = None


def init(system_name, system_type, resource_identifier, sas_address):
    """
    Start the SAS client with the specified details.
    """
    global _client
    _client = Client(system_name, system_type, resource_identifier, sas_address)


def stop():
    """
    Stop the SAS client, dropping all unsent messages, and wait for this to be finished.
    """
    global _client
    _client.stop()


def new_trail():
    return _client.new_trail()