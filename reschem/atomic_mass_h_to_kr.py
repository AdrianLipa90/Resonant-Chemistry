from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .atomic_hf_diis import RobustAtomicHFResult, solve_atom_average_hf_robust


K_TO_KR_Z = tuple(range(19, 37))
H_TO_KR_Z = tuple(range(1, 37))


@dataclass(frozen=True)
class AtomicMassBatchResult:
    start_z: int
    end_z: int
    results: tuple[RobustAtomicHFResult, ...]

    @property
    def quality_pass_count(self) -> int:
        return sum(int(item.quality_pass) for item in self.results)

    @property
    def all_quality_pass(self) -> bool:
        return self.quality_pass_count == len(self.results)

    @property
    def worst_abs_virial_hartree(self) -> float:
        return max(abs(item.result.virial_residual_hartree) for item in self.results)

    def as_dict(self) -> dict:
        return {
            "schema": "RESCHEM_ATOMIC_MASS_BATCH_V0_1",
            "range": [self.start_z, self.end_z],
            "species_count": len(self.results),
            "quality_pass_count": self.quality_pass_count,
            "all_quality_pass": self.all_quality_pass,
            "worst_abs_virial_hartree": self.worst_abs_virial_hartree,
            "results": [
                {
                    "Z": item.result.z,
                    "configuration": item.result.configuration,
                    "energy_hartree": item.result.energy_hartree,
                    "virial_residual_hartree": item.result.virial_residual_hartree,
                    "stage": item.stage,
                    "quality_pass": item.quality_pass,
                }
                for item in self.results
            ],
            "control_contract": {
                "reference_values_available_to_solver": False,
                "element_specific_solver_branches": False,
                "tir_corrections_applied": False,
                "affective_mapping_applied": False,
            },
        }


def solve_atomic_range_robust(
    atomic_numbers: Iterable[int],
    *,
    virial_gate_hartree: float = 2.0,
    tolerance_hartree: float = 1e-6,
) -> AtomicMassBatchResult:
    zs = tuple(int(z) for z in atomic_numbers)
    if not zs:
        raise ValueError("atomic_numbers cannot be empty")
    if min(zs) < 1 or max(zs) > 36:
        raise ValueError("v0.1 mass solver supports H..Kr (Z=1..36)")
    results = tuple(
        solve_atom_average_hf_robust(
            z,
            virial_gate_hartree=virial_gate_hartree,
            tolerance_hartree=tolerance_hartree,
        )
        for z in zs
    )
    return AtomicMassBatchResult(min(zs), max(zs), results)


def solve_k_to_kr_robust(**kwargs) -> AtomicMassBatchResult:
    return solve_atomic_range_robust(K_TO_KR_Z, **kwargs)


def solve_h_to_kr_robust(**kwargs) -> AtomicMassBatchResult:
    return solve_atomic_range_robust(H_TO_KR_Z, **kwargs)
