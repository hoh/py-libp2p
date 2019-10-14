import asyncio

import pytest

from libp2p.host.exceptions import ConnectionFailure
from libp2p.peer.peerinfo import PeerInfo
from tests.utils import set_up_routers, set_up_nodes_by_transport_opt, set_up_nodes_by_transport_and_disc_opt


@pytest.mark.asyncio
async def test_host_routing_success():
    routers = await set_up_routers([5678, 5679])
    transports = [["/ip4/127.0.0.1/tcp/0"], ["/ip4/127.0.0.1/tcp/0"]]
    transport_disc_opt_list = zip(transports, routers)
    (host_a, host_b) = await set_up_nodes_by_transport_and_disc_opt(transport_disc_opt_list)

    # Set routing info
    await routers[0].server.set(host_a.get_id().xor_id, PeerInfo(host_a.get_id(), host_a.get_addrs()).to_string())
    await routers[1].server.set(host_b.get_id().xor_id, PeerInfo(host_b.get_id(), host_b.get_addrs()).to_string())

    # forces to use routing as no addrs are provided
    await host_a.connect(PeerInfo(host_b.get_id(), []))
    await host_b.connect(PeerInfo(host_a.get_id(), []))

    # Clean up
    await asyncio.gather(*[host_a.close(), host_b.close()])
    routers[0].server.stop()
    routers[1].server.stop()


@pytest.mark.asyncio
async def test_host_routing_fail():
    routers = await set_up_routers([5678, 5679])
    transports = [["/ip4/127.0.0.1/tcp/0"], ["/ip4/127.0.0.1/tcp/0"]]
    transport_disc_opt_list = zip(transports, routers)
    (host_a, host_b) = await set_up_nodes_by_transport_and_disc_opt(transport_disc_opt_list)

    host_c = (await set_up_nodes_by_transport_opt([["/ip4/127.0.0.1/tcp/0"]]))[0]

    # Set routing info
    await routers[0].server.set(host_a.get_id().xor_id, PeerInfo(host_a.get_id(), host_a.get_addrs()).to_string())
    await routers[1].server.set(host_b.get_id().xor_id, PeerInfo(host_b.get_id(), host_b.get_addrs()).to_string())

    # routing fails because host_c does not use routing
    with pytest.raises(ConnectionFailure):
        await host_a.connect(PeerInfo(host_c.get_id(), []))
    with pytest.raises(ConnectionFailure):
        await host_b.connect(PeerInfo(host_c.get_id(), []))

    # Clean up
    await asyncio.gather(*[host_a.close(), host_b.close(), host_c.close()])
    routers[0].server.stop()
    routers[1].server.stop()
