import asyncio
import pytest

from meshnet.envelope import generate_session_key
from meshnet.transport_udp import bind_udp_endpoint, send_envelope


@pytest.mark.asyncio
async def test_udp_loopback_envelope_exchange():
    key = generate_session_key()
    received = []

    def on_msg(msg, addr):
        received.append(msg)

    transport_b, protocol_b, port_b = await bind_udp_endpoint(host="127.0.0.1", prefer_prime=False, key=key, on_message=on_msg)
    transport_a, protocol_a, port_a = await bind_udp_endpoint(host="127.0.0.1", prefer_prime=False, key=key)
    try:
        send_envelope(transport_a, ("127.0.0.1", port_b), "node-a", "node-b", 1, 0, b"ping", key)
        for _ in range(50):
            if received:
                break
            await asyncio.sleep(0.02)
        assert received, "no UDP envelope received"
        assert received[0]["payload"] == b"ping"
        assert received[0]["sender"] == "node-a"
    finally:
        transport_a.close()
        transport_b.close()
