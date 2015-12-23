from metaswitch.sasclient import (
    Marker,
    Trail,
    SCOPE_NONE,
    SCOPE_TRACE,
    SCOPE_BRANCH)
from test_sasclient import SASClientTestCase

TIMESTAMP = 1450180692598
MARKER_STRING_EMPTY = '\x00 \x03\x04\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x00\x00\x00\xde\x00\x00\x00\x00\x00\x00\x00\x00'
MARKER_STRING_ONE_STATIC = '\x00$\x03\x04\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x00\x00\x00\xde\x00\x00\x00\x00\x00\x00\x00\x04M\x01\x00\x00'
MARKER_STRING_TWO_STATIC = '\x00(\x03\x04\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x00\x00\x00\xde\x00\x00\x00\x00\x00\x00\x00\x08M\x01\x00\x00\xbc\x01\x00\x00'
MARKER_STRING_ONE_VAR = '\x000\x03\x04\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x00\x00\x00\xde\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0etest parameter'
MARKER_STRING_TWO_VAR = '\x00F\x03\x04\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x00\x00\x00\xde\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0etest parameter\x00\x14other test parameter'
MARKER_STRING_ALL = '\x00N\x03\x04\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x00\x00\x00\xde\x00\x00\x02+\x00\x00\x00\x08M\x01\x00\x00\xbc\x01\x00\x00\x00\x0etest parameter\x00\x14other test parameter' 
MARKER_STRING_BRANCH = '\x00 \x03\x04\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x00\x00\x00\xde\x00\x00\x00\x00\x01\x01\x00\x00'
MARKER_STRING_TRACE = '\x00 \x03\x04\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x00\x00\x00\xde\x00\x00\x00\x00\x01\x02\x00\x00' 
MARKER_STRING_REACTIVATE = '\x00 \x03\x04\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x00\x00\x00\xde\x00\x00\x00\x00\x03\x01\x00\x00'


class SASClientMarkerTest(SASClientTestCase):
    """
    Test the serialisation of Markers. We test against recorded byte strings that we know to be
    correct.
    """
    def test_empty(self):
        marker = Marker(Trail(), 222).set_timestamp(TIMESTAMP)
        assert marker.serialize() == MARKER_STRING_EMPTY

    def test_one_static_param(self):
        marker = Marker(Trail(), 222).set_timestamp(TIMESTAMP)
        marker.add_static_param(333)
        assert marker.serialize() == MARKER_STRING_ONE_STATIC

    def test_two_static_params(self):
        marker = Marker(Trail(), 222).set_timestamp(TIMESTAMP)
        marker.add_static_params([333, 444])
        assert marker.serialize() == MARKER_STRING_TWO_STATIC

    def test_one_variable_param(self):
        marker = Marker(Trail(), 222).set_timestamp(TIMESTAMP)
        marker.add_variable_param("test parameter")
        assert marker.serialize() == MARKER_STRING_ONE_VAR

    def test_two_variable_params(self):
        marker = Marker(Trail(), 222).set_timestamp(TIMESTAMP)
        marker.add_variable_params(["test parameter", "other test parameter"])
        assert marker.serialize() == MARKER_STRING_TWO_VAR
        # Now just check that __str__ doesn't throw
        assert len(str(marker)) > 0

    def test_params_no_list(self):
        marker = Marker(Trail(), 222).set_timestamp(TIMESTAMP)
        with self.assertRaises(TypeError):
            marker.add_static_params(333)
        with self.assertRaises(TypeError):
            marker.add_variable_params("test parameter")

    def test_ordering(self):
        trail = Trail()
        marker_static_first = Marker(trail, 222).set_timestamp(TIMESTAMP)
        marker_static_first.add_static_params([333, 444])
        marker_static_first.add_variable_params(["test parameter", "other test parameter"])
        marker_static_first.set_instance_id(555)
        marker_variable_first = Marker(trail, 222).set_timestamp(TIMESTAMP)
        marker_variable_first.add_variable_params(["test parameter", "other test parameter"])
        marker_variable_first.set_instance_id(555)
        marker_variable_first.add_static_params([333, 444]).set_timestamp(TIMESTAMP)
        assert marker_static_first.serialize() == marker_variable_first.serialize()
        assert marker_static_first.serialize() == MARKER_STRING_ALL

    def test_interfaces(self):
        trail = Trail()
        marker_constructor = Marker(
            trail,
            222,
            555,
            False,
            SCOPE_NONE,
            [333, 444],
            ["test parameter", "other test parameter"]).set_timestamp(TIMESTAMP)
        marker_plurals = Marker(trail, 222).set_timestamp(TIMESTAMP)
        marker_plurals.set_instance_id(555)
        marker_plurals.add_static_params([333,444])
        marker_plurals.add_variable_params(["test parameter", "other test parameter"])
        marker_singles = Marker(trail, 222).set_timestamp(TIMESTAMP)
        marker_singles.set_instance_id(555)
        marker_singles.add_static_param(333).add_static_param(444)
        marker_singles.add_variable_param("test parameter").add_variable_param("other test parameter")
        assert marker_constructor.serialize() == marker_plurals.serialize()
        assert marker_constructor.serialize() == marker_singles.serialize()
        assert marker_constructor.serialize() == MARKER_STRING_ALL

    def test_scope_branch(self):
        marker = Marker(Trail(), 222).set_timestamp(TIMESTAMP)
        marker.set_association_scope(SCOPE_BRANCH)
        assert marker.serialize() == MARKER_STRING_BRANCH
        pass

    def test_scope_trace(self):
        marker = Marker(Trail(), 222).set_timestamp(TIMESTAMP)
        marker.set_association_scope(SCOPE_TRACE)
        assert marker.serialize() == MARKER_STRING_TRACE
        pass

    def test_reactivate(self):
        marker = Marker(Trail(), 222).set_timestamp(TIMESTAMP)
        marker.set_association_scope(SCOPE_BRANCH).set_reactivate(False)
        assert marker.serialize() == MARKER_STRING_REACTIVATE
        pass

    def test_reactivate_scope_none(self):
        marker = Marker(Trail(), 222).set_timestamp(TIMESTAMP)
        marker.set_reactivate(False)
        assert marker.serialize() == MARKER_STRING_EMPTY
        pass
