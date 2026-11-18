"""Append-only hash-linked blockchain of common chat messages."""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, List, Optional


def _canonical(data: dict) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_hash(block_core: dict) -> str:
    return hashlib.sha256(_canonical(block_core).encode("utf-8")).hexdigest()


class MessageBlockchain:
    def __init__(self) -> None:
        self.chain: List[Dict[str, Any]] = []
        self._create_genesis()

    def _create_genesis(self) -> None:
        core = {
            "index": 0,
            "timestamp": 0.0,
            "prev_hash": "0" * 64,
            "message_id": "genesis",
            "kind": "genesis",
            "source": "system",
            "destination": "*",
            "room": "common",
            "payload": "MeshNet common chat blockchain genesis",
            "path": [],
            "hops": 0,
        }
        block = dict(core)
        block["hash"] = compute_hash(core)
        self.chain.append(block)

    @property
    def head(self) -> Dict[str, Any]:
        return self.chain[-1]

    def append(self, message: Dict[str, Any]) -> Dict[str, Any]:
        prev = self.head
        core = {
            "index": len(self.chain),
            "timestamp": float(message.get("created_at", time.time())),
            "prev_hash": prev["hash"],
            "message_id": message.get("id", ""),
            "kind": message.get("kind", "chat"),
            "source": message.get("source", "?"),
            "destination": message.get("destination", "*"),
            "room": message.get("room", "common"),
            "payload": message.get("payload", ""),
            "path": list(message.get("path", [])),
            "hops": int(message.get("hops", 0) or 0),
        }
        block = dict(core)
        block["hash"] = compute_hash(core)
        self.chain.append(block)
        return block

    def to_list(self) -> List[Dict[str, Any]]:
        return [dict(b) for b in self.chain]

    def verify(self) -> bool:
        if not self.chain:
            return False
        # verify genesis hash and links
        for i, block in enumerate(self.chain):
            core = {k: block[k] for k in [
                "index","timestamp","prev_hash","message_id","kind","source","destination","room","payload","path","hops"
            ]}
            if compute_hash(core) != block.get("hash"):
                return False
            if i == 0:
                if block.get("prev_hash") != "0" * 64:
                    return False
            else:
                if block.get("prev_hash") != self.chain[i-1].get("hash"):
                    return False
        return True
