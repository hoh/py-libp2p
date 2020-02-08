from libp2p.crypto.keys import KeyPair, PrivateKey
from libp2p.network.connection.raw_connection_interface import IRawConnection
from libp2p.peer.id import ID
from libp2p.security.secure_conn_interface import ISecureConn
from libp2p.security.secure_transport_interface import ISecureTransport
from libp2p.typing import TProtocol

from .patterns import IPattern, PatternXX

PROTOCOL_ID = TProtocol("/noise")


class Transport(ISecureTransport):
    libp2p_privkey: PrivateKey
    noise_privkey: PrivateKey
    local_peer: ID
    early_data: bytes
    with_noise_pipes: bool
    # TODO: A storage of seen noise static keys for pattern IK?

    def __init__(
        self,
        libp2p_keypair: KeyPair,
        noise_privkey: PrivateKey = None,
        early_data: bytes = None,
        with_noise_pipes: bool = False,
    ) -> None:
        self.libp2p_privkey = libp2p_keypair.private_key
        self.noise_privkey = noise_privkey
        self.local_peer = ID.from_pubkey(libp2p_keypair.public_key)
        self.early_data = early_data
        self.with_noise_pipes = with_noise_pipes

        if self.with_noise_pipes:
            raise NotImplementedError

    def get_pattern(self) -> IPattern:
        if self.with_noise_pipes:
            raise NotImplementedError
        else:
            return PatternXX(self.local_peer, self.libp2p_privkey, self.noise_privkey)

    async def secure_inbound(self, conn: IRawConnection) -> ISecureConn:
        # TODO: SecureInbound attempts to complete a noise-libp2p handshake initiated
        #   by a remote peer over the given InsecureConnection.
        pattern = self.get_pattern()
        return await pattern.handshake_inbound(conn)

    async def secure_outbound(self, conn: IRawConnection, peer_id: ID) -> ISecureConn:
        # TODO: Validate libp2p pubkey with `peer_id`. Abort if not correct.
        # NOTE: Implementations that support Noise Pipes must decide whether to use
        #   an XX or IK handshake based on whether they possess a cached static
        #   Noise key for the remote peer.
        pattern = self.get_pattern()
        return await pattern.handshake_outbound(conn, peer_id)
