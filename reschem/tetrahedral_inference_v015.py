"""Tetrahedral SIC inference geometry for Resonant Chemistry v0.15.

The primary tetrahedral frame is taken from the TIR/Metatime Hilbert-Kahler
phase Hamiltonian.  It supplies four probability coordinates on the Bloch ball
for the electron/subshell spin-reduction layer.  Spatial orbital-band features
remain a separate calculation channel.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np


TIR_REFERENCE_REPOSITORY = "AdrianLipa90/Metatime-Relation_of_Information_Framework"
TIR_REFERENCE_COMMIT = "7498d8c6349573f8d58895145342e849d36983c8"
TIR_REFERENCE_PATH = "theory/metatime/foundational_formal_notes/hilbert_kahler_phase_hamiltonian/main.tex"
TETRAHEDRAL_SIC_CONTRACT_ID = "RESCHEM_TIR_TETRAHEDRAL_SIC_INFERENCE_V0_15"

_SQRT3 = math.sqrt(3.0)
_TETRA = np.asarray(
    [
        (1.0, 1.0, 1.0),
        (1.0, -1.0, -1.0),
        (-1.0, 1.0, -1.0),
        (-1.0, -1.0, 1.0),
    ],
    dtype=float,
) / _SQRT3


def tetrahedral_vertices() -> np.ndarray:
    return _TETRA.copy()


def tetrahedral_gram_matrix() -> np.ndarray:
    dots = _TETRA @ _TETRA.T
    return 0.5 * (1.0 + dots)


def _bloch_vector(values: Sequence[float]) -> np.ndarray:
    row = np.asarray(values, dtype=float)
    if row.shape != (3,) or np.any(~np.isfinite(row)):
        raise ValueError("Bloch vector must contain exactly three finite components")
    norm = float(np.linalg.norm(row))
    if norm > 1.0 + 1.0e-12:
        raise ValueError("Bloch vector norm must be at most one")
    if norm > 1.0:
        row = row / norm
    return row


def bloch_vector_from_angles(theta: float, phi: float, radius: float = 1.0) -> np.ndarray:
    polar = float(theta)
    azimuth = float(phi)
    r = float(radius)
    if not all(math.isfinite(value) for value in (polar, azimuth, r)):
        raise ValueError("Bloch angles and radius must be finite")
    if polar < 0.0 or polar > math.pi:
        raise ValueError("theta must be in [0, pi]")
    if r < 0.0 or r > 1.0:
        raise ValueError("Bloch radius must be in [0, 1]")
    return np.asarray(
        [
            r * math.sin(polar) * math.cos(azimuth),
            r * math.sin(polar) * math.sin(azimuth),
            r * math.cos(polar),
        ],
        dtype=float,
    )


def tetrahedral_sic_probabilities(bloch_vector: Sequence[float]) -> np.ndarray:
    """Return p_j(n)=1/4(1+n·v_j) for the TIR tetrahedral frame."""
    n = _bloch_vector(bloch_vector)
    probs = 0.25 * (1.0 + _TETRA @ n)
    if np.any(probs < -1.0e-12):
        raise RuntimeError("tetrahedral SIC probability became negative")
    probs = np.maximum(probs, 0.0)
    probs /= float(np.sum(probs))
    return probs


def sic_information_nats(probabilities: Sequence[float]) -> float:
    """KL information of SIC coordinates relative to the maximally mixed 1/4 baseline."""
    probs = np.asarray(probabilities, dtype=float)
    if probs.shape != (4,) or np.any(probs < 0.0):
        raise ValueError("tetrahedral SIC probabilities must be four nonnegative values")
    if not np.isclose(float(np.sum(probs)), 1.0, atol=1.0e-12):
        raise ValueError("tetrahedral SIC probabilities must sum to one")
    positive = probs > 0.0
    return float(np.sum(probs[positive] * np.log(4.0 * probs[positive])))


def _rotation_matrix(axis: Sequence[float], angle: float) -> np.ndarray:
    a = np.asarray(axis, dtype=float)
    if a.shape != (3,) or np.any(~np.isfinite(a)):
        raise ValueError("rotation axis must contain three finite components")
    norm = float(np.linalg.norm(a))
    if norm <= 0.0:
        raise ValueError("rotation axis must have positive norm")
    x, y, z = a / norm
    c = math.cos(float(angle))
    s = math.sin(float(angle))
    one = 1.0 - c
    return np.asarray(
        [
            (c + x * x * one, x * y * one - z * s, x * z * one + y * s),
            (y * x * one + z * s, c + y * y * one, y * z * one - x * s),
            (z * x * one - y * s, z * y * one + x * s, c + z * z * one),
        ],
        dtype=float,
    )


def tetrahedral_phase_trace(
    bloch_vector: Sequence[float],
    *,
    cone_index: int = 0,
    rotation_axis: Sequence[float] = (0.0, 0.0, 1.0),
    phase_samples: int = 128,
) -> np.ndarray:
    n = _bloch_vector(bloch_vector)
    index = int(cone_index)
    if index < 0 or index >= 4:
        raise ValueError("cone_index must be in [0, 3]")
    count = int(phase_samples)
    if count < 16:
        raise ValueError("phase_samples must be at least 16")
    trace = []
    for phase in np.linspace(0.0, 2.0 * math.pi, count, endpoint=False):
        rotated = _rotation_matrix(rotation_axis, float(phase)) @ n
        trace.append(float(tetrahedral_sic_probabilities(rotated)[index] - 0.25))
    return np.asarray(trace, dtype=float)


def dominant_harmonic(trace: Sequence[float]) -> tuple[int, float]:
    row = np.asarray(trace, dtype=float)
    if row.ndim != 1 or len(row) < 16:
        raise ValueError("trace must be one-dimensional with at least 16 samples")
    centered = row - float(np.mean(row))
    spectrum = np.abs(np.fft.rfft(centered)) / float(len(centered))
    if len(spectrum) <= 1 or float(np.max(spectrum[1:])) <= 1.0e-12:
        return 0, 0.0
    order = 1 + int(np.argmax(spectrum[1:]))
    return order, float(spectrum[order])


def period2_p_spin_bloch_control(z: int) -> dict:
    """Reduce the B-Ne 2p alpha/beta occupation to a Bloch-ball spin coordinate."""
    from .atomic_hf_average import subshells_for_atom

    atomic_number = int(z)
    if atomic_number < 5 or atomic_number > 10:
        raise ValueError("period-2 p-spin control supports B-Ne (Z=5..10)")
    p_shell = next(shell for shell in subshells_for_atom(atomic_number, 0) if shell.label == "2p")
    alpha = int(p_shell.alpha_occupancy)
    beta = int(p_shell.beta_occupancy)
    total = alpha + beta
    if total <= 0:
        raise RuntimeError("2p occupancy must be positive for B-Ne control cohort")
    polarization = float(alpha - beta) / float(total)
    bloch = np.asarray((0.0, 0.0, polarization), dtype=float)
    return {
        "schema": "RESCHEM_PERIOD2_P_SPIN_BLOCH_CONTROL_V0_15",
        "Z": atomic_number,
        "subshell": "2p",
        "alpha_occupancy": alpha,
        "beta_occupancy": beta,
        "total_occupancy": total,
        "spin_polarization": polarization,
        "bloch_vector": [float(value) for value in bloch],
        "bloch_radius": abs(polarization),
        "reduction": "MODEL_DEFINED_SUBSHELL_SPIN_POLARIZATION_BLOCH_COORDINATE",
        "source": "reschem.atomic_hf_average.subshells_for_atom",
    }


@dataclass(frozen=True)
class TetrahedralInferenceProbe:
    bloch_vector: tuple[float, float, float]
    sic_probabilities: tuple[float, float, float, float]
    sic_information_nats: float
    bloch_radius: float
    gram_diagonal: tuple[float, ...]
    gram_off_diagonal: float
    dominant_harmonic_order: int
    dominant_harmonic_strength: float

    def as_dict(self) -> dict:
        return {
            "schema": TETRAHEDRAL_SIC_CONTRACT_ID,
            "tir_reference": {
                "repository": TIR_REFERENCE_REPOSITORY,
                "commit": TIR_REFERENCE_COMMIT,
                "path": TIR_REFERENCE_PATH,
                "coordinate_expression": "p_j(n)=1/4*(1+n dot v_j)",
            },
            "bloch_vector": list(self.bloch_vector),
            "bloch_radius": self.bloch_radius,
            "sic_probabilities": list(self.sic_probabilities),
            "sic_information_nats": self.sic_information_nats,
            "gram": {
                "diagonal": list(self.gram_diagonal),
                "off_diagonal": self.gram_off_diagonal,
            },
            "phase": {
                "dominant_harmonic_order": self.dominant_harmonic_order,
                "dominant_harmonic_strength": self.dominant_harmonic_strength,
            },
            "epistemic_status": {
                "tetrahedral_frame": "TIR_MODEL_AXIOM_REFERENCE_BOUND",
                "bloch_coordinate": "MODEL_DEFINED_CONTROL_REDUCTION",
                "spectral_validation": "BLIND_COMPARISON_PENDING",
            },
        }


def build_tetrahedral_inference_probe(
    bloch_vector: Sequence[float],
    *,
    phase_samples: int = 128,
    cone_index: int = 0,
    rotation_axis: Sequence[float] = (0.0, 0.0, 1.0),
) -> TetrahedralInferenceProbe:
    n = _bloch_vector(bloch_vector)
    probs = tetrahedral_sic_probabilities(n)
    info = sic_information_nats(probs)
    gram = tetrahedral_gram_matrix()
    trace = tetrahedral_phase_trace(
        n,
        cone_index=cone_index,
        rotation_axis=rotation_axis,
        phase_samples=phase_samples,
    )
    harmonic_order, harmonic_strength = dominant_harmonic(trace)
    return TetrahedralInferenceProbe(
        bloch_vector=tuple(float(value) for value in n),
        sic_probabilities=tuple(float(value) for value in probs),
        sic_information_nats=info,
        bloch_radius=float(np.linalg.norm(n)),
        gram_diagonal=tuple(float(value) for value in np.diag(gram)),
        gram_off_diagonal=float(gram[0, 1]),
        dominant_harmonic_order=harmonic_order,
        dominant_harmonic_strength=harmonic_strength,
    )
