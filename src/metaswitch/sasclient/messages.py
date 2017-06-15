# @file messages.py
# Copyright (C) 2015  Metaswitch Networks Ltd

import struct
import time
import datetime
import zlib
from metaswitch.sasclient.constants import (
    FLAG_ASSOCIATE,
    FLAG_NO_REACTIVATE,
    INTERFACE_VERSION,
    MESSAGE_EVENT,
    MESSAGE_HEARTBEAT,
    MESSAGE_INITIALISATION,
    MESSAGE_MARKER,
    MESSAGE_ANALYTICS,
    MESSAGE_STRINGS,
    MESSAGE_TRAIL_ASSOCIATION,
    PROTOCOL_VERSION,
    SCOPE_NONE,
    COMPRESS_ZLIB)

# The base event ID for all events specified by resource bundles.
RESOURCE_BUNDLE_BASE = 0x0F000000


class Message(object):
    """
    Message that can be sent to SAS. All messages are made of two parts, a header and a body, the
    format of which are specified by the VPED protocol. Strings are encoded as length + data,
    denoted by "1+n".

    The header is of the form:
    2 bytes - length of message (including header)
    1 byte - the protocol version
    1 byte - the message type
    8 bytes - the timestamp of the message (in ms) (not present in heartbeat message)

    The body varies depending on the message type - see implementations.
    """

    def __init__(self):
        self.timestamp = int(time.time() * 1000)
        self.msg_type = None

    def serialize_header(self, body_length):
        return struct.pack(
            '!hbbq',
            body_length + 12,
            INTERFACE_VERSION,
            self.msg_type,
            self.timestamp)

    def serialize_body(self):
        """
        Default implementation for messages with no body (e.g. heartbeat).
        """
        return struct.pack('')

    def serialize(self):
        """
        Convert the python message into a serialized string conforming to the VPED protocol.
        """
        body = self.serialize_body()
        header = self.serialize_header(len(body))
        return header + body

    def __str__(self):
        return "SAS Message: {0} ({1})".format(
            MESSAGE_STRINGS.get(self.msg_type, "Unknown type"),
            datetime.datetime.fromtimestamp(self.timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S'))

    def set_timestamp(self, timestamp):
        """
        Set the timestamp in milliseconds.
        :return: self, for fluent API
        """
        self.timestamp = timestamp
        return self


class Init(Message):
    """
    Message used when connecting to SAS. Not exposed to the user app.
    The body is of the form:
    1+n bytes - system name
    4 bytes - number 1 in native endian
    1+n bytes - protocol version
    1+n bytes - system type (e.g. sprout)
    1+n bytes - resource bundle ID
    1+n bytes - resource version (currently not implemented)
    """
    msg_type = MESSAGE_INITIALISATION

    def __init__(self, system_name, system_type, resource_identifier, resource_version=''):
        super(Init, self).__init__()
        self.system_name = system_name
        self.system_type = system_type
        self.resource_identifier = resource_identifier
        self.resource_version = resource_version
        self.msg_type = Init.msg_type

    def serialize_body(self):
        return ''.join([
            pack_string(self.system_name),
            struct.pack('=i', 1),
            pack_string(PROTOCOL_VERSION),
            pack_string(self.system_type),
            pack_string(self.resource_identifier),
            pack_string(self.resource_version)])

    def __str__(self):
        return ("{string}\n" +
                "   System name: {name}\n" +
                "   System type: {sys_type}\n" +
                "   Resource identifier: {res_id}\n" +
                "   Resource version: {ver}").format(
                    string=Message.__str__(self),
                    name=self.system_name,
                    sys_type=self.system_type,
                    res_id=self.resource_identifier,
                    ver=self.resource_version)


def pack_string(string):
    """
    Pack a string with its length.
    """
    data = string.encode('UTF-8') if isinstance(string, unicode) else str(string)
    return struct.pack('b', len(data)) + data


class TrailAssoc(Message):
    """
    Message used to associate trails manually.
    The body is of the form:
    8 bytes - trail A
    8 bytes - trail B
    1 byte - scope
    """
    msg_type = MESSAGE_TRAIL_ASSOCIATION

    def __init__(self, trail_a, trail_b, scope):
        super(TrailAssoc, self).__init__()
        self.trail_a_id = trail_a.get_trail_id()
        self.trail_b_id = trail_b.get_trail_id()
        self.scope = scope
        self.msg_type = TrailAssoc.msg_type

    def serialize_body(self):
        return struct.pack('!qqb', self.trail_a_id, self.trail_b_id, self.scope)

    def __str__(self):
        return ("{string}\n" +
                "   Trail A: {trail_a:d}\n" +
                "   Trail B: {trail_b:d}\n" +
                "   Scope: {scope:d}").format(
                    string=Message.__str__(self),
                    trail_a=self.trail_a_id,
                    trail_b=self.trail_b_id,
                    scope=self.scope)


class DataMessage(Message):
    """
    Message with included variable and static parameters. These consist of a header, the
    message-type-specific variables (in a fixed order) - see implementations, and then:
    2 bytes - length of static parameters
    4 bytes - static parameter 1
    4 bytes - static parameter 2
    ...etc.
    2 + n bytes - variable length parameter 1 (+ length)
    2 + n bytes - variable length parameter 2 (+ length)
    ...etc.
    """
    def __init__(self, static_params, var_params):
        super(DataMessage, self).__init__()
        self.static_params = static_params[:]
        self.var_params = []
        self.add_variable_params(var_params)

    def serialize_params(self):
        static_data = ''.join(
            [struct.pack('=i', static_param) for static_param in self.static_params])
        static_data = struct.pack('!h', len(static_data)) + static_data

        var_data = ''.join([
            struct.pack('!h', len(var_param)) + var_param
            for var_param in self.var_params])

        return static_data + var_data

    # Fluent interfaces to add params
    def add_static_params(self, static_params):
        if not isinstance(static_params, list):
            raise TypeError("Expecting a list")
        self.static_params += static_params
        return self

    def add_static_param(self, static_param):
        self.static_params.append(static_param)
        return self

    def add_variable_params(self, var_params, compress=None):
        if not isinstance(var_params, list):
            raise TypeError("Expecting a list")
        [self.add_variable_param(p, compress) for p in var_params]
        return self

    def add_variable_param(self, var_param, compress=None):
        enc_value = var_param.encode('UTF-8') if isinstance(var_param, unicode) else str(var_param)

        if compress == COMPRESS_ZLIB:
            # Compress with zlib
            enc_value = zlib.compress(enc_value)
        elif compress is not None:
            # Unrecognised compression type
            raise ValueError("Unrecognised compression type: {}".format(compress))

        self.var_params.append(enc_value)
        return self

    def __str__(self):
        return ("{string}\n" +
                "   Static parameters: {static_params}\n" +
                "   Variable parameters: {var_params}").format(
                    string=Message.__str__(self),
                    static_params=",".join([str(param) for param in self.static_params]),
                    var_params="{amount} parameters".format(amount=len(self.var_params)))


class Event(DataMessage):
    """
    Message used to indicate that something has happened.
    The body is of the form:
    8 bytes - trail ID
    4 bytes - event ID - because we use interface version 3, we need to bitwise OR this with
                         RESOURCE_BUNDLE_BASE
    4 bytes - instance ID (unique in codebase, to see from where this event was called)
    static and variable params (see above)
    """
    msg_type = MESSAGE_EVENT

    def __init__(self, trail, event_id, instance_id=0, static_params=None, var_params=None):
        if var_params is None:
            var_params = []
        if static_params is None:
            static_params = []
        super(Event, self).__init__(static_params, var_params)
        self.trail_id = trail.get_trail_id()
        self.event_id = event_id
        self.instance_id = instance_id
        self.msg_type = Event.msg_type

    def serialize_body(self):
        return self.serialize_event_headers() + self.serialize_params()

    def serialize_event_headers(self):
        """Serialise the headers that are specific to Events"""
        return struct.pack(
            '!qii', self.trail_id,
            self.event_id | RESOURCE_BUNDLE_BASE,
            self.instance_id)

    def set_instance_id(self, instance_id):
        """
        :param instance_id: instance id for identifying this SAS message from within the NE code
        :return: self, for fluent interface
        """
        self.instance_id = instance_id
        return self

    def __str__(self):
        return ("{string}\n" +
                "   Trail: {trail:d}\n" +
                "   Event ID: 0x{event:06x}\n" +
                "   Instance ID: {instance:d}").format(
                    string=DataMessage.__str__(self),
                    trail=self.trail_id,
                    event=self.event_id,
                    instance=self.instance_id)


class Marker(DataMessage):
    """
    Message used to provide metadata about the trails.
    The body is of the form:
    8 bytes - trail ID
    4 bytes - marker ID
    4 bytes - instance ID
    1 byte - flags, where FLAG_ASSOCIATE should be set if scope is not SCOPE_NONE, and if this is
             the case FLAG_NO_REACTIVATE may also be set
    1 byte - scope, either SCOPE_NONE, SCOPE_BRANCH or SCOPE_TRACE
    """
    msg_type = MESSAGE_MARKER

    def __init__(
            self,
            trail,
            marker_id,
            instance_id=0,
            reactivate=True,
            scope=SCOPE_NONE,
            static_params=None,
            var_params=None):
        if var_params is None:
            var_params = []
        if static_params is None:
            static_params = []
        super(Marker, self).__init__(static_params, var_params)
        self.trail_id = trail.get_trail_id()
        self.marker_id = marker_id
        self.instance_id = instance_id
        self.reactivate = reactivate
        self.scope = scope
        self.msg_type = Marker.msg_type

    def serialize_body(self):
        flags = 0
        if self.scope != SCOPE_NONE:
            flags |= FLAG_ASSOCIATE
            if not self.reactivate:
                flags |= FLAG_NO_REACTIVATE
        return struct.pack(
            '!qiibb',
            self.trail_id,
            self.marker_id,
            self.instance_id,
            flags,
            self.scope) + self.serialize_params()

    def set_association_scope(self, scope):
        """
        :param scope: association scope
        :return: self, for fluent interface
        """
        self.scope = scope
        return self

    def set_reactivate(self, reactivate):
        """
        :param reactivate: reactivate flag (boolean)
        :return: self, for fluent interface
        """
        self.reactivate = reactivate
        return self

    def set_instance_id(self, instance_id):
        """
        :param instance_id: instance id for identifying this SAS message from within the NE code
        :return: self, for fluent interface
        """
        self.instance_id = instance_id
        return self

    def __str__(self):
        return ("{string}\n" +
                "   Trail: {trail:d}\n" +
                "   Marker ID: 0x{marker:08x}\n" +
                "   Instance ID: {instance:d}\n" +
                "   Scope: {scope:d}\n" +
                "   Reactivate: {react}").format(
                    string=DataMessage.__str__(self),
                    trail=self.trail_id,
                    marker=self.marker_id,
                    instance=self.instance_id,
                    scope=self.scope,
                    react=("True" if self.reactivate else "False"))


class Analytics(Event):
    """
    Message that should be forwarded to an analytics server.
    The body is of the form:
    8 bytes - trail ID
    4 bytes - marker ID
    4 bytes - instance ID
    1 byte      - format type, this should be one of FORMAT_JSON or FORMAT_XML
    2 + n bytes - source type (+ length)
    2 + n bytes - friendly id (+ length)
    static and variable params (as for Event)
    """

    # Format types, this specifies how SAS should format the message before
    # forwarding it to an analytics server.
    FORMAT_JSON = 1
    FORMAT_XML = 2

    msg_type = MESSAGE_ANALYTICS

    def __init__(self,
                 trail,
                 format_type,
                 source_type,
                 friendly_id,
                 store_event=False,
                 event_id=0,
                 inst_id=0,
                 static_params=None,
                 var_params=None):

        super(Analytics, self).__init__(trail,
                                        event_id,
                                        inst_id,
                                        static_params,
                                        var_params)
        self.trail = trail
        self.format_type = format_type
        self.source_type = source_type
        self.friendly_id = friendly_id
        self.store_event = store_event
        self.msg_type = Analytics.msg_type

    def serialize_event_headers(self):
        # The initial headers are the same as for Events so call into the
        # superclass method.
        analytics_headers = super(Analytics, self).serialize_event_headers()

        # Now add Analytics specific headers
        analytics_headers += struct.pack('!bb',
                                         self.format_type, self.store_event)
        analytics_headers += struct.pack('!h', len(self.source_type)) + str(self.source_type)
        analytics_headers += struct.pack('!h', len(self.friendly_id)) + str(self.friendly_id)
        return analytics_headers

    def get_format_type(self):
        format_str = "Unknown"

        if self.format_type == Analytics.FORMAT_JSON:
            format_str = "JSON"
        elif self.format_type == Analytics.FORMAT_XML:
            format_str = "XML"

        return format_str

    def __str__(self):
        return ("{string}\n" +
                "   Format Type: {format_type}\n" +
                "   Store Msg  : {store}\n"
                "   Source Type: {source_type}\n" +
                "   Friendly ID: {friendly_id}\n").format(
                    string=Event.__str__(self),
                    format_type=self.get_format_type(),
                    store=self.store_event,
                    source_type=self.source_type,
                    friendly_id=self.friendly_id)


class Heartbeat(Message):
    """
    Message used to keep the connection alive. Consists of just the message header, without the
    timestamp.
    """
    msg_type = MESSAGE_HEARTBEAT

    def __init__(self):
        super(Heartbeat, self).__init__()
        self.msg_type = Heartbeat.msg_type

    def serialize_header(self, body_length):
        return struct.pack('!hbb', body_length + 4, INTERFACE_VERSION, self.msg_type)

    def __str__(self):
        return "SAS Heartbeat"
