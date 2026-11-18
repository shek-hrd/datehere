"""Node model."""

from __future__ import annotations

import random
import string
import uuid
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Optional, Set

_ADJECTIVES = ("swift", "quiet", "bright", "calm", "bold", "clever", "lunar", "solar", "sensei")
_NOUNS = ("otter", "falcon", "cedar", "river", "comet", "lynx", "ember", "maple", "node")

PLATFORM_CHANNELS = {
    "android": ("wifi", "bluetooth", "proximity", "web"),
    "bash": ("wifi", "bluetooth", "web"),
    "terminal": ("wifi", "bluetooth", "web"),
    "web": ("web",),
}


def generate_nickname(rng: Optional[random.Random] = None) -> str:
    rng = rng or random.Random()
    suffix = "".join(rng.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{rng.choice(_ADJECTIVES)}-{rng.choice(_NOUNS)}-{suffix}"


@dataclass
class Node:
    nickname: str
    platform: str = "terminal"
    node_id: str = field(default_factory=lambda: f"node-{uuid.uuid4().hex[:10]}")
    host: Optional[str] = None
    udp_port: Optional[int] = None
    channels: tuple[str, ...] = field(default_factory=tuple)
    neighbors: Set[str] = field(default_factory=set)
    groups: Set[str] = field(default_factory=set)
    inbox: Deque[dict] = field(default_factory=deque)
    public_log: List[dict] = field(default_factory=list)
    meta: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.channels:
            self.channels = PLATFORM_CHANNELS.get(self.platform, ("wifi", "web"))

    def receive(self, message: dict) -> None:
        msg = dict(message)
        self.inbox.append(msg)
        if msg.get("kind") in {"chat", "group_chat", "system"}:
            self.public_log.append(msg)
