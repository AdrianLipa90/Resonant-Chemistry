"""Minimal three-centre augmentation for shell-relation graphs.

The v0.3 two-centre graph gate is kept intact.  This module introduces one
additional candidate primitive only when a connected two-centre graph cannot
satisfy the frozen shell relation degrees.

To avoid floating-point bookkeeping, relation load is counted in half-units:

* an atom with relation degree d carries target load 2*d;
* a two-centre bond of integer order b consumes 2*b half-units at each end;
* a symmetric three-centre bridge (outer--bridge--outer) consumes 1,2,1
  half-units respectively.

The 1:2:1 load is a representation rule for a symmetric 3c candidate, not a
claim about literal fractional electrons or bond energy.  Candidate solutions
are searched in increasing number of three-centre bridges.  Therefore the
ordinary two-centre model wins whenever it already closes the graph, and the
smallest augmentation that restores closure is selected otherwise.

Bridge eligibility is shell-defined rather than element-labelled: the bridge
centre must have relation degree one and each outer centre degree at least two.
Each bridge centre may participate in at most one three-centre primitive in
v0.4.  Transition-metal and closed-shell limitations inherited from
``valence_shell_profile`` still fail closed.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import combinations
from typing import Iterable

from .atom import ELEMENT_SYMBOLS
from .compound_shell_relations import valence_shell_profile
from .relation_graph import Bond


@dataclass(frozen=True)
class ThreeCentreBridge:
    outer_a: int
    bridge: int
    outer_b: int
    outer_half_units: int = 1
    bridge_half_units: int = 2
    status: str = "MODEL_DEFINED_SYMMETRIC_3C_BRIDGE_CANDIDATE"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class AugmentedRelationGraph:
    atomic_numbers: tuple[int, ...]
    symbols: tuple[str, ...]
    target_relation_degrees: tuple[int, ...]
    pair_bonds: tuple[Bond, ...]
    three_centre_bridges: tuple[ThreeCentreBridge, ...]
    augmentation_order: int
    signature: tuple
    status: str = "MODEL_DEFINED_MINIMAL_3C_AUGMENTED_RELATION_GRAPH"

    def to_dict(self) -> dict:
        return {
            "atomic_numbers": list(self.atomic_numbers),
            "symbols": list(self.symbols),
            "target_relation_degrees": list(self.target_relation_degrees),
            "pair_bonds": [bond.to_dict() for bond in self.pair_bonds],
            "three_centre_bridges": [edge.to_dict() for edge in self.three_centre_bridges],
            "augmentation_order": self.augmentation_order,
            "status": self.status,
        }


def relation_load_half_units(graph: AugmentedRelationGraph) -> tuple[int, ...]:
    """Return the realized relation load on every atomic centre."""
    load = [0 for _ in graph.atomic_numbers]
    for bond in graph.pair_bonds:
        value = 2 * bond.order
        load[bond.i] += value
        load[bond.j] += value
    for edge in graph.three_centre_bridges:
        load[edge.outer_a] += edge.outer_half_units
        load[edge.bridge] += edge.bridge_half_units
        load[edge.outer_b] += edge.outer_half_units
    return tuple(load)


def _combined_connected(
    n: int,
    pair_bonds: tuple[Bond, ...],
    bridges: tuple[ThreeCentreBridge, ...],
) -> bool:
    adjacency = [set() for _ in range(n)]
    for bond in pair_bonds:
        adjacency[bond.i].add(bond.j)
        adjacency[bond.j].add(bond.i)
    for edge in bridges:
        vertices = (edge.outer_a, edge.bridge, edge.outer_b)
        for left, right in combinations(vertices, 2):
            adjacency[left].add(right)
            adjacency[right].add(left)

    seen = {0}
    stack = [0]
    while stack:
        i = stack.pop()
        for j in adjacency[i]:
            if j not in seen:
                seen.add(j)
                stack.append(j)
    return len(seen) == n


def _coarse_signature(
    zs: tuple[int, ...],
    pair_bonds: tuple[Bond, ...],
    bridges: tuple[ThreeCentreBridge, ...],
) -> tuple:
    local = []
    for i, z in enumerate(zs):
        pair_environment: list[tuple] = []
        for bond in pair_bonds:
            if bond.i == i:
                pair_environment.append(("2c", zs[bond.j], bond.order))
            elif bond.j == i:
                pair_environment.append(("2c", zs[bond.i], bond.order))

        bridge_environment: list[tuple] = []
        for edge in bridges:
            if edge.bridge == i:
                bridge_environment.append(
                    (
                        "3c_bridge",
                        tuple(sorted((zs[edge.outer_a], zs[edge.outer_b]))),
                    )
                )
            elif edge.outer_a == i:
                bridge_environment.append(("3c_outer", zs[edge.bridge], zs[edge.outer_b]))
            elif edge.outer_b == i:
                bridge_environment.append(("3c_outer", zs[edge.bridge], zs[edge.outer_a]))

        local.append(
            (
                z,
                tuple(sorted(pair_environment)),
                tuple(sorted(bridge_environment)),
            )
        )
    return tuple(sorted(local))


def _distributions(
    total: int,
    limits: list[int],
    pos: int = 0,
    prefix: tuple[int, ...] = (),
):
    if pos == len(limits):
        if total == 0:
            yield prefix
        return
    for value in range(min(total, limits[pos], 3) + 1):
        yield from _distributions(
            total - value,
            limits,
            pos + 1,
            prefix + (value,),
        )


def _pair_assignments_from_half_residual(
    residual_half_units: tuple[int, ...],
    max_results: int,
) -> tuple[tuple[Bond, ...], ...]:
    """Enumerate ordinary pair-bond assignments for an even half-unit residual."""
    if any(value < 0 or value % 2 for value in residual_half_units):
        return ()

    n = len(residual_half_units)
    remaining = [value // 2 for value in residual_half_units]
    adjacency = [[0] * n for _ in range(n)]
    raw: list[tuple[Bond, ...]] = []

    def recurse(i: int) -> None:
        if len(raw) >= max_results * 30:
            return
        while i < n and remaining[i] == 0:
            i += 1
        if i == n:
            if any(remaining):
                return
            raw.append(
                tuple(
                    Bond(a, b, adjacency[a][b])
                    for a in range(n)
                    for b in range(a + 1, n)
                    if adjacency[a][b]
                )
            )
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
    return tuple(raw)


def _bridge_candidates(
    degrees: tuple[int, ...],
) -> tuple[ThreeCentreBridge, ...]:
    out: list[ThreeCentreBridge] = []
    n = len(degrees)
    for bridge in range(n):
        if degrees[bridge] != 1:
            continue
        outers = [
            i for i in range(n) if i != bridge and degrees[i] >= 2
        ]
        for outer_a, outer_b in combinations(outers, 2):
            out.append(
                ThreeCentreBridge(
                    outer_a=min(outer_a, outer_b),
                    bridge=bridge,
                    outer_b=max(outer_a, outer_b),
                )
            )
    return tuple(out)


def enumerate_minimal_augmented_graphs(
    atomic_numbers: Iterable[int],
    max_results: int = 256,
) -> tuple[AugmentedRelationGraph, ...]:
    """Return the smallest 3c augmentation that closes the relation graph.

    Search begins at augmentation order zero.  Consequently ordinary 2c
    solutions are returned unchanged whenever they exist.  Only if no such
    graph exists are one, two, ... bridge primitives admitted.
    """
    zs = tuple(int(z) for z in atomic_numbers)
    if len(zs) < 2:
        raise ValueError("at least two atoms required")
    if max_results < 1:
        raise ValueError("max_results must be positive")

    profiles = tuple(valence_shell_profile(z) for z in zs)
    degrees = tuple(profile.relation_degree for profile in profiles)
    target_half_units = tuple(2 * degree for degree in degrees)

    # A truly closed centre still cannot be activated by this gate.  KrF2,
    # for example, remains a separate excitation/polarization falsifier.
    if any(degree == 0 for degree in degrees):
        return ()

    candidates = _bridge_candidates(degrees)
    n = len(zs)

    for augmentation_order in range(len(candidates) + 1):
        unique: dict[tuple, AugmentedRelationGraph] = {}

        for selected in combinations(candidates, augmentation_order):
            # v0.4 permits each degree-one centre to bridge at most one pair.
            bridge_indices = [edge.bridge for edge in selected]
            if len(set(bridge_indices)) != len(bridge_indices):
                continue

            residual = list(target_half_units)
            feasible = True
            for edge in selected:
                residual[edge.outer_a] -= edge.outer_half_units
                residual[edge.bridge] -= edge.bridge_half_units
                residual[edge.outer_b] -= edge.outer_half_units
                if min(residual) < 0:
                    feasible = False
                    break
            if not feasible or any(value % 2 for value in residual):
                continue

            for pair_bonds in _pair_assignments_from_half_residual(
                tuple(residual), max_results=max_results
            ):
                selected_tuple = tuple(selected)
                if not _combined_connected(n, pair_bonds, selected_tuple):
                    continue

                signature = _coarse_signature(zs, pair_bonds, selected_tuple)
                graph = AugmentedRelationGraph(
                    atomic_numbers=zs,
                    symbols=tuple(ELEMENT_SYMBOLS[z] for z in zs),
                    target_relation_degrees=degrees,
                    pair_bonds=pair_bonds,
                    three_centre_bridges=selected_tuple,
                    augmentation_order=augmentation_order,
                    signature=signature,
                )

                expected_load = target_half_units
                if relation_load_half_units(graph) != expected_load:
                    raise RuntimeError("augmented relation-load conservation failed")

                unique.setdefault(signature, graph)
                if len(unique) >= max_results:
                    break
            if len(unique) >= max_results:
                break

        if unique:
            return tuple(unique.values())

    return ()
