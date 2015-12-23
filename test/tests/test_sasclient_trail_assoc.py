from metaswitch.sasclient import (
    TrailAssoc,
    Trail,
    SCOPE_NONE,
    SCOPE_BRANCH,
    SCOPE_TRACE)
from test_sasclient import SASClientTestCase

TIMESTAMP = 1450180692598
ASSOC_STRING_SCOPE_NONE = '\x00\x1d\x03\x02\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x00\x00\x00\x00\x00\x00\x00p\x00'
ASSOC_STRING_SCOPE_BRANCH = '\x00\x1d\x03\x02\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x00\x00\x00\x00\x00\x00\x00p\x01'
ASSOC_STRING_SCOPE_TRACE = '\x00\x1d\x03\x02\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x00\x00\x00\x00\x00\x00\x00p\x02'


class SASClientTrailAssocTest(SASClientTestCase):
    """
    Test the serialisation of Trail Associations. We test against recorded byte strings that we
    know to be correct.
    """
    def test_scope_none(self):
        assoc = TrailAssoc(Trail(), Trail(), SCOPE_NONE).set_timestamp(TIMESTAMP)
        assert assoc.serialize() == ASSOC_STRING_SCOPE_NONE

    def test_scope_branch(self):
        assoc = TrailAssoc(Trail(), Trail(), SCOPE_BRANCH).set_timestamp(TIMESTAMP)
        assert assoc.serialize() == ASSOC_STRING_SCOPE_BRANCH

    def test_scope_trace(self):
        assoc = TrailAssoc(Trail(), Trail(), SCOPE_TRACE).set_timestamp(TIMESTAMP)
        assert assoc.serialize() == ASSOC_STRING_SCOPE_TRACE
        # Now just check that __str__ doesn't throw
        assert len(str(assoc)) > 0
