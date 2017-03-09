from metaswitch.sasclient import Analytics, Trail
from test_sasclient import SASClientTestCase

TIMESTAMP = 1450180692598

MSG_XML_NO_STORE = (
    '\x00Y\x03\x07\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x0f\x00'
    '\x00\x00\x00\x00\x00\x00\x02\x00\x00\nTestFormat\x00\x0eTestFriendlyID'
    '\x00\x00\x00\x1b<data>Analytics data</data>'
)
MSG_JSON_NO_STORE = (
    '\x00T\x03\x07\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x0f\x00'
    '\x00\x00\x00\x00\x00\x00\x01\x00\x00\nTestFormat\x00\x0eTestFriendlyID'
    '\x00\x00\x00\x16data: {"key": "value"}')
MSG_XML_STORE = (
    '\x00Y\x03\x07\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x0f\x00'
    '\x00\xde\x00\x00\x00\x00\x02\x01\x00\nTestFormat\x00\x0eTestFriendlyID'
    '\x00\x00\x00\x1b<data>Analytics data</data>'
)
MSG_JSON_STORE = (
    '\x00T\x03\x07\x00\x00\x01Q\xa5\x81Jv\x00\x00\x00\x00\x00\x00\x00o\x0f\x00'
    '\x00\xde\x00\x00\x00\x00\x01\x01\x00\nTestFormat\x00\x0eTestFriendlyID'
    '\x00\x00\x00\x16data: {"key": "value"}'
)


class SASClientAnalyticsTest(SASClientTestCase):
    """
    Test the serialisation of Analytics messages. We test against a recorded
    byte string that we know to be correct.
    """

    def test_xml_no_store(self):
        message = Analytics(Trail(),
                            Analytics.FORMAT_XML,
                            'TestFormat',
                            'TestFriendlyID',
                            False).set_timestamp(TIMESTAMP)
        message.add_variable_param('<data>Analytics data</data>')
        self.assertEqual(message.serialize(), MSG_XML_NO_STORE)
        self.assertEqual(message.get_format_type(), "XML")

    def test_json_no_store(self):
        message = Analytics(Trail(),
                            Analytics.FORMAT_JSON,
                            'TestFormat',
                            'TestFriendlyID',
                            False).set_timestamp(TIMESTAMP)
        message.add_variable_param('data: {"key": "value"}')
        self.assertEqual(message.serialize(), MSG_JSON_NO_STORE)
        self.assertEqual(message.get_format_type(), "JSON")

    def test_xml_store(self):
        message = Analytics(Trail(),
                            Analytics.FORMAT_XML,
                            'TestFormat',
                            'TestFriendlyID',
                            True,
                            222).set_timestamp(TIMESTAMP)
        message.add_variable_param('<data>Analytics data</data>')
        self.assertEqual(message.serialize(), MSG_XML_STORE)
        self.assertEqual(message.get_format_type(), "XML")

    def test_json_store(self):
        message = Analytics(Trail(),
                            Analytics.FORMAT_JSON,
                            'TestFormat',
                            'TestFriendlyID',
                            True,
                            222).set_timestamp(TIMESTAMP)
        message.add_variable_param('data: {"key": "value"}')
        self.assertEqual(message.serialize(), MSG_JSON_STORE)
        self.assertEqual(message.get_format_type(), "JSON")

    def test_string_format(self):
        message = Analytics(Trail(),
                            Analytics.FORMAT_JSON,
                            'TestFormat',
                            'TestFriendlyID',
                            True,
                            222).set_timestamp(TIMESTAMP)
        message.add_variable_param('data: {"string_test": "test_value"}')
        expected_string = (
            'SAS Message: Analytics (2015-12-15 11:58:12)\n'
            '   Static parameters: \n'
            '   Variable parameters: 1 parameters\n'
            '   Trail: 111\n'
            '   Event ID: 0x0000de\n'
            '   Instance ID: 0\n'
            '   Format Type: JSON\n'
            '   Store Msg  : True\n'
            '   Source Type: TestFormat\n'
            '   Friendly ID: TestFriendlyID\n'
        )
        self.assertEqual(str(message), expected_string)

