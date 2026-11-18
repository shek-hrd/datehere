"""Port selection: OS-assigned by default, optional prime preference (49152-65535)."""

from __future__ import annotations

import random
import socket
from typing import Tuple

DYNAMIC_PORT_MIN = 49152
DYNAMIC_PORT_MAX = 65535


def is_prime(number: int) -> bool:
    n = int(number)
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def nearest_prime_port(preferred: int) -> int:
    preferred = min(max(int(preferred), DYNAMIC_PORT_MIN), DYNAMIC_PORT_MAX)
    lower = preferred
    upper = preferred
    while lower >= DYNAMIC_PORT_MIN or upper <= DYNAMIC_PORT_MAX:
        if lower >= DYNAMIC_PORT_MIN and is_prime(lower):
            return lower
        if upper <= DYNAMIC_PORT_MAX and is_prime(upper):
            return upper
        lower -= 1
        upper += 1
    raise RuntimeError("no prime port available in dynamic range")


def reserve_udp_port(host: str = "::", prefer_prime: bool = False) -> Tuple[socket.socket, int]:
    """Bind a UDP socket and return (socket, actual_port). Default: OS-assigned port=0."""
    family = socket.AF_INET6 if ":" in host else socket.AF_INET
    sock = socket.socket(family, socket.SOCK_DGRAM)
    try:
        if family == socket.AF_INET6:
            try:
                sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            except Exception:
                pass
        if prefer_prime:
            start = random.randint(DYNAMIC_PORT_MIN, DYNAMIC_PORT_MAX)
            tried = 0
            candidate = nearest_prime_port(start)
            while tried < 200:
                try:
                    sock.bind((host, candidate))
                    return sock, sock.getsockname()[1]
                except OSError:
                    candidate += 1
                    if candidate > DYNAMIC_PORT_MAX:
                        candidate = DYNAMIC_PORT_MIN
                    candidate = nearest_prime_port(candidate)
                    tried += 1
            sock.bind((host, 0))
        else:
            sock.bind((host, 0))
        return sock, sock.getsockname()[1]
    except Exception:
        sock.close()
        raise
