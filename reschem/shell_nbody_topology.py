"""Candidate shell-level N-body topology diagnostics for Resonant Chemistry.

This module does not replace quantum chemistry. It adds representation-level
observables around explicit nuclear Coulomb centres. In 3 spatial dimensions,
exchange topology of identical particles reduces to permutations; braid-group
language is reserved for effective 2D/constrained projections.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import pi
from typing import Iterable, Sequence
import numpy as np

KE = 1.0  # atomic units

@dataclass(frozen=True)
class NucleusAttractor:
    Z: float
    position: tuple[float, float, float] = (0.0, 0.0, 0.0)

    def coulomb_potential(self, r: Sequence[float]) -> float:
        d = np.linalg.norm(np.asarray(r, dtype=float) - np.asarray(self.position, dtype=float))
        if d == 0.0:
            return float('-inf')
        return -KE * self.Z / d


def shell_capacity(l: int) -> int:
    if l < 0:
        raise ValueError("l must be non-negative")
    return 2 * (2 * l + 1)


def hole_count(l: int, k: int) -> int:
    cap = shell_capacity(l)
    if not 0 <= k <= cap:
        raise ValueError("occupation outside shell capacity")
    return cap - k


def particle_hole_partner(l: int, k: int) -> int:
    return hole_count(l, k)


def half_filled(l: int, k: int) -> bool:
    return k == (2 * l + 1)


def _unwrap_winding(z: np.ndarray) -> float:
    if z.ndim != 1 or len(z) < 2:
        raise ValueError("trajectory must be a 1D complex sequence")
    if np.any(np.abs(z) == 0):
        raise ValueError("trajectory crosses reference centre")
    a = np.unwrap(np.angle(z))
    return float((a[-1] - a[0]) / (2 * pi))


def projected_nuclear_winding(path_xyz: Sequence[Sequence[float]], nucleus: NucleusAttractor, axes=(0, 1)) -> float:
    p = np.asarray(path_xyz, dtype=float)
    c = np.asarray(nucleus.position, dtype=float)
    z = (p[:, axes[0]] - c[axes[0]]) + 1j * (p[:, axes[1]] - c[axes[1]])
    return _unwrap_winding(z)


def projected_pair_winding(path_i: Sequence[Sequence[float]], path_j: Sequence[Sequence[float]], axes=(0, 1)) -> float:
    a = np.asarray(path_i, dtype=float)
    b = np.asarray(path_j, dtype=float)
    if a.shape != b.shape:
        raise ValueError("pair trajectories must share shape")
    z = (a[:, axes[0]] - b[:, axes[0]]) + 1j * (a[:, axes[1]] - b[:, axes[1]])
    return _unwrap_winding(z)


def permutation_parity(permutation: Sequence[int]) -> int:
    p = list(permutation)
    if sorted(p) != list(range(len(p))):
        raise ValueError("not a permutation of 0..N-1")
    inv = sum(p[i] > p[j] for i in range(len(p)) for j in range(i + 1, len(p)))
    return -1 if inv % 2 else 1


def conformal_inverse(phi: complex, anchor: complex = 0.5 + 0j) -> complex:
    zeta = complex(phi) - complex(anchor)
    if zeta == 0:
        return complex(np.inf, np.inf)
    return 1.0 / zeta


def shell_duality_record(n: int, l: int, k: int) -> dict:
    cap = shell_capacity(l)
    return {
        "n": int(n), "l": int(l), "occupation": int(k), "capacity": cap,
        "holes": cap - k, "particle_hole_partner": cap - k,
        "half_filled_self_dual": half_filled(l, k),
    }


def shell_topology_summary(n: int, l: int, k: int, nuclear_windings: Iterable[float], pair_windings: Iterable[float], permutation: Sequence[int] | None = None) -> dict:
    rec = shell_duality_record(n, l, k)
    nw = tuple(float(x) for x in nuclear_windings)
    pw = tuple(float(x) for x in pair_windings)
    rec.update({
        "nuclear_windings": nw,
        "pair_windings": pw,
        "mean_abs_nuclear_winding": float(np.mean(np.abs(nw))) if nw else 0.0,
        "mean_abs_pair_winding": float(np.mean(np.abs(pw))) if pw else 0.0,
        "exchange_parity": permutation_parity(permutation) if permutation is not None else None,
        "status": "CANDIDATE_REPRESENTATION_OBSERVABLE",
    })
    return rec
