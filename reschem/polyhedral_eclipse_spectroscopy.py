"""Polyhedral-cone orbital information and eclipse observables for v0.15.

The module keeps the existing radial atomic solver as the control substrate and
adds a separate polyhedral angular partition. Semantic mass is an explicit,
provenance-bearing input. Spectral comparison is performed through frozen
prediction records after model features have been generated.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping, Sequence

import numpy as np
from scipy.special import sph_harm


KAPPA_INFORMATION = math.log(2.0) / (24.0 * math.pi)
_EPS = 1.0e-15


def _unit(vector: Sequence[float]) -> np.ndarray:
    row = np.asarray(vector, dtype=float)
    if row.shape != (3,):
        raise ValueError("direction must have exactly three components")
    norm = float(np.linalg.norm(row))
    if not math.isfinite(norm) or norm <= 0.0:
        raise ValueError("direction must have positive finite norm")
    return row / norm


def fibonacci_sphere(sample_count: int) -> np.ndarray:
    """Return deterministic equal-area sample directions on S^2."""
    n = int(sample_count)
    if n < 256:
        raise ValueError("sample_count must be at least 256")
    i = np.arange(n, dtype=float)
    z = 1.0 - 2.0 * (i + 0.5) / float(n)
    golden_angle = math.pi * (3.0 - math.sqrt(5.0))
    azimuth = golden_angle * i
    radius = np.sqrt(np.maximum(0.0, 1.0 - z * z))
    return np.column_stack((radius * np.cos(azimuth), radius * np.sin(azimuth), z))


def regular_polyhedral_axes(kind: str) -> np.ndarray:
    """Return normalized vertex axes for a regular-polyhedron cone partition."""
    key = kind.strip().lower()
    if key == "tetrahedron":
        raw = np.asarray(
            [
                (1.0, 1.0, 1.0),
                (1.0, -1.0, -1.0),
                (-1.0, 1.0, -1.0),
                (-1.0, -1.0, 1.0),
            ],
            dtype=float,
        )
    elif key == "octahedron":
        raw = np.asarray(
            [
                (1.0, 0.0, 0.0),
                (-1.0, 0.0, 0.0),
                (0.0, 1.0, 0.0),
                (0.0, -1.0, 0.0),
                (0.0, 0.0, 1.0),
                (0.0, 0.0, -1.0),
            ],
            dtype=float,
        )
    elif key == "cube":
        raw = np.asarray(
            [
                (sx, sy, sz)
                for sx in (-1.0, 1.0)
                for sy in (-1.0, 1.0)
                for sz in (-1.0, 1.0)
            ],
            dtype=float,
        )
    elif key == "icosahedron":
        phi = 0.5 * (1.0 + math.sqrt(5.0))
        raw = np.asarray(
            [
                (0.0, sy, sz * phi)
                for sy in (-1.0, 1.0)
                for sz in (-1.0, 1.0)
            ]
            + [
                (sx, sy * phi, 0.0)
                for sx in (-1.0, 1.0)
                for sy in (-1.0, 1.0)
            ]
            + [
                (sx * phi, 0.0, sz)
                for sx in (-1.0, 1.0)
                for sz in (-1.0, 1.0)
            ],
            dtype=float,
        )
    else:
        raise ValueError(f"unsupported regular polyhedron: {kind!r}")
    return raw / np.linalg.norm(raw, axis=1)[:, None]


@dataclass(frozen=True)
class PolyhedralConePartition:
    name: str
    axes: tuple[tuple[float, float, float], ...]

    @classmethod
    def regular(cls, kind: str) -> "PolyhedralConePartition":
        axes = regular_polyhedral_axes(kind)
        return cls(
            name=kind.strip().lower(),
            axes=tuple(tuple(float(value) for value in row) for row in axes),
        )

    def axis_array(self) -> np.ndarray:
        axes = np.asarray(self.axes, dtype=float)
        if axes.ndim != 2 or axes.shape[1] != 3 or len(axes) < 4:
            raise ValueError("polyhedral partition requires at least four 3D axes")
        norms = np.linalg.norm(axes, axis=1)
        if np.any(~np.isfinite(norms)) or np.any(norms <= 0.0):
            raise ValueError("polyhedral axes must have positive finite norm")
        return axes / norms[:, None]

    def assignments(self, directions: np.ndarray) -> np.ndarray:
        points = np.asarray(directions, dtype=float)
        if points.ndim != 2 or points.shape[1] != 3:
            raise ValueError("directions must have shape (N, 3)")
        return np.argmax(points @ self.axis_array().T, axis=1)

    def solid_angle_fractions(self, sample_count: int = 8192) -> np.ndarray:
        directions = fibonacci_sphere(sample_count)
        assignment = self.assignments(directions)
        counts = np.bincount(assignment, minlength=len(self.axes)).astype(float)
        return counts / float(np.sum(counts))


def m_state_coefficients(l: int, m: int) -> np.ndarray:
    ell = int(l)
    em = int(m)
    if ell < 0 or abs(em) > ell:
        raise ValueError("require l >= 0 and -l <= m <= l")
    coeffs = np.zeros(2 * ell + 1, dtype=complex)
    coeffs[em + ell] = 1.0 + 0.0j
    return coeffs


def orbital_angular_density(
    l: int,
    coefficients: Sequence[complex],
    directions: np.ndarray,
) -> np.ndarray:
    """Evaluate normalized |sum_m c_m Y_lm|^2 on equal-area directions."""
    ell = int(l)
    coeffs = np.asarray(coefficients, dtype=complex)
    if ell < 0 or coeffs.shape != (2 * ell + 1,):
        raise ValueError("coefficients must contain one entry for every m=-l..l")
    norm = float(np.linalg.norm(coeffs))
    if not math.isfinite(norm) or norm <= 0.0:
        raise ValueError("orbital coefficient vector must have positive finite norm")
    coeffs = coeffs / norm

    points = np.asarray(directions, dtype=float)
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError("directions must have shape (N, 3)")
    radii = np.linalg.norm(points, axis=1)
    if np.any(radii <= 0.0):
        raise ValueError("directions must have positive norm")
    points = points / radii[:, None]
    polar = np.arccos(np.clip(points[:, 2], -1.0, 1.0))
    azimuth = np.arctan2(points[:, 1], points[:, 0])

    amplitude = np.zeros(len(points), dtype=complex)
    for index, em in enumerate(range(-ell, ell + 1)):
        amplitude += coeffs[index] * sph_harm(em, ell, azimuth, polar)
    density = np.square(np.abs(amplitude))
    total = float(np.sum(density))
    if not math.isfinite(total) or total <= 0.0:
        raise RuntimeError("orbital angular density failed normalization")
    return density / total


def cone_probabilities(
    partition: PolyhedralConePartition,
    directions: np.ndarray,
    normalized_density: np.ndarray,
) -> np.ndarray:
    density = np.asarray(normalized_density, dtype=float)
    if density.shape != (len(directions),):
        raise ValueError("normalized_density length must equal direction count")
    if np.any(density < 0.0) or not np.isclose(float(np.sum(density)), 1.0, atol=1.0e-10):
        raise ValueError("normalized_density must be nonnegative and sum to one")
    assignment = partition.assignments(directions)
    probs = np.bincount(
        assignment,
        weights=density,
        minlength=len(partition.axes),
    ).astype(float)
    probs /= float(np.sum(probs))
    return probs


def shannon_information_nats(probabilities: Sequence[float]) -> float:
    probs = np.asarray(probabilities, dtype=float)
    positive = probs > 0.0
    return -float(np.sum(probs[positive] * np.log(probs[positive])))


def polyhedral_information_nats(
    probabilities: Sequence[float],
    solid_angle_fractions: Sequence[float],
) -> float:
    """KL information of orbital cone occupancy relative to cone solid angle."""
    probs = np.asarray(probabilities, dtype=float)
    reference = np.asarray(solid_angle_fractions, dtype=float)
    if probs.shape != reference.shape:
        raise ValueError("probability and solid-angle vectors must have equal shape")
    if np.any(probs < 0.0) or np.any(reference <= 0.0):
        raise ValueError("probabilities must be nonnegative and reference strictly positive")
    if not np.isclose(float(np.sum(probs)), 1.0, atol=1.0e-10):
        raise ValueError("probabilities must sum to one")
    if not np.isclose(float(np.sum(reference)), 1.0, atol=1.0e-10):
        raise ValueError("solid-angle fractions must sum to one")
    positive = probs > 0.0
    return float(np.sum(probs[positive] * np.log(probs[positive] / reference[positive])))


def _rotation_matrix(axis: Sequence[float], angle: float) -> np.ndarray:
    x, y, z = _unit(axis)
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


def eclipse_phase_trace(
    partition: PolyhedralConePartition,
    l: int,
    coefficients: Sequence[complex],
    *,
    rotation_axis: Sequence[float] = (0.0, 0.0, 1.0),
    observer_direction: Sequence[float] = (1.0, 0.0, 0.0),
    sample_count: int = 4096,
    phase_samples: int = 128,
) -> np.ndarray:
    """Return observer-cone occupancy contrast over one model phase cycle."""
    if int(phase_samples) < 16:
        raise ValueError("phase_samples must be at least 16")
    directions = fibonacci_sphere(sample_count)
    reference = partition.solid_angle_fractions(sample_count)
    observer = _unit(observer_direction)
    axes = partition.axis_array()
    observer_cone = int(np.argmax(axes @ observer))
    baseline = float(reference[observer_cone])

    trace = []
    for phase in np.linspace(0.0, 2.0 * math.pi, int(phase_samples), endpoint=False):
        rotation = _rotation_matrix(rotation_axis, -float(phase))
        orbital_frame_points = directions @ rotation.T
        density = orbital_angular_density(l, coefficients, orbital_frame_points)
        probs = cone_probabilities(partition, directions, density)
        trace.append(float(probs[observer_cone] / baseline - 1.0))
    return np.asarray(trace, dtype=float)


def dominant_harmonic(trace: Sequence[float]) -> tuple[int, float]:
    row = np.asarray(trace, dtype=float)
    if row.ndim != 1 or len(row) < 16:
        raise ValueError("trace must be a one-dimensional array with at least 16 samples")
    centered = row - float(np.mean(row))
    spectrum = np.abs(np.fft.rfft(centered)) / float(len(centered))
    if len(spectrum) <= 1 or float(np.max(spectrum[1:])) <= 1.0e-12:
        return 0, 0.0
    order = 1 + int(np.argmax(spectrum[1:]))
    return order, float(spectrum[order])


def semantic_mass_from_card(card: Mapping[str, object], key: str = "semantic_mass") -> tuple[float, str]:
    """Resolve a provenance-bearing semantic mass assignment from an atom card."""
    tir = card.get("tir")
    if not isinstance(tir, Mapping):
        raise ValueError("atom card lacks tir mapping")
    semantic_axes = tir.get("semantic_axes")
    if not isinstance(semantic_axes, Mapping):
        raise ValueError("atom card lacks tir.semantic_axes mapping")
    values = semantic_axes.get("values")
    if not isinstance(values, Mapping) or key not in values:
        raise ValueError(f"semantic mass binding {key!r} is unresolved")
    raw = values[key]
    if isinstance(raw, Mapping):
        value = raw.get("value")
        provenance = raw.get("provenance")
    else:
        value = raw
        provenance = semantic_axes.get("provenance")
    mass = float(value)
    if not math.isfinite(mass):
        raise ValueError("semantic mass must be finite")
    if not provenance:
        raise ValueError("semantic mass binding requires provenance")
    return mass, str(provenance)


@dataclass(frozen=True)
class OrbitalEclipseProbe:
    partition: str
    l: int
    nucleon_count: int
    semantic_mass: float
    semantic_mass_provenance: str
    semantic_mass_per_nucleon: float
    shannon_information_nats: float
    polyhedral_information_nats: float
    orbital_information_ratio_to_nucleons: float
    radial_nuclear_exposure: float
    eclipse_coupling: float
    cone_probabilities: tuple[float, ...]
    solid_angle_fractions: tuple[float, ...]
    cone_information_contributions: tuple[float, ...]
    dominant_eclipse_harmonic_order: int
    dominant_eclipse_harmonic_strength: float

    def as_dict(self) -> dict:
        return {
            "schema": "RESCHEM_POLYHEDRAL_ECLIPSE_PROBE_V0_15",
            "partition": self.partition,
            "l": self.l,
            "nucleon_count": self.nucleon_count,
            "semantic_mass": {
                "value": self.semantic_mass,
                "provenance": self.semantic_mass_provenance,
                "per_nucleon": self.semantic_mass_per_nucleon,
            },
            "information": {
                "kappa": KAPPA_INFORMATION,
                "shannon_nats": self.shannon_information_nats,
                "polyhedral_relative_nats": self.polyhedral_information_nats,
                "ratio_to_nucleons_kappa_normalized": self.orbital_information_ratio_to_nucleons,
            },
            "nuclear_exposure": {
                "radial_control": self.radial_nuclear_exposure,
                "eclipse_coupling": self.eclipse_coupling,
            },
            "polyhedral_cones": {
                "probabilities": list(self.cone_probabilities),
                "solid_angle_fractions": list(self.solid_angle_fractions),
                "information_contributions": list(self.cone_information_contributions),
            },
            "phase": {
                "dominant_harmonic_order": self.dominant_eclipse_harmonic_order,
                "dominant_harmonic_strength": self.dominant_eclipse_harmonic_strength,
                "frequency_mapping_status": "REQUIRES_INDEPENDENT_PHASE_RATE",
            },
            "epistemic_status": {
                "geometry": "MODEL_DEFINED_POLYHEDRAL_CONE_PARTITION",
                "semantic_mass": "PROVENANCE_BOUND_INPUT",
                "radial_exposure": "CONTROL_INPUT",
                "spectral_validation": "BLIND_COMPARISON_PENDING",
            },
        }


def build_orbital_eclipse_probe(
    *,
    partition: PolyhedralConePartition,
    l: int,
    coefficients: Sequence[complex],
    nucleon_count: int,
    semantic_mass: float,
    semantic_mass_provenance: str,
    radial_nuclear_exposure: float,
    sample_count: int = 8192,
    phase_samples: int = 128,
    rotation_axis: Sequence[float] = (0.0, 0.0, 1.0),
    observer_direction: Sequence[float] = (1.0, 0.0, 0.0),
) -> OrbitalEclipseProbe:
    a = int(nucleon_count)
    if a <= 0:
        raise ValueError("nucleon_count must be positive")
    mass = float(semantic_mass)
    exposure = float(radial_nuclear_exposure)
    if not math.isfinite(mass) or not math.isfinite(exposure):
        raise ValueError("semantic mass and radial exposure must be finite")
    if not semantic_mass_provenance:
        raise ValueError("semantic_mass_provenance is required")

    directions = fibonacci_sphere(sample_count)
    density = orbital_angular_density(l, coefficients, directions)
    probs = cone_probabilities(partition, directions, density)
    reference = partition.solid_angle_fractions(sample_count)
    shannon = shannon_information_nats(probs)
    poly_info = polyhedral_information_nats(probs, reference)
    info_ratio = poly_info / (float(a) * KAPPA_INFORMATION)
    mass_per_nucleon = mass / float(a)
    coupling = mass_per_nucleon * info_ratio * exposure

    contributions = np.zeros_like(probs)
    positive = probs > 0.0
    contributions[positive] = probs[positive] * np.log(probs[positive] / reference[positive])

    trace = eclipse_phase_trace(
        partition,
        l,
        coefficients,
        rotation_axis=rotation_axis,
        observer_direction=observer_direction,
        sample_count=max(1024, sample_count // 2),
        phase_samples=phase_samples,
    )
    harmonic_order, harmonic_strength = dominant_harmonic(trace)

    return OrbitalEclipseProbe(
        partition=partition.name,
        l=int(l),
        nucleon_count=a,
        semantic_mass=mass,
        semantic_mass_provenance=str(semantic_mass_provenance),
        semantic_mass_per_nucleon=mass_per_nucleon,
        shannon_information_nats=shannon,
        polyhedral_information_nats=poly_info,
        orbital_information_ratio_to_nucleons=info_ratio,
        radial_nuclear_exposure=exposure,
        eclipse_coupling=coupling,
        cone_probabilities=tuple(float(value) for value in probs),
        solid_angle_fractions=tuple(float(value) for value in reference),
        cone_information_contributions=tuple(float(value) for value in contributions),
        dominant_eclipse_harmonic_order=harmonic_order,
        dominant_eclipse_harmonic_strength=harmonic_strength,
    )


def eclipse_frequency_hz(phase_rate_rad_per_second: float, harmonic_order: int) -> float:
    rate = float(phase_rate_rad_per_second)
    order = int(harmonic_order)
    if not math.isfinite(rate) or rate < 0.0:
        raise ValueError("phase rate must be finite and nonnegative")
    if order < 0:
        raise ValueError("harmonic order must be nonnegative")
    return float(order) * rate / (2.0 * math.pi)


def blind_transition_prediction(
    initial_label: str,
    initial: OrbitalEclipseProbe,
    final_label: str,
    final: OrbitalEclipseProbe,
) -> dict:
    """Freeze model-side transition features before spectral observations are joined."""
    if initial.nucleon_count != final.nucleon_count:
        raise ValueError("transition probes must use the same nucleon count")
    if initial.semantic_mass_provenance != final.semantic_mass_provenance:
        raise ValueError("transition probes must share one semantic-mass provenance binding")
    return {
        "schema": "RESCHEM_POLYHEDRAL_ECLIPSE_BLIND_TRANSITION_V0_15",
        "initial": initial_label,
        "final": final_label,
        "partition": initial.partition,
        "nucleon_count": initial.nucleon_count,
        "delta_polyhedral_information_nats": (
            final.polyhedral_information_nats - initial.polyhedral_information_nats
        ),
        "delta_orbital_information_ratio": (
            final.orbital_information_ratio_to_nucleons
            - initial.orbital_information_ratio_to_nucleons
        ),
        "delta_eclipse_coupling": final.eclipse_coupling - initial.eclipse_coupling,
        "initial_harmonic_order": initial.dominant_eclipse_harmonic_order,
        "final_harmonic_order": final.dominant_eclipse_harmonic_order,
        "observed_spectrum": "WITHHELD_FOR_BLIND_COMPARISON",
        "validation_status": "PREDICTION_FEATURES_FROZEN",
    }


def period2_p_radial_control_exposure(
    z: int,
    *,
    basis_size: int = 24,
    grid_points: int = 1500,
    mixing: float = 0.32,
    tolerance_hartree: float = 5.0e-8,
    max_iterations: int = 120,
) -> dict:
    """Compute the existing B-Ne 2p radial central-field exposure as control input."""
    from .atomic_radial_spectroscopy import (
        ALPHA_FINE_STRUCTURE,
        _pauli_central_zeta,
        _solve_period2_radial_state,
    )

    state = _solve_period2_radial_state(
        int(z),
        basis_size=basis_size,
        grid_points=grid_points,
        mixing=mixing,
        tolerance_hartree=tolerance_hartree,
        max_iterations=max_iterations,
    )
    zeta = _pauli_central_zeta(
        int(z),
        state["density"],
        state["one_p_density"],
        state["r"],
        state["weights"],
    )
    exposure = 2.0 * float(zeta) / (ALPHA_FINE_STRUCTURE**2)
    return {
        "schema": "RESCHEM_PERIOD2_P_RADIAL_EXPOSURE_CONTROL_V0_15",
        "Z": int(z),
        "radial_nuclear_exposure": exposure,
        "zeta_2p_hartree": float(zeta),
        "hf_energy_hartree": float(state["energy_hartree"]),
        "virial_residual_hartree": float(state["virial_residual_hartree"]),
        "control_source": "reschem.atomic_radial_spectroscopy",
        "status": "CONTROL_RADIAL_EXPOSURE_AVAILABLE",
    }
