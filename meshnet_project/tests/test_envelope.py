import pytest
from meshnet.envelope import generate_session_key, pack, unpack


def test_envelope_roundtrip():
    key = generate_session_key()
    raw = pack("node-a", "node-b", 1, 0, b"hello mesh", key)
    msg = unpack(raw, key)
    assert msg["sender"] == "node-a"
    assert msg["recipient"] == "node-b"
    assert msg["payload"] == b"hello mesh"
    assert msg["sequence"] == 0


def test_replay_rejected():
    key = generate_session_key()
    raw = pack("node-a", "node-b", 1, 7, b"hello", key)
    seen = set()
    unpack(raw, key, seen=seen)
    with pytest.raises(ValueError):
        unpack(raw, key, seen=seen)


def test_tampered_ciphertext_rejected():
    key = generate_session_key()
    raw = bytearray(pack("node-a", "node-b", 1, 1, b"secret", key))
    raw[-1] ^= 0x01
    with pytest.raises(ValueError):
        unpack(bytes(raw), key)
