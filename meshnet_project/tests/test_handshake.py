from nacl.signing import SigningKey

from meshnet.envelope import generate_session_key  # noqa: F401 (sanity import context)
from meshnet.envelope import pack, unpack
from meshnet.handshake import (
    derive_session_key,
    exchange_private_key,
    exchange_public_key_b64,
    exchange_public_key_from_signing,
    exchange_public_key_from_verify,
)
from meshnet.invite import create_invite, verify_invite


def test_curve25519_keys_consistent_with_identity():
    sk = SigningKey.generate()
    assert exchange_private_key(sk).encode()
    assert bytes(exchange_public_key_from_signing(sk)) == bytes(
        exchange_public_key_from_verify(sk.verify_key)
    )
    assert bytes(exchange_public_key_from_verify(sk.verify_key.encode())) == bytes(
        exchange_public_key_from_signing(sk)
    )


def test_derive_session_key_symmetric_and_peer_specific():
    sk_a = SigningKey.generate()
    sk_b = SigningKey.generate()
    sk_c = SigningKey.generate()

    key_ab = derive_session_key(sk_a, sk_b.verify_key)
    key_ba = derive_session_key(sk_b, sk_a.verify_key)
    key_ac = derive_session_key(sk_a, sk_c.verify_key)

    assert key_ab == key_ba
    assert isinstance(key_ab, bytes) and len(key_ab) == 32
    assert key_ab != key_ac


def test_invite_carries_exchange_key_and_derives_shared_session():
    token_a, sk_a = create_invite("node-a", "alpha", "2001:db8::1", 41001)
    token_b, sk_b = create_invite("node-b", "beta", "2001:db8::2", 41002)

    info_a = verify_invite(token_a)
    info_b = verify_invite(token_b)

    assert info_a["public_key"]
    assert info_a["exchange_public_key"] == exchange_public_key_b64(sk_a)
    assert info_b["exchange_public_key"] == exchange_public_key_b64(sk_b)

    # Each side derives the same session key from its own signing key and peer's verified identity key.
    key_a = derive_session_key(sk_a, info_b["public_key"])
    key_b = derive_session_key(sk_b, info_a["public_key"])
    assert key_a == key_b

    # Derived key works end-to-end with authenticated, compression-encrypted envelopes.
    raw = pack("node-a", "node-b", 1, 0, b"handshake-payload", key_a)
    msg = unpack(raw, key_b)
    assert msg["payload"] == b"handshake-payload"
    assert msg["sender"] == "node-a"
