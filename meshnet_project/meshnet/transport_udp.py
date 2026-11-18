"""Asyncio UDP transport (simple encrypted envelope exchange)."""

from __future__ import annotations

import asyncio
from typing import Callable, Optional, Tuple

from .envelope import pack, unpack
from .port_selection import reserve_udp_port


class MeshDatagramProtocol(asyncio.DatagramProtocol):
    def __init__(self, on_message: Callable[[dict, Tuple[str, int]], None], key: bytes):
        self.on_message = on_message
        self.key = key
        self.transport: Optional[asyncio.transports.DatagramTransport] = None
        self.seen = set()

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        try:
            msg = unpack(data, self.key, seen=self.seen)
            self.on_message(msg, addr)
        except Exception:
            return


async def bind_udp_endpoint(
    host: str = "::",
    prefer_prime: bool = False,
    key: Optional[bytes] = None,
    on_message: Optional[Callable[[dict, Tuple[str, int]], None]] = None,
):
    if key is None:
        raise ValueError("session key required")
    on_message = on_message or (lambda msg, addr: None)
    loop = asyncio.get_running_loop()
    sock, port = reserve_udp_port(host=host, prefer_prime=prefer_prime)
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: MeshDatagramProtocol(on_message, key),
        sock=sock,
    )
    return transport, protocol, port


def send_envelope(transport, addr, sender, recipient, stream_id, sequence, payload: bytes, key: bytes, flags: int = 0):
    raw = pack(sender, recipient, stream_id, sequence, payload, key, flags=flags)
    transport.sendto(raw, addr)
