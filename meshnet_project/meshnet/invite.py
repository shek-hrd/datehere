"""Signed invitation tokens for slow/contact bootstrap (QR/NFC/BLE/paste)."""

from __future__ import annotations

import base64
import json
import time
import uuid
from typing import Any, Dict, Optional, Tuple

from nacl.encoding import RawEncoder
from nacl.exceptions import BadSignatureError
from nacl.signing import SigningKey, VerifyKey

PREFIX = "MESH1"


def _b64e(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64d(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)


def generate_signing_key() -> SigningKey:
    return SigningKey.generate()


def public_key_b64(signing_key: SigningKey) -> str:
    return _b64e(signing_key.verify_key.encode(encoder=RawEncoder))


def create_invite(
    node_id: str,
    nickname: str,
    host: str,
    port: int,
    signing_key: Optional[SigningKey] = None,
    expires_in_s: Optional[int] = None,
) -> Tuple[str, SigningKey]:
    """Create a signed invite token. Returns (token, signing_key)."""
    signing_key = signing_key or generate_signing_key()
    payload: Dict[str, Any] = {
        "node_id": node_id,
        "nickname": nickname,
        "host": host,
        "port": int(port),
        "public_key": public_key_b64(signing_key),
        "nonce": uuid.uuid4().hex,
        "issued_at": int(time.time()),
    }
    if expires_in_s is not None:
        payload["expires_at"] = payload["issued_at"] + int(expires_in_s)

    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    signature = signing_key.sign(payload_bytes).signature
    token = f"{PREFIX}.{_b64e(payload_bytes)}.{_b64e(signature)}"
    return token, signing_key


def verify_invite(token: str, now: Optional[int] = None) -> Dict[str, Any]:
    """Verify a signed invite token and return its payload."""
    try:
        prefix, payload_b64, sig_b64 = token.split(".", 2)
        if prefix != PREFIX:
            raise ValueError("unsupported invite prefix")
        payload_bytes = _b64d(payload_b64)
        signature = _b64d(sig_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))
    except Exception as exc:
        raise ValueError(f"malformed invite token: {exc}") from exc

    required = {"node_id", "nickname", "host", "port", "public_key", "nonce", "issued_at"}
    if not required.issubset(payload.keys()):
        raise ValueError("invite payload missing required fields")

    try:
        verify_key = VerifyKey(_b64d(payload["public_key"]))
        verify_key.verify(payload_bytes, signature)
    except BadSignatureError as exc:
        raise ValueError("invite signature verification failed") from exc
    except Exception as exc:
        raise ValueError(f"invalid invite public key/signature: {exc}") from exc

    if "expires_at" in payload:
        current = int(time.time()) if now is None else int(now)
        if current > int(payload["expires_at"]):
            raise ValueError("invite token expired")

    payload["port"] = int(payload["port"])
    return payload
