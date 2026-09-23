from __future__ import annotations

import cmath
import math
from typing import Iterable, Sequence

import numpy as np


class ChemicalBerryLoopError(ValueError):
    pass


def linear_conical_intersection_hamiltonian(x: float, y: float) -> np.ndarray:
    x = float(x)
    y = float(y)
    if not (math.isfinite(x) and math.isfinite(y)):
        raise ChemicalBerryLoopError("parameters must be finite")
    return np.array([[y, x], [x, -y]], dtype=np.complex128)


def normalized_eigenstate(
    hamiltonian: np.ndarray,
    state_index: int = 0,
) -> np.ndarray:
    h = np.asarray(hamiltonian, dtype=np.complex128)
    if h.ndim != 2 or h.shape[0] != h.shape[1] or h.shape[0] == 0:
        raise ChemicalBerryLoopError("hamiltonian must be a non-empty square matrix")
    if not np.all(np.isfinite(h.real)) or not np.all(np.isfinite(h.imag)):
        raise ChemicalBerryLoopError("hamiltonian must be finite")
    if not np.allclose(h, h.conjugate().T, rtol=0.0, atol=1e-12):
        raise ChemicalBerryLoopError("hamiltonian must be Hermitian")
    values, vectors = np.linalg.eigh(h)
    if not 0 <= int(state_index) < len(values):
        raise ChemicalBerryLoopError("state_index out of range")
    return vectors[:, int(state_index)]


def normalized_overlap_transport(
    state_left: Sequence[complex],
    state_right: Sequence[complex],
    *,
    atol: float = 1e-12,
) -> complex:
    left = np.asarray(state_left, dtype=np.complex128).reshape(-1)
    right = np.asarray(state_right, dtype=np.complex128).reshape(-1)
    if left.shape != right.shape or left.size == 0:
        raise ChemicalBerryLoopError("states must have equal non-empty dimension")
    if not (
        np.all(np.isfinite(left.real))
        and np.all(np.isfinite(left.imag))
        and np.all(np.isfinite(right.real))
        and np.all(np.isfinite(right.imag))
    ):
        raise ChemicalBerryLoopError("states must be finite")
    for name, state in (("left", left), ("right", right)):
        norm = float(np.vdot(state, state).real)
        if not math.isclose(norm, 1.0, rel_tol=0.0, abs_tol=atol):
            raise ChemicalBerryLoopError(f"{name} state must be normalized")
    overlap = complex(np.vdot(left, right))
    magnitude = abs(overlap)
    if magnitude <= atol:
        raise ChemicalBerryLoopError("adjacent overlap is too small for phase transport")
    return overlap / magnitude


def discrete_wilson_loop(
    states: Iterable[Sequence[complex]],
    *,
    atol: float = 1e-12,
) -> complex:
    vecs = [np.asarray(state, dtype=np.complex128).reshape(-1) for state in states]
    if len(vecs) < 3:
        raise ChemicalBerryLoopError("closed loop requires at least three samples")
    product = 1.0 + 0.0j
    for left, right in zip(vecs, vecs[1:] + vecs[:1]):
        product *= normalized_overlap_transport(left, right, atol=atol)
    if not math.isclose(abs(product), 1.0, rel_tol=0.0, abs_tol=1e-10):
        raise ChemicalBerryLoopError("Wilson product lost unit modulus")
    return product / abs(product)


def discrete_berry_phase(
    states: Iterable[Sequence[complex]],
    *,
    atol: float = 1e-12,
) -> float:
    return float(cmath.phase(discrete_wilson_loop(states, atol=atol)))


def sampled_lower_state_loop(
    *,
    center_x: float = 0.0,
    center_y: float = 0.0,
    radius: float = 1.0,
    samples: int = 32,
) -> tuple[np.ndarray, ...]:
    cx = float(center_x)
    cy = float(center_y)
    r = float(radius)
    if not all(math.isfinite(v) for v in (cx, cy, r)):
        raise ChemicalBerryLoopError("loop parameters must be finite")
    if r <= 0.0:
        raise ChemicalBerryLoopError("radius must be positive")
    if not isinstance(samples, int) or samples < 3:
        raise ChemicalBerryLoopError("samples must be an integer >= 3")
    out = []
    for k in range(samples):
        angle = 2.0 * math.pi * k / samples
        h = linear_conical_intersection_hamiltonian(
            cx + r * math.cos(angle),
            cy + r * math.sin(angle),
        )
        out.append(normalized_eigenstate(h, 0))
    return tuple(out)


def rephase_states(
    states: Iterable[Sequence[complex]],
    phases: Sequence[float],
) -> tuple[np.ndarray, ...]:
    vecs = [np.asarray(state, dtype=np.complex128).reshape(-1) for state in states]
    if len(vecs) != len(phases):
        raise ChemicalBerryLoopError("one rephasing angle is required per state")
    out = []
    for state, phase in zip(vecs, phases):
        angle = float(phase)
        if not math.isfinite(angle):
            raise ChemicalBerryLoopError("rephasing angles must be finite")
        out.append(np.exp(1j * angle) * state)
    return tuple(out)
