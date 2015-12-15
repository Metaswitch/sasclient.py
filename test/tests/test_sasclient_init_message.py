from metaswitch.sasclient.messages import Init
from test_sasclient import SASClientTestCase

TIMESTAMP = 1450180692598
INIT_STRING_EMPTY = ''
INIT_STRING_NONEMPTY = ''


class SASClientInitMessageTest(SASClientTestCase):
    """
    Test the serialisation of Init messages. We test against recorded byte strings that we know to
    be correct.
    """
    def test_empty_strings(self):
        init = Init('', '', '').set_timestamp(TIMESTAMP)
        assert init.serialize() == INIT_STRING_EMPTY

    def test_nonempty_strings(self):
        init = Init("ellis@ellis.cw-ngv.com", "ellis", "org.projectclearwater.20151201", '1.1')
        init.set_timestamp(TIMESTAMP)
        assert init.serialize() == INIT_STRING_NONEMPTY