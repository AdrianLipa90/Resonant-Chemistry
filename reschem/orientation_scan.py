"""Rigid relative-orientation controls for Resonant Chemistry.

This module owns geometry and a minimal two-orbital control Hamiltonian only.
It does not derive wavelengths, oscillator strengths, colors, or OES transition
observables.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Iterable, Sequence

import numpy as np


class OrientationScanError(ValueError):
    pass


def _finite(value: float, name: str) -> float:
    x = float(value)
    if not math.isfinite(x):
        raise OrientationScanError(f"{name} must be finite")
    return x


def _vector3(values: Sequence[float], name: str) -> np.ndarray:
    vec = np.asarray(values, dtype=float)
    if vec.shape != (3,) or not np.all(np.isfinite(vec)):
        raise OrientationScanError(f"{name} must be a finite 3-vector")
    return vec


def rotation_matrix(axis: Sequence[float], angle_rad: float) -> np.ndarray:
    """Return the proper 3D Rodrigues rotation matrix for one axis/angle."""
    unit = _vector3(axis, "axis")
    norm = float(np.linalg.norm(unit))
    if norm <= 0.0:
        raise OrientationScanError("axis must have non-zero norm")
    unit = unit / norm
    theta = _finite(angle_rad, "angle_rad")
    x, y, z = unit
    skew = np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])
    outer = np.outer(unit, unit)
    ident = np.eye(3)
    return (
        math.cos(theta) * ident
        + math.sin(theta) * skew
        + (1.0 - math.cos(theta)) * outer
    )


def rotate_fragment(
    coordinates: Sequence[Sequence[float]],
    fragment_indices: Iterable[int],
    *,
    pivot: Sequence[float],
    axis: Sequence[float],
    angle_rad: float,
) -> np.ndarray:
    """Rigidly rotate selected atoms around a fixed pivot and axis.

    Coordinates not named by fragment_indices are returned unchanged. The
    operation is purely geometric and does not run an electronic solver.
    """
    coords = np.asarray(coordinates, dtype=float)
    if coords.ndim != 2 or coords.shape[1] != 3 or coords.shape[0] < 1:
        raise OrientationScanError("coordinates must have shape (n_atoms, 3)")
    if not np.all(np.isfinite(coords)):
        raise OrientationScanError("coordinates must be finite")

    raw_indices = tuple(fragment_indices)
    if not raw_indices:
        raise OrientationScanError("fragment_indices must not be empty")
    indices_list: list[int] = []
    for value in raw_indices:
        if isinstance(value, (bool, np.bool_)):
            raise OrientationScanError("fragment indices must be integers")
        try:
            integer = int(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise OrientationScanError("fragment indices must be integers") from exc
        if integer != value:
            raise OrientationScanError("fragment indices must be integers")
        indices_list.append(integer)
    indices = tuple(indices_list)

    if len(set(indices)) != len(indices):
        raise OrientationScanError("fragment_indices must be unique")
    if any(i < 0 or i >= coords.shape[0] for i in indices):
        raise OrientationScanError("fragment index out of range")

    origin = _vector3(pivot, "pivot")
    rot = rotation_matrix(axis, angle_rad)
    out = coords.copy()
    for i in indices:
        out[i] = origin + rot @ (coords[i] - origin)
    return out


def xy2_rigid_orientation_coordinates(
    r_yy_angstrom: float,
    x_to_midpoint_angstrom: float,
    angle_rad: float,
) -> np.ndarray:
    """Return a rigid X...Y2 orientation-control geometry.

    Atom order is X, Y1, Y2. Y2 is fixed on the z axis with midpoint at the
    origin. X moves on a sphere of fixed radius D around that midpoint:

        X(theta) = (D sin(theta), 0, D cos(theta)).

    Thus r_YY and D are exact invariants while only relative orientation changes.
    """
    ryy = _finite(r_yy_angstrom, "r_yy_angstrom")
    distance = _finite(x_to_midpoint_angstrom, "x_to_midpoint_angstrom")
    theta = _finite(angle_rad, "angle_rad")
    if ryy <= 0.0:
        raise OrientationScanError("r_yy_angstrom must be positive")
    if distance <= 0.0:
        raise OrientationScanError("x_to_midpoint_angstrom must be positive")

    half = 0.5 * ryy
    return np.asarray(
        [
            [distance * math.sin(theta), 0.0, distance * math.cos(theta)],
            [0.0, 0.0, -half],
            [0.0, 0.0, half],
        ],
        dtype=float,
    )


@dataclass(frozen=True)
class PPOrientationControlPoint:
    angle_rad: float
    coupling_hartree: float
    lower_energy_hartree: float
    upper_energy_hartree: float
    gap_hartree: float

    def as_dict(self) -> dict[str, float | str]:
        data = asdict(self)
        data["schema"] = "RESCHEM_PP_ORIENTATION_CONTROL_V0_1"
        return data


def pp_two_orbital_hamiltonian(
    angle_rad: float,
    *,
    epsilon_a_hartree: float,
    epsilon_b_hartree: float,
    coupling_hartree: float,
) -> np.ndarray:
    """Two-orbital p-p control H(theta) with t(theta)=t0 cos(theta)."""
    theta = _finite(angle_rad, "angle_rad")
    ea = _finite(epsilon_a_hartree, "epsilon_a_hartree")
    eb = _finite(epsilon_b_hartree, "epsilon_b_hartree")
    t0 = _finite(coupling_hartree, "coupling_hartree")
    t = t0 * math.cos(theta)
    return np.asarray([[ea, t], [t, eb]], dtype=float)


def pp_orientation_control_point(
    angle_rad: float,
    *,
    epsilon_a_hartree: float,
    epsilon_b_hartree: float,
    coupling_hartree: float,
) -> PPOrientationControlPoint:
    theta = _finite(angle_rad, "angle_rad")
    h = pp_two_orbital_hamiltonian(
        theta,
        epsilon_a_hartree=epsilon_a_hartree,
        epsilon_b_hartree=epsilon_b_hartree,
        coupling_hartree=coupling_hartree,
    )
    energies = np.linalg.eigvalsh(h)
    t = float(h[0, 1])
    lower, upper = float(energies[0]), float(energies[1])
    return PPOrientationControlPoint(
        angle_rad=theta,
        coupling_hartree=t,
        lower_energy_hartree=lower,
        upper_energy_hartree=upper,
        gap_hartree=upper - lower,
    )


def scan_pp_orientation(
    angles_rad: Iterable[float],
    *,
    epsilon_a_hartree: float,
    epsilon_b_hartree: float,
    coupling_hartree: float,
) -> tuple[PPOrientationControlPoint, ...]:
    angles = tuple(_finite(value, "angle_rad") for value in angles_rad)
    if not angles:
        raise OrientationScanError("angles_rad must not be empty")
    return tuple(
        pp_orientation_control_point(
            theta,
            epsilon_a_hartree=epsilon_a_hartree,
            epsilon_b_hartree=epsilon_b_hartree,
            coupling_hartree=coupling_hartree,
        )
        for theta in angles
    )


__all__ = [
    "OrientationScanError",
    "PPOrientationControlPoint",
    "rotation_matrix",
    "rotate_fragment",
    "xy2_rigid_orientation_coordinates",
    "pp_two_orbital_hamiltonian",
    "pp_orientation_control_point",
    "scan_pp_orientation",
]
