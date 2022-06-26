from durator.common.log import LOG
from durator.world.opcodes import OpCode


class MoveWorldportAckHandler:
    def __init__(self, connection, _):
        self.conn = connection

    def process(self):
        if "worldport_ack_pending" in self.conn.shared_data:
            LOG.debug("Received expected " + str(OpCode.MSG_MOVE_WORLDPORT_ACK))
            del self.conn.shared_data["worldport_ack_pending"]
            return None, None
        else:
            LOG.error("Received unexpected " + str(OpCode.MSG_MOVE_WORLDPORT_ACK))
            return self.conn.MAIN_ERROR_STATE, None
