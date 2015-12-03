from metaswitch.sasclient.main import Client, Trail
from metaswitch.sasclient.messages import Event, TrailAssoc, Marker
from metaswitch.sasclient.constants import *
import logging


# Set up logger
logging.basicConfig(filename='/var/tmp/sasclient.log', level=logging.DEBUG)