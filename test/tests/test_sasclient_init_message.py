from metaswitch.sasclient.messages import Init
from test_sasclient import SASClientTestCase

TIMESTAMP = 1450180692598
INIT_STRING_EMPTY = '\x00\x19\x03\x01\x00\x00\x01Q\xa5\x81Jv\x00\x01\x00\x00\x00\x04v0.1\x00\x00\x00'
INIT_STRING_NONEMPTY = '\x00U\x03\x01\x00\x00\x01Q\xa5\x81Jv\x16ellis@ellis.cw-ngv.com\x01\x00\x00\x00\x04v0.1\x05ellis\x1eorg.projectclearwater.20151201\x031.1'


class SASClientInitMessageTest(SASClientTestCase):
    """
    Test the serialisation of Init messages. We test against recorded byte strings that we know to
    be correct.
    """
    def test_empty_strings(self):
        init = Init('', '', '').set_timestamp(TIMESTAMP)
        self.assertEqual(init.serialize(), INIT_STRING_EMPTY)

    def test_nonempty_strings(self):
        init = Init("ellis@ellis.cw-ngv.com", "ellis", "org.projectclearwater.20151201", '1.1')
        init.set_timestamp(TIMESTAMP)
        self.assertEqual(init.serialize(), INIT_STRING_NONEMPTY)
        # Now just check that __str__ doesn't throw
        self.assertGreater(len(str(init)), 0)
