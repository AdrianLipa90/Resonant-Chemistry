"""Connected integer relation graphs from frozen shell relation degrees."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

from .atom import ELEMENT_SYMBOLS
from .compound_shell_relations import valence_shell_profile


@dataclass(frozen=True)
class Bond:
    i: int
    j: int
    order: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class RelationGraph:
    atomic_numbers: tuple[int, ...]
    symbols: tuple[str, ...]
    target_degrees: tuple[int, ...]
    bonds: tuple[Bond, ...]
    signature: tuple
    status: str = "MODEL_DEFINED_CONNECTED_INTEGER_RELATION_GRAPH"

    def to_dict(self) -> dict:
        return {
            "atomic_numbers": list(self.atomic_numbers),
            "symbols": list(self.symbols),
            "target_degrees": list(self.target_degrees),
            "bonds": [bond.to_dict() for bond in self.bonds],
            "status": self.status,
        }


def _connected(n: int, bonds: list[Bond]) -> bool:
    adjacency = [set() for _ in range(n)]
    for bond in bonds:
        adjacency[bond.i].add(bond.j)
        adjacency[bond.j].add(bond.i)
    seen = {0}
    stack = [0]
    while stack:
        i = stack.pop()
        for j in adjacency[i]:
            if j not in seen:
                seen.add(j)
                stack.append(j)
    return len(seen) == n


def _coarse_signature(zs: tuple[int, ...], bonds: list[Bond]) -> tuple:
    neighbours: list[list[tuple[int, int]]] = [[] for _ in zs]
    for bond in bonds:
        neighbours[bond.i].append((zs[bond.j], bond.order))
        neighbours[bond.j].append((zs[bond.i], bond.order))
    return tuple(sorted((zs[i], tuple(sorted(neighbours[i]))) for i in range(len(zs))))


def _distributions(total: int, limits: list[int], pos: int = 0, prefix: tuple[int, ...] = ()):
    if pos == len(limits):
        if total == 0:
            yield prefix
        return
    for value in range(min(total, limits[pos], 3) + 1):
        yield from _distributions(total - value, limits, pos + 1, prefix + (value,))


def enumerate_relation_graphs(atomic_numbers: Iterable[int], max_results: int = 256) -> tuple[RelationGraph, ...]:
    zs = tuple(int(z) for z in atomic_numbers)
    if len(zs) < 2:
        raise ValueError("at least two atoms required")
    target = tuple(valence_shell_profile(z).relation_degree for z in zs)
    if any(degree == 0 for degree in target) or sum(target) % 2:
        return ()

    n = len(zs)
    adjacency = [[0] * n for _ in range(n)]
    remaining = list(target)
    raw: list[list[Bond]] = []

    def recurse(i: int) -> None:
        if len(raw) >= max_results * 30:
            return
        while i < n and remaining[i] == 0:
            i += 1
        if i == n:
            if any(remaining):
                return
            bonds = [Bond(a, b, adjacency[a][b]) for a in range(n) for b in range(a + 1, n) if adjacency[a][b]]
            if _connected(n, bonds):
                raw.append(bonds)
            return
        later = list(range(i + 1, n))
        if not later:
            return
        limits = [remaining[j] for j in later]
        if sum(min(3, value) for value in limits) < remaining[i]:
            return
        needed = remaining[i]
        for distribution in _distributions(needed, limits):
            if sum(distribution) != needed:
                continue
            changed: list[tuple[int, int]] = []
            for j, value in zip(later, distribution):
                if value:
                    adjacency[i][j] = adjacency[j][i] = value
                    remaining[j] -= value
                    changed.append((j, value))
            old_i = remaining[i]
            remaining[i] = 0
            if sum(remaining) % 2 == 0:
                recurse(i + 1)
            remaining[i] = old_i
            for j, value in changed:
                remaining[j] += value
                adjacency[i][j] = adjacency[j][i] = 0

    recurse(0)

    unique: dict[tuple, RelationGraph] = {}
    for bonds in raw:
        signature = _coarse_signature(zs, bonds)
        if signature not in unique:
            unique[signature] = RelationGraph(zs, tuple(ELEMENT_SYMBOLS[z] for z in zs), target, tuple(bonds), signature)
            if len(unique) >= max_results:
                break
    return tuple(unique.values())


def bond_order_multiset(graph: RelationGraph) -> tuple[int, ...]:
    return tuple(sorted((bond.order for bond in graph.bonds), reverse=True))
