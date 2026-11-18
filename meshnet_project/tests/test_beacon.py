import json
import urllib.request
from meshnet.mesh import MeshNetwork
from meshnet.web_beacon import start_beacon


def _get_json(url):
    with urllib.request.urlopen(url, timeout=3) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _post_json(url, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=3) as resp:
        return json.loads(resp.read().decode("utf-8"))


def test_beacon_live_session_blockchain_and_map_ui():
    net = MeshNetwork()
    a = net.add_node("android-node", platform="android", udp_port=52417)
    b = net.add_node("terminal-node", platform="terminal", udp_port=53128)
    net.connect(a, b)
    net.hail(a)
    net.broadcast_common_chat(a, "beacon test message")

    beacon = start_beacon(net, host="127.0.0.1", port=0)
    try:
        assert beacon.url.startswith("http://") and ":0/" not in beacon.url
        with urllib.request.urlopen(beacon.url, timeout=3) as resp:
            body = resp.read().decode("utf-8")
        assert "Sensei Network Map" in body
        assert "Blockchain of messages" in body
        assert "COMPLETE PROJECT OBJECTIVE" in body or "Complete Objective" in body

        state = _get_json(beacon.url + "api/state")
        assert state["chain_valid"] is True
        assert len(state["chain"]) >= 2
        assert any(n["nickname"] == "android-node" for n in state["nodes"])

        # browser join pops in as new node and hails
        joined = _post_json(beacon.url + "api/join", {"platform": "web"})
        assert joined["ok"] is True
        assert "node" in joined and joined["node"]["nickname"]
        state2 = _get_json(beacon.url + "api/state")
        assert len(state2["nodes"]) >= len(state["nodes"]) + 1
        assert any("HAIL " + joined["node"]["nickname"] in b["payload"] for b in state2["chain"])
    finally:
        beacon.stop()
