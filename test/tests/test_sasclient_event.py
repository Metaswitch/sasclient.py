from metaswitch.sasclient import Event, Trail, COMPRESS_ZLIB
from test_sasclient import SASClientTestCase

TIMESTAMP = 1450180692598
EVENT_STRING_EMPTY = (
    '\x00\x1e\x03\x03\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x0f\x00\x00\xde\x00\x00'
    '\x00\x00\x00\x00'
)
EVENT_STRING_ONE_STATIC = (
    '\x00"\x03\x03\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x0f\x00\x00\xde\x00\x00\x00'
    '\x00\x00\x04M\x01\x00\x00'
)
EVENT_STRING_TWO_STATIC = (
    '\x00&\x03\x03\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x0f\x00\x00\xde\x00\x00\x00'
    '\x00\x00\x08M\x01\x00\x00\xbc\x01\x00\x00'
)
EVENT_STRING_ONE_VAR = (
    '\x00.\x03\x03\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x0f\x00\x00\xde\x00\x00\x00'
    '\x00\x00\x00\x00\x0etest parameter'
)
EVENT_STRING_TWO_VAR = (
    '\x00D\x03\x03\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x0f\x00\x00\xde\x00\x00\x00'
    '\x00\x00\x00\x00\x0etest parameter\x00\x14other test parameter'
)
EVENT_STRING_COMPRESSED_VAR = (
    '\x006\x03\x03\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x0f\x00\x00\xde\x00\x00\x00'
    '\x00\x00\x00\x00\x16x\x9c+I-.Q(H,J\xccM-I-\x02\x00)\xd0\x05\xa2'
)
EVENT_STRING_ALL = (
    '\x00L\x03\x03\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x0f\x00\x00\xde\x00\x00\x02'
    '+\x00\x08M\x01\x00\x00\xbc\x01\x00\x00\x00\x0etest parameter\x00\x14other test parameter'
)


class SASClientEventTest(SASClientTestCase):
    """
    Test the serialisation of Events. We test against recorded byte strings that we know to be
    correct.
    """
    def test_empty(self):
        event = Event(Trail(), 222).set_timestamp(TIMESTAMP)
        self.assertEqual(event.serialize(), EVENT_STRING_EMPTY)

    def test_one_static_param(self):
        event = Event(Trail(), 222).set_timestamp(TIMESTAMP)
        event.add_static_param(333)
        self.assertEqual(event.serialize(), EVENT_STRING_ONE_STATIC)

    def test_two_static_params(self):
        event = Event(Trail(), 222).set_timestamp(TIMESTAMP)
        event.add_static_params([333, 444])
        self.assertEqual(event.serialize(), EVENT_STRING_TWO_STATIC)

    def test_one_variable_param(self):
        event = Event(Trail(), 222).set_timestamp(TIMESTAMP)
        event.add_variable_param("test parameter")
        self.assertEqual(event.serialize(), EVENT_STRING_ONE_VAR)

    def test_two_variable_params(self):
        event = Event(Trail(), 222).set_timestamp(TIMESTAMP)
        event.add_variable_params(["test parameter", "other test parameter"])
        self.assertEqual(event.serialize(), EVENT_STRING_TWO_VAR)
        # Now just check that __str__ doesn't throw
        self.assertGreater(len(str(event)), 0)

    def test_compressed_variable_param(self):
        event = Event(Trail(), 222).set_timestamp(TIMESTAMP)
        event.add_variable_param("test parameter", compress=COMPRESS_ZLIB)
        self.assertEqual(event.serialize(), EVENT_STRING_COMPRESSED_VAR)

    def test_unknown_compression(self):
        event = Event(Trail(), 222).set_timestamp(TIMESTAMP)
        with self.assertRaises(ValueError):
            event.add_variable_param("test parameter", compress='bogus_compression')

    def test_params_no_list(self):
        event = Event(Trail(), 222).set_timestamp(TIMESTAMP)
        with self.assertRaises(TypeError):
            event.add_static_params(333)
        with self.assertRaises(TypeError):
            event.add_variable_params("test parameter")

    def test_ordering(self):
        trail = Trail()
        event_static_first = Event(trail, 222).set_timestamp(TIMESTAMP)
        event_static_first.add_static_params([333, 444])
        event_static_first.add_variable_params(["test parameter", "other test parameter"])
        event_static_first.set_instance_id(555)
        event_variable_first = Event(trail, 222).set_timestamp(TIMESTAMP)
        event_variable_first.add_variable_params(["test parameter", "other test parameter"])
        event_variable_first.set_instance_id(555)
        event_variable_first.add_static_params([333, 444]).set_timestamp(TIMESTAMP)
        self.assertEqual(event_static_first.serialize(), event_variable_first.serialize())
        self.assertEqual(event_static_first.serialize(), EVENT_STRING_ALL)

    def test_interfaces(self):
        trail = Trail()
        event_constructor = Event(
            trail,
            222,
            555,
            [333, 444],
            ["test parameter", "other test parameter"]).set_timestamp(TIMESTAMP)
        event_plurals = Event(trail, 222).set_timestamp(TIMESTAMP)
        event_plurals.set_instance_id(555)
        event_plurals.add_static_params([333, 444])
        event_plurals.add_variable_params(["test parameter", "other test parameter"])
        event_singles = Event(trail, 222).set_timestamp(TIMESTAMP)
        event_singles.set_instance_id(555)
        event_singles.add_static_param(333).add_static_param(444)
        event_singles.add_variable_param("test parameter")\
            .add_variable_param("other test parameter")
        self.assertEqual(event_constructor.serialize(), event_plurals.serialize())
        self.assertEqual(event_constructor.serialize(), event_singles.serialize())
        self.assertEqual(event_constructor.serialize(), EVENT_STRING_ALL)
