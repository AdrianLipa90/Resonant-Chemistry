"""Global L3 continuation for the preregistered atomic-ion scan.

v0.12B adds exactly one common numerical level after v0.12A.  It does not
select a convergence threshold and does not modify the L0/L1/L2 history.
"""
from __future__ import annotations

from dataclasses import asdict
from math import isfinite
from typing import Callable

from .atomic_hf_average import AverageAtomicHFResult
from .atomic_hf_diis import solve_atom_average_hf_diis
from .atomic_ion_convergence import NumericalLevel
from .atom import ELEMENT_SYMBOLS

L3 = NumericalLevel(
    name="L3",
    basis_size=32,
    grid_points=2200,
    zeta_min=0.0025,
    radial_grid_max_bohr=300.0,
    damping=0.06,
    diis_start=12,
    diis_size=8,
    max_iterations=1500,
    tolerance_hartree=1e-6,
)

StateSolver = Callable[..., AverageAtomicHFResult]


def run_l3_state(
    z: int,
    charge: int,
    *,
    solver: StateSolver = solve_atom_average_hf_diis,
) -> dict:
    result = solver(z, charge, **L3.solver_kwargs())
    energy = float(result.energy_hartree)
    virial = float(result.virial_residual_hartree)
    return {
        "Z": z,
        "symbol": ELEMENT_SYMBOLS[z],
        "charge": charge,
        "level": "L3",
        "parameters": asdict(L3),
        "configuration": result.configuration,
        "energy_hartree": energy,
        "energy_finite": isfinite(energy),
        "converged": bool(result.converged),
        "iterations": int(result.iterations),
        "virial_residual_hartree": virial,
        "virial_abs_hartree": abs(virial),
        "basis_size": int(result.basis_size),
        "grid_points": int(result.grid_points),
        "status": "RAW_GLOBAL_L3_CONTINUATION_NO_CONVERGENCE_THRESHOLD",
    }
