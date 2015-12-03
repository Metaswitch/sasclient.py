from metaswitch.sasclient.main import Client, Trail
from metaswitch.sasclient.messages import Event, TrailAssoc, Marker
from metaswitch.sasclient.constants import *
import logging


# The default SAS port, at the moment not configurable
DEFAULT_SAS_PORT = 6761

# Set up logger
logging.basicConfig(filename='/var/tmp/sasclient.log', level=logging.DEBUG)