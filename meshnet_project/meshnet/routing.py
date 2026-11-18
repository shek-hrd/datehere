"""Topology and shortest-path routing (local link-state computation)."""

from __future__ import annotations

from collections import deque
from typing import Dict, List, Set


class MeshTopology:
    def __init__(self) -> None:
        self.links: Dict[str, Set[str]] = {}

    def add_node(self, node_id: str) -> None:
        self.links.setdefault(node_id, set())

    def add_link(self, a: str, b: str) -> None:
        if a == b:
            return
        self.add_node(a)
        self.add_node(b)
        self.links[a].add(b)
        self.links[b].add(a)

    def remove_link(self, a: str, b: str) -> None:
        if a in self.links:
            self.links[a].discard(b)
        if b in self.links:
            self.links[b].discard(a)

    def remove_node(self, node_id: str) -> None:
        for peer in list(self.links.get(node_id, set())):
            self.links[peer].discard(node_id)
        self.links.pop(node_id, None)

    def neighbors(self, node_id: str) -> Set[str]:
        return set(self.links.get(node_id, set()))

    def route(self, src: str, dst: str) -> List[str]:
        if src not in self.links or dst not in self.links:
            raise ValueError("unknown source or destination")
        if src == dst:
            return [src]
        q = deque([src])
        prev: Dict[str, str | None] = {src: None}
        while q:
            cur = q.popleft()
            for nb in sorted(self.links.get(cur, [])):
                if nb in prev:
                    continue
                prev[nb] = cur
                if nb == dst:
                    path = [dst]
                    while prev[path[-1]] is not None:
                        path.append(prev[path[-1]])  # type: ignore[arg-type]
                    return list(reversed(path))
                q.append(nb)
        raise ValueError(f"no route from {src} to {dst}")
