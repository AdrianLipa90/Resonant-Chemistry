"""Gauge-clean graph holonomy primitives for Resonant Chemistry.

This module implements the mathematical control layer only. It does not bind
chemical graph holonomy to PhaseNav/TIR semantic holonomy.
"""

from __future__ import annotations

import cmath
import math
from collections import deque
from typing import Iterable, Sequence

import numpy as np


class HolonomyGraphError(ValueError):
    pass


def _check_vertex_count(num_vertices: int) -> int:
    if not isinstance(num_vertices, int) or num_vertices <= 0:
        raise HolonomyGraphError("num_vertices must be a positive integer")
    return num_vertices


def _check_edges(
    num_vertices: int, edges: Sequence[tuple[int, int]]
) -> tuple[tuple[int, int], ...]:
    n = _check_vertex_count(num_vertices)
    out: list[tuple[int, int]] = []
    for edge in edges:
        if len(edge) != 2:
            raise HolonomyGraphError("each edge must have two endpoints")
        i, j = int(edge[0]), int(edge[1])
        if i == j:
            raise HolonomyGraphError("self-loops are not supported in v0.1")
        if not (0 <= i < n and 0 <= j < n):
            raise HolonomyGraphError("edge endpoint out of range")
        out.append((i, j))
    return tuple(out)


def connected_components(
    num_vertices: int, edges: Sequence[tuple[int, int]]
) -> int:
    n = _check_vertex_count(num_vertices)
    checked = _check_edges(n, edges)
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i, j in checked:
        union(i, j)
    return len({find(i) for i in range(n)})


def cycle_rank(num_vertices: int, edges: Sequence[tuple[int, int]]) -> int:
    """Return beta_1 = E - V + C for an undirected finite graph."""

    n = _check_vertex_count(num_vertices)
    checked = _check_edges(n, edges)
    return len(checked) - n + connected_components(n, checked)


def gauge_transform_phases(
    phases: Sequence[float],
    edges: Sequence[tuple[int, int]],
    chi: Sequence[float],
) -> np.ndarray:
    """Apply theta_ij -> theta_ij + chi_j - chi_i."""

    if len(phases) != len(edges):
        raise HolonomyGraphError("phases and edges must have equal length")
    if not edges:
        return np.asarray(phases, dtype=float)
    n = max(max(i, j) for i, j in edges) + 1
    if len(chi) != n:
        raise HolonomyGraphError("chi must contain one phase per graph vertex")
    checked = _check_edges(n, edges)
    p = np.asarray(phases, dtype=float)
    c = np.asarray(chi, dtype=float)
    if not np.all(np.isfinite(p)) or not np.all(np.isfinite(c)):
        raise HolonomyGraphError("phases and chi must be finite")
    return np.asarray(
        [theta + c[j] - c[i] for theta, (i, j) in zip(p, checked)],
        dtype=float,
    )


def oriented_cycle_phase(
    phases: Sequence[float],
    signed_edge_indices: Iterable[tuple[int, int]],
) -> float:
    """Return the signed loop phase for a declared oriented cycle.

    Each tuple is (edge_index, orientation) with orientation +1 or -1.
    """

    p = np.asarray(phases, dtype=float)
    if not np.all(np.isfinite(p)):
        raise HolonomyGraphError("phases must be finite")
    total = 0.0
    for edge_index, orientation in signed_edge_indices:
        if orientation not in (-1, 1):
            raise HolonomyGraphError("cycle orientation must be +1 or -1")
        if not 0 <= int(edge_index) < len(p):
            raise HolonomyGraphError("cycle edge index out of range")
        total += orientation * float(p[int(edge_index)])
    return math.atan2(math.sin(total), math.cos(total))


def wilson_loop(
    phases: Sequence[float],
    signed_edge_indices: Iterable[tuple[int, int]],
) -> complex:
    return cmath.exp(1j * oriented_cycle_phase(phases, signed_edge_indices))


