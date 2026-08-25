"""Axis-resolved phase diagnostics for the v0.15 TIR tetrahedral SIC layer."""
from __future__ import annotations

from typing import Sequence

from .tetrahedral_inference_v015 import dominant_harmonic, tetrahedral_phase_trace


AXIS_RESOLVED_PHASE_CONTRACT_ID = "RESCHEM_TIR_TETRAHEDRAL_SIC_AXIS_RESOLVED_PHASE_V0_15_R2"
CARTESIAN_ROTATION_AXES = {
    "x": (1.0, 0.0, 0.0),
    "y": (0.0, 1.0, 0.0),
    "z": (0.0, 0.0, 1.0),
}


def axis_resolved_tetrahedral_harmonics(
    bloch_vector: Sequence[float],
    *,
    cone_index: int = 0,
    phase_samples: int = 128,
) -> dict:
    rows = {}
    for label, axis in CARTESIAN_ROTATION_AXES.items():
        trace = tetrahedral_phase_trace(
            bloch_vector,
            cone_index=cone_index,
            rotation_axis=axis,
            phase_samples=phase_samples,
        )
        order, strength = dominant_harmonic(trace)
        rows[label] = {
            "rotation_axis": list(axis),
            "dominant_harmonic_order": int(order),
            "dominant_harmonic_strength": float(strength),
        }
    return {
        "schema": AXIS_RESOLVED_PHASE_CONTRACT_ID,
        "cone_index": int(cone_index),
        "phase_samples": int(phase_samples),
        "axes": rows,
        "selection_status": "ALL_PREREGISTERED_AXES_PRESERVED",
        "spectral_join": "WITHHELD_FOR_BLIND_COMPARISON",
    }
