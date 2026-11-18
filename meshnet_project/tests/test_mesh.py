import pytest
from meshnet.mesh import MeshNetwork, NicknameTakenError
from meshnet.objective import HELP_TEXT


def test_unique_nicknames_and_resolve():
    net = MeshNetwork()
    a = net.add_node("fixed-node", platform="android")
    b = net.add_node(platform="terminal")
    assert a.nickname == "fixed-node"
    assert b.nickname != a.nickname
    assert net.resolve("fixed-node").node_id == a.node_id
    with pytest.raises(NicknameTakenError):
        net.add_node("fixed-node")


def test_direct_chat_ping_route_and_blockchain():
    net = MeshNetwork()
    a = net.add_node("alice", platform="android", udp_port=50001)
    b = net.add_node("bob", platform="terminal", udp_port=50002)
    net.connect(a, b)
    msg = net.send_chat("alice", "bob", "hello")
    assert msg["hops"] == 1
    assert msg["path"] == ["alice", "bob"]
    assert any(m["payload"] == "hello" and m["kind"] == "chat" for m in b.public_log)
    ping = net.ping("alice", "bob")
    assert ping.hops == 1 and ping.path == ["alice", "bob"] and ping.latency_ms > 0
    assert net.render_route("alice", "bob") == "alice -> bob"
    assert net.blockchain.verify()
    assert len(net.blockchain.chain) >= 2  # genesis + chat


def test_multihop_group_reroute_hail_and_chain():
    net = MeshNetwork()
    # Explicit node_ids make equal-length path selection deterministic (BFS explores neighbors in sorted node_id order).
    a = net.add_node("android-node", platform="android", udp_port=52417, node_id="node-a-android")
    b = net.add_node("terminal-node", platform="terminal", udp_port=53128, node_id="node-b-terminal")
    c = net.add_node("browser-node", platform="web", node_id="node-c-browser")
    d = net.add_node("alt-node", platform="bash", node_id="node-d-alt")
    net.connect(a, b); net.connect(b, c)
    net.connect(a, d); net.connect(d, c)

    assert net.route_nicknames(a, c) == ["android-node", "terminal-node", "browser-node"]
    net.create_group("team", [a, b, c])
    delivered = net.send_group_chat("android-node", "team", "status")
    assert len(delivered) == 2

    net.remove_node(b)
    assert net.route_nicknames(a, c) == ["android-node", "alt-node", "browser-node"]
    assert net.ping(a, c).hops == 2

    hail = net.hail(a)
    assert hail["kind"] == "system"
    assert "HAIL android-node joined the mesh" in hail["payload"]
    assert "udp_port=52417" in hail["payload"]
    assert any(m["payload"] == hail["payload"] for m in c.public_log)

    assert net.blockchain.verify()
    assert len(net.blockchain.chain) >= 4  # genesis + group msgs + hail


def test_help_available():
    net = MeshNetwork()
    assert net.show_help() == HELP_TEXT
