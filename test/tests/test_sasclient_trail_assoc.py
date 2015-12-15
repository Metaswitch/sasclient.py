from metaswitch.sasclient import (
    TrailAssoc,
    Trail,
    SCOPE_NONE,
    SCOPE_BRANCH,
    SCOPE_TRACE)
from test_sasclient import SASClientTestCase

TIMESTAMP = 1450180692598
ASSOC_STRING_SCOPE_NONE = ''
ASSOC_STRING_SCOPE_BRANCH = ''
ASSOC_STRING_SCOPE_TRACE = ''


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
