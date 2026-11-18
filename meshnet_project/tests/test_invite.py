import pytest
from meshnet.invite import create_invite, verify_invite


def test_invite_roundtrip():
    token, _key = create_invite("node-a", "swift-otter", "2001:db8::1", 4242)
    info = verify_invite(token)
    assert info["node_id"] == "node-a"
    assert info["nickname"] == "swift-otter"
    assert info["host"] == "2001:db8::1"
    assert info["port"] == 4242
    assert "public_key" in info


def test_tampered_invite_rejected():
    token, _key = create_invite("node-a", "swift-otter", "2001:db8::1", 4242)
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
    with pytest.raises(ValueError):
        verify_invite(tampered)


def test_expired_invite_rejected():
    token, _key = create_invite("node-a", "swift-otter", "2001:db8::1", 4242, expires_in_s=10)
    with pytest.raises(ValueError):
        verify_invite(token, now=10**12)
