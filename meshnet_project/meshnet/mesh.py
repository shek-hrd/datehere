"""Mesh network with hash-linked common chat blockchain, hails, routes, groups, ping."""

from __future__ import annotations

import random
import threading
import time
import uuid
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set, Union

from .blockchain import MessageBlockchain
from .node import Node, generate_nickname
from .objective import HELP_TEXT, OBJECTIVE
from .routing import MeshTopology

NodeLike = Union[str, Node]


class NicknameTakenError(ValueError):
    pass


class UnknownNodeError(KeyError):
    pass


@dataclass
class PingResult:
    source: str
    destination: str
    hops: int
    path: List[str]
    latency_ms: float
    reachable: bool = True

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "destination": self.destination,
            "hops": self.hops,
            "path": list(self.path),
            "latency_ms": round(self.latency_ms, 3),
            "reachable": self.reachable,
        }


class MeshNetwork:
    def __init__(self) -> None:
        self.nodes: Dict[str, Node] = {}
        self.nick_to_id: Dict[str, str] = {}
        self.groups: Dict[str, Set[str]] = {}
        self.topology = MeshTopology()
        self.blockchain = MessageBlockchain()
        self._rng = random.Random(42)
        self._lock = threading.RLock()
        self._seen_block_messages: Set[str] = set()

    def add_node(
        self,
        nickname: Optional[str] = None,
        platform: str = "terminal",
        node_id: Optional[str] = None,
        host: Optional[str] = None,
        udp_port: Optional[int] = None,
    ) -> Node:
        with self._lock:
            nickname = nickname or generate_nickname(self._rng)
            if nickname in self.nick_to_id:
                raise NicknameTakenError(f"nickname already in use: {nickname}")
            node = Node(
                nickname=nickname,
                platform=platform,
                node_id=node_id or f"node-{uuid.uuid4().hex[:10]}",
                host=host,
                udp_port=udp_port,
            )
            self.nodes[node.node_id] = node
            self.nick_to_id[nickname] = node.node_id
            self.topology.add_node(node.node_id)
            return node

    def resolve(self, identifier: NodeLike) -> Node:
        if isinstance(identifier, Node):
            return identifier
        node_id = self.nick_to_id.get(identifier, identifier)
        if node_id not in self.nodes:
            raise UnknownNodeError(identifier)
        return self.nodes[node_id]

    def connect(self, a: NodeLike, b: NodeLike) -> None:
        with self._lock:
            na, nb = self.resolve(a), self.resolve(b)
            if na.node_id == nb.node_id:
                return
            na.neighbors.add(nb.node_id)
            nb.neighbors.add(na.node_id)
            self.topology.add_link(na.node_id, nb.node_id)

    def disconnect(self, a: NodeLike, b: NodeLike) -> None:
        with self._lock:
            na, nb = self.resolve(a), self.resolve(b)
            na.neighbors.discard(nb.node_id)
            nb.neighbors.discard(na.node_id)
            self.topology.remove_link(na.node_id, nb.node_id)

    def remove_node(self, identifier: NodeLike) -> None:
        with self._lock:
            node = self.resolve(identifier)
            nid = node.node_id
            for other in list(node.neighbors):
                if other in self.nodes:
                    self.nodes[other].neighbors.discard(nid)
            self.topology.remove_node(nid)
            for members in list(self.groups.values()):
                members.discard(nid)
            for name in [n for n, m in self.groups.items() if not m]:
                self.groups.pop(name, None)
            self.nick_to_id.pop(node.nickname, None)
            self.nodes.pop(nid, None)

    def show_help(self) -> str:
        return HELP_TEXT

    @property
    def objective(self) -> str:
        return OBJECTIVE

    def _record_chain(self, message: dict) -> None:
        mid = message.get("id")
        if not mid or mid in self._seen_block_messages:
            return
        if message.get("kind") in {"chat", "group_chat", "system"}:
            self.blockchain.append(message)
            self._seen_block_messages.add(mid)

    def _deliver_along_path(self, path_ids: List[str], message: dict) -> dict:
        for nid in path_ids:
            self.nodes[nid].receive(message)
        self._record_chain(message)
        return message

    def broadcast_system_message(self, source: NodeLike, text: str, room: str = "common") -> dict:
        with self._lock:
            src = self.resolve(source)
            message = {
                "id": uuid.uuid4().hex,
                "kind": "system",
                "source": src.nickname,
                "source_id": src.node_id,
                "destination": "*",
                "room": room,
                "payload": text,
                "created_at": time.time(),
                "path": [src.nickname],
                "hops": 0,
            }
            for node in self.nodes.values():
                node.receive(message)
            self._record_chain(message)
            return message

    def hail(self, source: NodeLike) -> dict:
        node = self.resolve(source)
        text = (
            f"HAIL {node.nickname} joined the mesh. "
            f"platform={node.platform}; node_id={node.node_id}; "
            f"udp_port={node.udp_port if node.udp_port is not None else 'unannounced'}; "
            f"peers={len(node.neighbors)}."
        )
        return self.broadcast_system_message(node, text)

    def route_ids(self, src: NodeLike, dst: NodeLike) -> List[str]:
        s = self.resolve(src).node_id
        d = self.resolve(dst).node_id
        return self.topology.route(s, d)

    def route_nicknames(self, src: NodeLike, dst: NodeLike) -> List[str]:
        return [self.nodes[nid].nickname for nid in self.route_ids(src, dst)]

    def render_route(self, src: NodeLike, dst: NodeLike) -> str:
        path = self.route_nicknames(src, dst)
        return " -> ".join(path) if path else "(no route)"

    def send_chat(self, source: NodeLike, destination: NodeLike, text: str) -> dict:
        with self._lock:
            src = self.resolve(source)
            dst = self.resolve(destination)
            path_ids = self.route_ids(src, dst)
            path_names = [self.nodes[nid].nickname for nid in path_ids]
            message = {
                "id": uuid.uuid4().hex,
                "kind": "chat",
                "source": src.nickname,
                "source_id": src.node_id,
                "destination": dst.nickname,
                "destination_id": dst.node_id,
                "room": "common",
                "payload": text,
                "created_at": time.time(),
                "path": path_names,
                "hops": max(0, len(path_ids) - 1),
            }
            return self._deliver_along_path(path_ids, message)

    def broadcast_common_chat(self, source: NodeLike, text: str) -> dict:
        """Send a common-chat message from source to all reachable peers (fan-out best-effort)."""
        with self._lock:
            src = self.resolve(source)
            message = {
                "id": uuid.uuid4().hex,
                "kind": "chat",
                "source": src.nickname,
                "source_id": src.node_id,
                "destination": "*",
                "room": "common",
                "payload": text,
                "created_at": time.time(),
                "path": [src.nickname],
                "hops": 0,
            }
            for node in self.nodes.values():
                node.receive(message)
            self._record_chain(message)
            return message

    def create_group(self, name: str, members: Iterable[NodeLike]) -> Set[str]:
        with self._lock:
            member_ids = {self.resolve(m).node_id for m in members}
            if len(member_ids) < 2:
                raise ValueError("a group needs at least two members")
            self.groups.setdefault(name, set()).update(member_ids)
            for mid in self.groups[name]:
                self.nodes[mid].groups.add(name)
            return set(self.groups[name])

    def join_group(self, name: str, member: NodeLike) -> None:
        with self._lock:
            node = self.resolve(member)
            self.groups.setdefault(name, set()).add(node.node_id)
            node.groups.add(name)

    def leave_group(self, name: str, member: NodeLike) -> None:
        with self._lock:
            node = self.resolve(member)
            if name in self.groups:
                self.groups[name].discard(node.node_id)
                if not self.groups[name]:
                    self.groups.pop(name, None)
            node.groups.discard(name)

    def send_group_chat(self, source: NodeLike, room: str, text: str) -> List[dict]:
        with self._lock:
            src = self.resolve(source)
            if room not in self.groups or src.node_id not in self.groups[room]:
                raise ValueError(f"{src.nickname} is not a member of group {room}")
            delivered: List[dict] = []
            for dst_id in sorted(self.groups[room]):
                if dst_id == src.node_id:
                    continue
                try:
                    path_ids = self.route_ids(src, dst_id)
                except Exception:
                    continue
                path_names = [self.nodes[nid].nickname for nid in path_ids]
                message = {
                    "id": uuid.uuid4().hex,
                    "kind": "group_chat",
                    "source": src.nickname,
                    "source_id": src.node_id,
                    "destination": self.nodes[dst_id].nickname,
                    "destination_id": dst_id,
                    "room": room,
                    "payload": text,
                    "created_at": time.time(),
                    "path": path_names,
                    "hops": max(0, len(path_ids) - 1),
                }
                self._deliver_along_path(path_ids, message)
                delivered.append(message)
            return delivered

    def ping(self, source: NodeLike, destination: NodeLike) -> PingResult:
        src = self.resolve(source)
        dst = self.resolve(destination)
        path_ids = self.route_ids(src, dst)
        path_names = [self.nodes[nid].nickname for nid in path_ids]
        hops = max(0, len(path_ids) - 1)
        base = 3.0
        per_hop_rtt = 8.0
        jitter = (hash((src.node_id, dst.node_id, hops, len(self.nodes))) % 13) * 0.25
        latency_ms = base + hops * per_hop_rtt + jitter
        return PingResult(source=src.nickname, destination=dst.nickname, hops=hops, path=path_names, latency_ms=latency_ms)

    def snapshot(self) -> dict:
        with self._lock:
            nodes = [
                {
                    "id": n.node_id,
                    "nickname": n.nickname,
                    "platform": n.platform,
                    "host": n.host,
                    "udp_port": n.udp_port,
                    "channels": list(n.channels),
                    "peers": [self.nodes[p].nickname for p in sorted(n.neighbors) if p in self.nodes],
                    "groups": sorted(n.groups),
                }
                for n in self.nodes.values()
            ]
            links = []
            seen = set()
            for n in self.nodes.values():
                for p in n.neighbors:
                    if p in self.nodes:
                        a, b = sorted([n.nickname, self.nodes[p].nickname])
                        key = (a, b)
                        if key in seen:
                            continue
                        seen.add(key)
                        links.append({"source": a, "target": b})
            groups = {
                name: sorted(self.nodes[mid].nickname for mid in members if mid in self.nodes)
                for name, members in self.groups.items()
            }
            return {
                "nodes": nodes,
                "links": links,
                "groups": groups,
                "chain": self.blockchain.to_list(),
                "chain_head": self.blockchain.head["hash"],
                "chain_valid": self.blockchain.verify(),
            }