def forest_gauge_potential(
    num_vertices: int,
    edges: Sequence[tuple[int, int]],
    phases: Sequence[float],
) -> np.ndarray:
    """Construct chi that removes all edge phases when beta_1 == 0."""

    n = _check_vertex_count(num_vertices)
    checked = _check_edges(n, edges)
    if len(phases) != len(checked):
        raise HolonomyGraphError("phases and edges must have equal length")
    if cycle_rank(n, checked) != 0:
        raise HolonomyGraphError("edge phases are globally removable only for a forest")

    p = np.asarray(phases, dtype=float)
    if not np.all(np.isfinite(p)):
        raise HolonomyGraphError("phases must be finite")

    adjacency: list[list[tuple[int, int, int]]] = [[] for _ in range(n)]
    for edge_index, (i, j) in enumerate(checked):
        adjacency[i].append((j, edge_index, +1))
        adjacency[j].append((i, edge_index, -1))

    chi = np.zeros(n, dtype=float)
    seen = [False] * n
    for root in range(n):
        if seen[root]:
            continue
        seen[root] = True
        queue: deque[int] = deque([root])
        while queue:
            u = queue.popleft()
            for v, edge_index, direction in adjacency[u]:
                if seen[v]:
                    continue
                theta = float(p[edge_index])
                # edge i->j transforms as theta + chi_j - chi_i.
                # direction=+1 means u=i,v=j; direction=-1 means u=j,v=i.
                if direction == +1:
                    chi[v] = chi[u] - theta
                else:
                    chi[v] = chi[u] + theta
                seen[v] = True
                queue.append(v)
    return chi


def phase_dressed_hamiltonian(
    diagonal_energies: Sequence[float],
    edges: Sequence[tuple[int, int]],
    hoppings: Sequence[complex],
    phases: Sequence[float],
) -> np.ndarray:
    """Build a Hermitian graph Hamiltonian with phase-dressed edge couplings."""

    eps = np.asarray(diagonal_energies, dtype=float)
    if eps.ndim != 1 or eps.size == 0 or not np.all(np.isfinite(eps)):
        raise HolonomyGraphError("diagonal_energies must be a finite 1D vector")
    n = int(eps.size)
    checked = _check_edges(n, edges)
    if not (len(checked) == len(hoppings) == len(phases)):
        raise HolonomyGraphError("edges, hoppings, and phases must have equal length")
    p = np.asarray(phases, dtype=float)
    if not np.all(np.isfinite(p)):
        raise HolonomyGraphError("phases must be finite")

    h = np.diag(eps.astype(complex))
    for (i, j), hopping, theta in zip(checked, hoppings, p):
        t = complex(hopping)
        if not (math.isfinite(t.real) and math.isfinite(t.imag)):
            raise HolonomyGraphError("hoppings must be finite")
        amplitude = t * cmath.exp(1j * float(theta))
        h[i, j] += amplitude
        h[j, i] += amplitude.conjugate()

    if not np.allclose(h, h.conjugate().T, rtol=0.0, atol=1e-12):
        raise HolonomyGraphError("constructed Hamiltonian is not Hermitian")
    return h


def basis_rephasing_unitary(chi: Sequence[float]) -> np.ndarray:
    c = np.asarray(chi, dtype=float)
    if c.ndim != 1 or not np.all(np.isfinite(c)):
        raise HolonomyGraphError("chi must be a finite 1D vector")
    return np.diag(np.exp(1j * c))


def gauge_equivalent_hamiltonian(
    hamiltonian: np.ndarray, chi: Sequence[float]
) -> np.ndarray:
    h = np.asarray(hamiltonian, dtype=complex)
    if h.ndim != 2 or h.shape[0] != h.shape[1]:
        raise HolonomyGraphError("hamiltonian must be square")
    if h.shape[0] != len(chi):
        raise HolonomyGraphError("chi dimension must match Hamiltonian")
    u = basis_rephasing_unitary(chi)
    return u.conjugate().T @ h @ u


def spectral_eigenvalues(hamiltonian: np.ndarray) -> np.ndarray:
    h = np.asarray(hamiltonian, dtype=complex)
    if h.ndim != 2 or h.shape[0] != h.shape[1]:
        raise HolonomyGraphError("hamiltonian must be square")
    if not np.allclose(h, h.conjugate().T, rtol=0.0, atol=1e-12):
        raise HolonomyGraphError("hamiltonian must be Hermitian")
    return np.linalg.eigvalsh(h)
