"""Encrypted, replay-protected UDP envelopes (compress-before-encrypt)."""

from __future__ import annotations

import json
import struct
import time
from typing import Any, Dict, Optional, Set, Tuple

from nacl.secret import SecretBox
from nacl.utils import random as nacl_random

from .compression import compress_payload, decompress_payload

MAGIC = b"MN1"
VERSION = 1


def generate_session_key() -> bytes:
    return nacl_random(SecretBox.KEY_SIZE)


def pack(
    sender: str,
    recipient: str,
    stream_id: int,
    sequence: int,
    payload: bytes,
    key: bytes,
    flags: int = 0,
) -> bytes:
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("payload must be bytes")
    header = {
        "v": VERSION,
        "sender": sender,
        "recipient": recipient,
        "stream": int(stream_id),
        "seq": int(sequence),
        "flags": int(flags),
        "ts": time.time(),
    }
    header_bytes = json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
    box = SecretBox(key)
    nonce = nacl_random(SecretBox.NONCE_SIZE)
    plaintext = compress_payload(bytes(payload))
    ciphertext = box.encrypt(plaintext, nonce).ciphertext
    return MAGIC + struct.pack("!H", len(header_bytes)) + header_bytes + nonce + ciphertext


def unpack(
    raw: bytes,
    key: bytes,
    seen: Optional[Set[Tuple[str, int]]] = None,
) -> Dict[str, Any]:
    if not isinstance(raw, (bytes, bytearray)):
        raise TypeError("raw must be bytes")
    raw = bytes(raw)
    if len(raw) < 5 + SecretBox.NONCE_SIZE:
        raise ValueError("envelope too short")
    if raw[:3] != MAGIC:
        raise ValueError("invalid envelope magic")
    header_len = struct.unpack("!H", raw[3:5])[0]
    start = 5
    end = start + header_len
    if end + SecretBox.NONCE_SIZE > len(raw):
        raise ValueError("truncated envelope")
    try:
        header = json.loads(raw[start:end].decode("utf-8"))
    except Exception as exc:
        raise ValueError(f"invalid envelope header: {exc}") from exc

    if header.get("v") != VERSION:
        raise ValueError("unsupported envelope version")

    nonce = raw[end:end + SecretBox.NONCE_SIZE]
    ciphertext = raw[end + SecretBox.NONCE_SIZE:]
    box = SecretBox(key)
    try:
        plaintext = box.decrypt(ciphertext, nonce)
    except Exception as exc:
        raise ValueError(f"envelope authentication/decryption failed: {exc}") from exc

    replay_key = (str(header.get("sender")), int(header.get("seq", -1)))
    if seen is not None:
        if replay_key in seen:
            raise ValueError("replayed envelope sequence")
        seen.add(replay_key)

    try:
        payload = decompress_payload(bytes(plaintext))
    except Exception as exc:
        raise ValueError(f"invalid envelope payload compression: {exc}") from exc

    return {
        "version": header["v"],
        "sender": header["sender"],
        "recipient": header["recipient"],
        "stream": header["stream"],
        "sequence": header["seq"],
        "flags": header.get("flags", 0),
        "timestamp": header.get("ts"),
        "payload": payload,
    }
