from metaswitch.sasclient.messages import Heartbeat
from test_sasclient import SASClientTestCase

HEARTBEAT_STRING = '\x00\x04\x03\x05'


class SASClientHeartbeatTest(SASClientTestCase):
    """
    Test the serialisation of Heartbeats. We test against recorded byte strings that we know to be
    correct.
    """
    def test_heartbeat(self):
        heartbeat = Heartbeat()
        self.assertEqual(heartbeat.serialize(), HEARTBEAT_STRING)
        # Now just check that __str__ doesn't throw
        self.assertGreater(len(str(heartbeat)), 0)
