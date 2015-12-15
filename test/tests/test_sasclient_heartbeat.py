from metaswitch.sasclient.messages import Heartbeat
from test_sasclient import SASClientTestCase

HEARTBEAT_STRING = ''


class SASClientHeartbeatTest(SASClientTestCase):
    """
    Test the serialisation of Heartbeats. We test against recorded byte strings that we know to be
    correct.
    """
    def test_heartbeat(self):
        heartbeat = Heartbeat()
        assert heartbeat.serialize() == HEARTBEAT_STRING