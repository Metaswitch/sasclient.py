from metaswitch.sasclient import Event, Trail
from test_sasclient import SASClientTestCase

TIMESTAMP = 1450180692598
EVENT_STRING_EMPTY = '\x00\x1e\x03\x03\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x0f\x00\x00\xde\x00\x00\x00\x00\x00\x00'
EVENT_STRING_ONE_STATIC = '\x00"\x03\x03\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x0f\x00\x00\xde\x00\x00\x00\x00\x00\x04M\x01\x00\x00'
EVENT_STRING_TWO_STATIC = '\x00&\x03\x03\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x0f\x00\x00\xde\x00\x00\x00\x00\x00\x08M\x01\x00\x00\xbc\x01\x00\x00'
EVENT_STRING_ONE_VAR = '\x00.\x03\x03\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x0f\x00\x00\xde\x00\x00\x00\x00\x00\x00\x00\x0etest parameter'
EVENT_STRING_TWO_VAR = '\x00D\x03\x03\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x0f\x00\x00\xde\x00\x00\x00\x00\x00\x00\x00\x0etest parameter\x00\x14other test parameter'
EVENT_STRING_ALL = '\x00L\x03\x03\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x0f\x00\x00\xde\x00\x00\x02+\x00\x08M\x01\x00\x00\xbc\x01\x00\x00\x00\x0etest parameter\x00\x14other test parameter'


class SASClientEventTest(SASClientTestCase):
    def test_empty(self):
        event = Event(Trail(), 222).set_timestamp(TIMESTAMP)
        assert event.serialize() == EVENT_STRING_EMPTY

    def test_one_static_param(self):
        event = Event(Trail(), 222).set_timestamp(TIMESTAMP)
        event.add_static_param(333)
        assert event.serialize() == EVENT_STRING_ONE_STATIC

    def test_two_static_params(self):
        event = Event(Trail(), 222).set_timestamp(TIMESTAMP)
        event.add_static_params([333, 444])
        assert event.serialize() == EVENT_STRING_TWO_STATIC

    def test_one_variable_param(self):
        event = Event(Trail(), 222).set_timestamp(TIMESTAMP)
        event.add_variable_param("test parameter")
        assert event.serialize() == EVENT_STRING_ONE_VAR

    def test_two_variable_params(self):
        event = Event(Trail(), 222).set_timestamp(TIMESTAMP)
        event.add_variable_params(["test parameter", "other test parameter"])
        assert event.serialize() == EVENT_STRING_TWO_VAR

    def test_ordering(self):
        trail = Trail()
        event_static_first = Event(trail, 222).set_timestamp(TIMESTAMP)
        event_static_first.add_static_params([333, 444])
        event_static_first.add_variable_params(["test parameter", "other test parameter"])
        event_static_first.instance_id = 555
        event_variable_first = Event(trail, 222).set_timestamp(TIMESTAMP)
        event_variable_first.add_variable_params(["test parameter", "other test parameter"])
        event_variable_first.instance_id = 555
        event_variable_first.add_static_params([333, 444]).set_timestamp(TIMESTAMP)
        assert event_static_first.serialize() == event_variable_first.serialize()
        assert event_static_first.serialize() == EVENT_STRING_ALL

    def test_interfaces(self):
        trail = Trail()
        event_constructor = Event(
            trail,
            222,
            555,
            [333, 444],
            ["test parameter", "other test parameter"]).set_timestamp(TIMESTAMP)
        event_plurals = Event(trail, 222).set_timestamp(TIMESTAMP)
        event_plurals.instance_id = 555
        event_plurals.add_static_params([333,444])
        event_plurals.add_variable_params(["test parameter", "other test parameter"])
        event_singles = Event(trail, 222).set_timestamp(TIMESTAMP)
        event_singles.instance_id = 555
        event_singles.add_static_param(333).add_static_param(444)
        event_singles.add_variable_param("test parameter").add_variable_param("other test parameter")
        assert event_constructor.serialize() == event_plurals.serialize()
        assert event_constructor.serialize() == event_singles.serialize()
        assert event_constructor.serialize() == EVENT_STRING_ALL
