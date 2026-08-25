"""Frozen angular basis states used by the first v0.15 B-Ne feature screen."""
from __future__ import annotations

import math

import numpy as np


P_ORBITAL_BASIS_ID = "RESCHEM_REAL_2P_BASIS_V0_15"


def real_p_coefficients(label: str) -> np.ndarray:
    """Return coefficients ordered by m=(-1,0,+1) for real 2p basis states."""
    key = label.strip().lower()
    scale = 1.0 / math.sqrt(2.0)
    if key == "p_x":
        return np.asarray([scale, 0.0, -scale], dtype=complex)
    if key == "p_y":
        return np.asarray([1j * scale, 0.0, 1j * scale], dtype=complex)
    if key == "p_z":
        return np.asarray([0.0, 1.0, 0.0], dtype=complex)
    raise ValueError(f"unsupported real 2p basis label: {label!r}")


def p_orbital_basis_manifest() -> dict:
    return {
        "schema": P_ORBITAL_BASIS_ID,
        "l": 1,
        "coefficient_order": [-1, 0, 1],
        "states": {
            label: [
                {"real": float(value.real), "imag": float(value.imag)}
                for value in real_p_coefficients(label)
            ]
            for label in ("p_x", "p_y", "p_z")
        },
        "status": "FROZEN_STAGE_A_ANGULAR_BASIS",
    }
