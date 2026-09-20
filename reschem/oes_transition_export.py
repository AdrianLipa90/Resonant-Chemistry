"""State-provider export surface for Orbital Eclipse Spectroscopy.

Resonant-Chemistry owns the state calculation and exports only typed state and
basis data needed by OES. It does not derive spectral line positions,
oscillator strengths, colors, or phase-microscope observables here.
"""
from __future__ import annotations

import math
from typing import Mapping, Sequence

import numpy as np

OES_SCHEMA_ID = "OES_TRANSITION_STATE_V0_1"
OES_TRANSITION_RDM_CONVENTION = "T_pq=<Psi_f|a_p^dagger a_q|Psi_i>"


def _finite(value: float, field: str) -> float:
    x = float(value)
    if not math.isfinite(x):
        raise ValueError(f"{field} must be finite")
    return x


def export_oes_transition_state(
    *,
    species_label: str,
    nuclei: Sequence[Mapping[str, object]],
    initial_label: str,
    initial_energy_hartree: float,
    final_label: str,
    final_energy_hartree: float,
    transition_rdm: np.ndarray,
    source_commit: str,
    method: str,
    orbital_basis_id: str,
    backend_status: str,
    initial_multiplicity: int | None = None,
    final_multiplicity: int | None = None,
    initial_symmetry: str | None = None,
    final_symmetry: str | None = None,
) -> dict[str, object]:
    """Emit a JSON-ready OES v0.1 transition packet without spectral inference."""
    if not species_label:
        raise ValueError("species_label is required")
    if not initial_label or not final_label:
        raise ValueError("state labels are required")
    if not source_commit or not method or not orbital_basis_id or not backend_status:
        raise ValueError("source_commit, method, orbital_basis_id and backend_status are required")

    initial_energy = _finite(initial_energy_hartree, "initial_energy_hartree")
    final_energy = _finite(final_energy_hartree, "final_energy_hartree")
    t = np.asarray(transition_rdm, dtype=complex)
    if t.ndim != 2 or t.shape[0] != t.shape[1] or t.shape[0] < 1:
        raise ValueError("transition_rdm must be a non-empty square matrix")
    if not np.all(np.isfinite(t.real)) or not np.all(np.isfinite(t.imag)):
        raise ValueError("transition_rdm must be finite")

    nuclear_framework = []
    for index, center in enumerate(nuclei):
        if not isinstance(center, Mapping):
            raise ValueError(f"nuclei[{index}] must be a mapping")
        label = str(center.get("label", ""))
        if not label:
            raise ValueError(f"nuclei[{index}].label is required")
        z = center.get("atomic_number")
        if isinstance(z, bool) or not isinstance(z, (int, np.integer)) or int(z) <= 0:
            raise ValueError(f"nuclei[{index}].atomic_number must be a positive integer")
        mass = _finite(center.get("mass_u"), f"nuclei[{index}].mass_u")
        if mass <= 0.0:
            raise ValueError(f"nuclei[{index}].mass_u must be positive")
        position = center.get("position_bohr")
        if not isinstance(position, Sequence) or isinstance(position, (str, bytes)) or len(position) != 3:
            raise ValueError(f"nuclei[{index}].position_bohr must have three coordinates")
        xyz = [_finite(value, f"nuclei[{index}].position_bohr") for value in position]
        nuclear_framework.append(
            {
                "label": label,
                "atomic_number": int(z),
                "mass_u": mass,
                "position_bohr": xyz,
            }
        )
    if not nuclear_framework:
        raise ValueError("at least one nuclear center is required")

    for name, multiplicity in (
        ("initial_multiplicity", initial_multiplicity),
        ("final_multiplicity", final_multiplicity),
    ):
        if multiplicity is not None and (
            isinstance(multiplicity, bool)
            or not isinstance(multiplicity, (int, np.integer))
            or int(multiplicity) < 1
        ):
            raise ValueError(f"{name} must be a positive integer when supplied")

    return {
        "schema": OES_SCHEMA_ID,
        "species_label": species_label,
        "transition_kind": "electronic",
        "nuclear_framework": nuclear_framework,
        "initial_state": {
            "label": initial_label,
            "energy_hartree": initial_energy,
            "multiplicity": initial_multiplicity,
            "symmetry": initial_symmetry,
        },
        "final_state": {
            "label": final_label,
            "energy_hartree": final_energy,
            "multiplicity": final_multiplicity,
            "symmetry": final_symmetry,
        },
        "transition_rdm": {
            "convention": OES_TRANSITION_RDM_CONVENTION,
            "real": t.real.tolist(),
            "imag": t.imag.tolist(),
        },
        "provenance": {
            "source_repository": "AdrianLipa90/Resonant-Chemistry",
            "source_commit": source_commit,
            "method": method,
            "orbital_basis_id": orbital_basis_id,
            "backend_status": backend_status,
        },
        "epistemic_status": "STANDARD_QM_STATE_PROVIDER_EXPORT",
        "spectral_inference": "NOT_PERFORMED_BY_RESONANT_CHEMISTRY",
    }


__all__ = [
    "OES_SCHEMA_ID",
    "OES_TRANSITION_RDM_CONVENTION",
    "export_oes_transition_state",
]
