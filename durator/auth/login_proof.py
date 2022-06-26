from struct import Struct

from durator.auth.constants import LoginOpCode, LoginResult
from durator.auth.login_connection_state import LoginConnectionState
from durator.common.log import LOG


class LoginProof:
    """Process a proof request and answer with the server proof."""

    PROOF_BIN = Struct("<32s20s20sB")
    RESPONSE_SUCC_BIN = Struct("<2B20sI")
    RESPONSE_FAIL_BIN = Struct("<2B")

    def __init__(self, connection, packet):
        self.conn = connection
        self.packet = packet

        self.client_ephemeral = 0
        self.client_proof = b""
        self.checksum = b""
        self.unk = 0

    def process(self):
        self._parse_packet(self.packet)

        account = self.conn.account
        verifier = account.srp_verifier_as_int
        self.conn.srp.generate_session_key(self.client_ephemeral, verifier)
        self.conn.srp.generate_client_proof(self.client_ephemeral, account)
        local_client_proof = self.conn.srp.client_proof

        if local_client_proof == self.client_proof:
            LOG.debug("Login: authenticated!")
            self.conn.accept_login()
            self.conn.srp.generate_server_proof(self.client_ephemeral)
            response = self._get_success_response()
            return LoginConnectionState.SENT_PROOF, response
        else:
            LOG.warning("Login: wrong proof!")
            response = self._get_failure_response()
            return LoginConnectionState.CLOSED, response

    def _parse_packet(self, packet):
        data = self.PROOF_BIN.unpack(packet)
        self.client_ephemeral = int.from_bytes(data[0], "little")
        self.client_proof = data[1]
        self.checksum = data[2]
        self.unk = data[3]

    def _get_success_response(self):
        response = self.RESPONSE_SUCC_BIN.pack(
            LoginOpCode.LOGIN_PROOF.value, LoginResult.SUCCESS.value, self.conn.srp.server_proof, 0
        )
        return response

    def _get_failure_response(self):
        response = self.RESPONSE_FAIL_BIN.pack(LoginOpCode.LOGIN_PROOF.value, LoginResult.FAIL_1.value)
        return response
