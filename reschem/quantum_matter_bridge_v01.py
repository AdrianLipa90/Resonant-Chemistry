from __future__ import annotations

import math

import numpy as np


class QuantumMatterBridgeError(ValueError):
    """Fail-closed contract error for the candidate quantum-matter bridge."""


def validate_state(state, *, atol: float = 1e-12) -> np.ndarray:
    psi = np.asarray(state, dtype=np.complex128)
    if psi.ndim != 1 or psi.size == 0:
        raise QuantumMatterBridgeError(
            "state must be a non-empty one-dimensional vector"
        )
    if not np.isfinite(psi.real).all() or not np.isfinite(psi.imag).all():
        raise QuantumMatterBridgeError("state must be finite")
    norm = float(np.vdot(psi, psi).real)
    if not math.isfinite(norm) or not math.isclose(
        norm, 1.0, rel_tol=0.0, abs_tol=atol
    ):
        raise QuantumMatterBridgeError("state must be normalized")
    return psi


def validate_hermitian_operator(
    operator, *, dimension: int | None = None, atol: float = 1e-12
) -> np.ndarray:
    op = np.asarray(operator, dtype=np.complex128)
    if op.ndim != 2 or op.shape[0] != op.shape[1] or op.shape[0] == 0:
        raise QuantumMatterBridgeError("operator must be a non-empty square matrix")
    if dimension is not None and op.shape != (dimension, dimension):
        raise QuantumMatterBridgeError(
            "operator dimension does not match state space"
        )
    if not np.isfinite(op.real).all() or not np.isfinite(op.imag).all():
        raise QuantumMatterBridgeError("operator must be finite")
    if not np.allclose(op, op.conjugate().T, rtol=0.0, atol=atol):
        raise QuantumMatterBridgeError("operator must be Hermitian")
    return op


def first_order_energy_shift(
    state, perturbation, *, atol: float = 1e-12
) -> float:
    """Standard first-order energy response after a perturbation is admitted."""
    psi = validate_state(state, atol=atol)
    op = validate_hermitian_operator(
        perturbation, dimension=psi.size, atol=atol
    )
    value = np.vdot(psi, op @ psi)
    if abs(value.imag) > atol:
        raise QuantumMatterBridgeError(
            "Hermitian expectation acquired a non-negligible imaginary part"
        )
    return float(value.real)


def transition_angular_shift(
    lower_state,
    upper_state,
    perturbation,
    *,
    hbar: float = 1.0,
    atol: float = 1e-12,
) -> float:
    """Return (Delta E_upper - Delta E_lower) / hbar."""
    if not math.isfinite(hbar) or hbar <= 0.0:
        raise QuantumMatterBridgeError("hbar must be finite and positive")
    lower = first_order_energy_shift(lower_state, perturbation, atol=atol)
    upper = first_order_energy_shift(upper_state, perturbation, atol=atol)
    return (upper - lower) / hbar


def common_mode_perturbation(dimension: int, scalar: float) -> np.ndarray:
    """Construct u0*I; transition shifts must cancel exactly."""
    if not isinstance(dimension, int) or dimension <= 0:
        raise QuantumMatterBridgeError("dimension must be a positive integer")
    value = float(scalar)
    if not math.isfinite(value):
        raise QuantumMatterBridgeError("common-mode scalar must be finite")
    return value * np.eye(dimension, dtype=np.complex128)


def h2plus_total_born_oppenheimer_energy(
    electronic_energy: float, internuclear_distance: float
) -> float:
    """Add the +1/R proton-proton term to an H2+ electronic energy in a.u."""
    energy = float(electronic_energy)
    distance = float(internuclear_distance)
    if not math.isfinite(energy):
        raise QuantumMatterBridgeError("electronic energy must be finite")
    if not math.isfinite(distance) or distance <= 0.0:
        raise QuantumMatterBridgeError(
            "internuclear distance must be finite and positive"
        )
    return energy + 1.0 / distance
