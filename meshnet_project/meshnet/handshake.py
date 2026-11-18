"""Handshake and key-agreement helpers for MeshNet peer sessions.

Bridges signed node identities (Ed25519 invites/intros) to symmetric session
keys (X25519/NaCl Box shared secret) for compression-encrypted envelopes.
"""

from __future__ import annotations

import base64
from typing import Union

from nacl.public import Box, PrivateKey, PublicKey
from nacl.signing import SigningKey, VerifyKey


def _b64e(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64d(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)


VerifyKeyLike = Union[VerifyKey, SigningKey, str, bytes]


def _as_verify_key(peer: VerifyKeyLike) -> VerifyKey:
    if isinstance(peer, VerifyKey):
        return peer
    if isinstance(peer, SigningKey):
        return peer.verify_key
    if isinstance(peer, str):
        return VerifyKey(_b64d(peer))
    if isinstance(peer, (bytes, bytearray)):
        return VerifyKey(bytes(peer))
    raise TypeError(f"unsupported peer verify key type: {type(peer)!r}")


def exchange_private_key(signing_key: SigningKey) -> PrivateKey:
    """Derive the X25519 private key corresponding to an Ed25519 signing key."""
    return signing_key.to_curve25519_private_key()


def exchange_public_key_from_signing(signing_key: SigningKey) -> PublicKey:
    """Derive the X25519 public key corresponding to an Ed25519 signing key."""
    return signing_key.verify_key.to_curve25519_public_key()


def exchange_public_key_from_verify(verify_key: VerifyKeyLike) -> PublicKey:
    """Derive the X25519 public key corresponding to an Ed25519 verify key."""
    return _as_verify_key(verify_key).to_curve25519_public_key()


def exchange_public_key_b64(signing_key: SigningKey) -> str:
    """Return the X25519 exchange public key (base64url, no padding) for a signing key."""
    return _b64e(bytes(exchange_public_key_from_signing(signing_key)))


def derive_session_key(local_signing_key: SigningKey, peer_verify_key: VerifyKeyLike) -> bytes:
    """Derive a symmetric session key for (local, peer) using X25519 DH.

    The result is the NaCl Box shared key (32 bytes), suitable for SecretBox
    envelope encryption. Derivation is symmetric: both peers compute the same
    key when given their own signing key and the other's verify key.
    """
    priv = exchange_private_key(local_signing_key)
    pub = exchange_public_key_from_verify(peer_verify_key)
    return Box(priv, pub).shared_key()
