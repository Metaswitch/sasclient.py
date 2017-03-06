# @file __init__.py
# Copyright (C) 2015  Metaswitch Networks Ltd

import logging

from metaswitch.sasclient.main import Client, Trail, TestClient
from metaswitch.sasclient.messages import Event, TrailAssoc, Marker, Analytics
from metaswitch.sasclient.constants import *

logger = logging.getLogger(__name__)
# Let the calling application control logging
logger.addHandler(logging.NullHandler())
# Some of our applications set logging on the root logger. Don't inherit from that by default.
logger.propagate = False
logger.setLevel(logging.INFO)
