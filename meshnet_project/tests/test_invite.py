import pytest
from meshnet.invite import create_invite, verify_invite


def test_invite_roundtrip():
    token, key = create_invite("node-a", "swift-otter", "2001:db8::1", 4242)
    info = verify_invite(token)
    assert info["node_id"] == "node-a"
    assert info["nickname"] == "swift-otter"
    assert info["host"] == "2001:db8::1"
    assert info["port"] == 4242
    assert "public_key" in info
    assert "exchange_public_key" in info
    import base64
    expected_x25519 = base64.urlsafe_b64encode(bytes(key.verify_key.to_curve25519_public_key())).decode("ascii").rstrip("=")
    assert info["exchange_public_key"] == expected_x25519


def test_tampered_invite_rejected():
    token, _key = create_invite("node-a", "swift-otter", "2001:db8::1", 4242)
    # Tamper signature bytes deterministically (avoid base64url trailing padding-bit ambiguity).
    prefix, payload_b64, sig_b64 = token.split(".", 2)
    i = len(sig_b64) // 2
    replacement = "A" if sig_b64[i] != "A" else "B"
    tampered_sig = sig_b64[:i] + replacement + sig_b64[i + 1:]
    tampered = f"{prefix}.{payload_b64}.{tampered_sig}"
    with pytest.raises(ValueError):
        verify_invite(tampered)


def test_expired_invite_rejected():
    token, _key = create_invite("node-a", "swift-otter", "2001:db8::1", 4242, expires_in_s=10)
    with pytest.raises(ValueError):
        verify_invite(token, now=10**12)
