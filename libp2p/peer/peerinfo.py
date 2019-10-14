import json
from typing import List, Sequence

import multiaddr

from .id import ID


class PeerInfo:

    peer_id: ID
    addrs: List[multiaddr.Multiaddr]

    def __init__(self, peer_id: ID, addrs: Sequence[multiaddr.Multiaddr]) -> None:
        self.peer_id = peer_id
        self.addrs = list(addrs)

    def to_string(self) -> str:
        return json.dumps([self.peer_id.to_string(), list(map(lambda a: str(a), self.addrs))])

    def __eq__(self, other):
        return isinstance(other, PeerInfo) and self.peer_id == other.peer_id and self.addrs == other.addrs

    @classmethod
    def info_from_string(cls, info: str) -> "PeerInfo":
        peer_id, raw_addrs = json.loads(info)
        return PeerInfo(ID.from_base58(peer_id), list(map(lambda a: multiaddr.Multiaddr(a), raw_addrs)))


def info_from_p2p_addr(addr: multiaddr.Multiaddr) -> PeerInfo:
    if not addr:
        raise InvalidAddrError("`addr` should not be `None`")

    if not isinstance(addr, multiaddr.Multiaddr):
        raise InvalidAddrError(f"`addr`={addr} should be of type `Multiaddr`")

    parts = addr.split()
    if not parts:
        raise InvalidAddrError(
            f"`parts`={parts} should at least have a protocol `P_P2P`"
        )

    p2p_part = parts[-1]
    last_protocol_code = p2p_part.protocols()[0].code
    if last_protocol_code != multiaddr.protocols.P_P2P:
        raise InvalidAddrError(
            f"The last protocol should be `P_P2P` instead of `{last_protocol_code}`"
        )

    # make sure the /p2p value parses as a peer.ID
    peer_id_str: str = p2p_part.value_for_protocol(multiaddr.protocols.P_P2P)
    peer_id: ID = ID.from_base58(peer_id_str)

    # we might have received just an / p2p part, which means there's no addr.
    if len(parts) > 1:
        addr = multiaddr.Multiaddr.join(*parts[:-1])

    return PeerInfo(peer_id, [addr])


class InvalidAddrError(ValueError):
    pass
