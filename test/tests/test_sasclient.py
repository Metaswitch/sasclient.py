import unittest
from metaswitch.sasclient import Trail

TRAIL_ID = 111

###################################################################################################
# Base class for SASClient testcases.
###################################################################################################


class SASClientTestCase(unittest.TestCase):

    def setUp(self):
        # Make the trail something fixed
        Trail.next_trail = TRAIL_ID

    def tearDown(self):
        pass
