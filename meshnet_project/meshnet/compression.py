"""Compress-before-encrypt payload helpers."""

from __future__ import annotations

import zlib

COMPRESSED_PREFIX = b"\x01Z"
RAW_PREFIX = b"\x00R"
THRESHOLD = 128


def compress_payload(data: bytes, threshold: int = THRESHOLD) -> bytes:
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("data must be bytes")
    data = bytes(data)
    if len(data) < threshold:
        return RAW_PREFIX + data
    compressed = zlib.compress(data, level=6)
    packed = COMPRESSED_PREFIX + compressed
    raw = RAW_PREFIX + data
    return packed if len(packed) < len(raw) else raw


def decompress_payload(data: bytes) -> bytes:
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("data must be bytes")
    data = bytes(data)
    if data.startswith(COMPRESSED_PREFIX):
        return zlib.decompress(data[len(COMPRESSED_PREFIX):])
    if data.startswith(RAW_PREFIX):
        return data[len(RAW_PREFIX):]
    raise ValueError("unknown payload compression prefix")
