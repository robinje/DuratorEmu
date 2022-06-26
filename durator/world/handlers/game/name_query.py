from struct import Struct

from durator.common.log import LOG
from durator.world.opcodes import OpCode
from durator.world.world_packet import WorldPacket


class NameQueryHandler:
    """Send name associated to a GUID to the client."""

    PACKET_BIN = Struct("<Q")

    # uint64 guid
    # char[] name
    # uint32 race
    # uint32 gender
    # uint32 class
    RESPONSE_FMT = "<Q{name_len}s3I"

    def __init__(self, connection, packet):
        self.conn = connection
        self.packet = packet

        self.guid = -1

    def process(self):
        self._parse_packet(self.packet)
        LOG.debug(f"NameQuery: GUID {self.guid:X}")

        object_manager = self.conn.server.object_manager
        unit = object_manager.get_player(self.guid)
        if unit is None:
            LOG.warning("NameQueryHandler: couldn't find player {:X}".format(self.guid))
            return None, None

        response = self._get_response_packet(unit)
        return None, response

    def _parse_packet(self, packet):
        self.guid = self.PACKET_BIN.unpack(packet)[0]

    def _get_response_packet(self, unit):
        name_bytes = unit.name.encode("utf8") + b"\x00"
        name_len = len(name_bytes)
        response_struct = Struct(self.RESPONSE_FMT.format(name_len=name_len))
        response_data = response_struct.pack(self.guid, name_bytes, unit.get_race(), unit.get_gender(), unit.get_class())
        return WorldPacket(OpCode.SMSG_NAME_QUERY_RESPONSE, response_data)
