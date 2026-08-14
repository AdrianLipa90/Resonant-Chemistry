"""Global numerical convergence scan for atomic neutral/ion controls.

v0.12A intentionally defines no numerical admission threshold.  It executes the
same explicit L0/L1/L2 parameter ladder for every state and records raw energy,
SCF convergence, virial residual, and adjacent-level drift.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Callable

from .atom import ELEMENT_SYMBOLS
from .atomic_hf_average import AverageAtomicHFResult
from .atomic_hf_diis import solve_atom_average_hf_diis


@dataclass(frozen=True)
class NumericalLevel:
    name: str
    basis_size: int
    grid_points: int
    zeta_min: float
    radial_grid_max_bohr: float
    damping: float
    diis_start: int
    diis_size: int
    max_iterations: int
    tolerance_hartree: float

    def solver_kwargs(self) -> dict:
        data = asdict(self)
        data.pop("name")
        return data


LEVELS = (
    NumericalLevel("L0", 20, 1000, 0.02, 120.0, 0.08, 10, 6, 700, 1e-6),
    NumericalLevel("L1", 24, 1400, 0.01, 180.0, 0.08, 10, 8, 900, 1e-6),
    NumericalLevel("L2", 28, 1800, 0.005, 240.0, 0.06, 12, 8, 1200, 1e-6),
)

StateSolver = Callable[..., AverageAtomicHFResult]


def run_atomic_state_scan(
    z: int,
    charge: int,
    *,
    solver: StateSolver = solve_atom_average_hf_diis,
) -> dict:
    rows = []
    for level in LEVELS:
        result = solver(z, charge, **level.solver_kwargs())
        energy = float(result.energy_hartree)
        virial = float(result.virial_residual_hartree)
        rows.append(
            {
                "level": level.name,
                "parameters": asdict(level),
                "configuration": result.configuration,
                "energy_hartree": energy,
                "energy_finite": isfinite(energy),
                "converged": bool(result.converged),
                "iterations": int(result.iterations),
                "virial_residual_hartree": virial,
                "virial_abs_hartree": abs(virial),
                "basis_size": int(result.basis_size),
                "grid_points": int(result.grid_points),
            }
        )

    drift = []
    for left, right in zip(rows, rows[1:]):
        delta = right["energy_hartree"] - left["energy_hartree"]
        drift.append(
            {
                "from": left["level"],
                "to": right["level"],
                "signed_energy_drift_hartree": delta,
                "absolute_energy_drift_hartree": abs(delta),
            }
        )

    return {
        "Z": z,
        "symbol": ELEMENT_SYMBOLS[z],
        "charge": charge,
        "levels": rows,
        "adjacent_energy_drift": drift,
        "status": "RAW_GLOBAL_NUMERICAL_SCAN_NO_CONVERGENCE_THRESHOLD",
    }


def state_label(z: int, charge: int) -> str:
    suffix = "+" if charge == 1 else ("-" if charge == -1 else "")
    return f"{ELEMENT_SYMBOLS[z]}{suffix}"
