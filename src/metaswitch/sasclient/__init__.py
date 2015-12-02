from metaswitch.sasclient.main import Client, Trail
from metaswitch.sasclient.messages import Event, TrailAssoc, Marker
from metaswitch.sasclient.constants import *
import logging


_client = None

# The default SAS port, at the moment not configurable
DEFAULT_SAS_PORT = 6761


def start(system_name, system_type, resource_identifier, sas_address):
    """
    Start the sasclient. This should only be called once since the latest call to stop().
    :param system_name: The system name.
    :param system_type: The system type, e.g. "ellis", "homer"
    :param resource_identifier: Identifier of the resource bundle, e.g. org.projectclearwater.20151201
    :param sas_address: The hostname or IP address of the SAS server to communicate with, (no port).
    """
    # Set up logger
    logging.basicConfig(filename='/var/log/sasclient.log', level=logging.DEBUG)

    global _client
    if _client is not None:
        _client.start(system_name, system_type, resource_identifier, sas_address, DEFAULT_SAS_PORT)
    else:
        _client = Client(system_name, system_type, resource_identifier, sas_address, DEFAULT_SAS_PORT)


def stop():
    """
    Stop the SAS client, dropping all unsent messages, and wait for this to be finished.
    """
    global _client
    _client.stop()


def send(message):
    """
    Put a message on the queue
    """
    global _client
    _client.send(message)
