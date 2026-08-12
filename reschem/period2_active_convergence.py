from __future__ import annotations

from dataclasses import dataclass
import math

from .period2_active_ci import solve_period2_active_p_ci


@dataclass(frozen=True)
class ActiveSpaceConvergencePoint:
    radial_orbitals: int
    spin_orbitals: int
    determinant_count: int
    ground_term: str
    term_centers_cm1: dict[str, float]

    def as_dict(self) -> dict:
        return {
            "radial_p_orbitals": self.radial_orbitals,
            "spin_orbitals": self.spin_orbitals,
            "determinants": self.determinant_count,
            "ground_term": self.ground_term,
            "term_centers_cm^-1": self.term_centers_cm1,
        }


def solve_carbon_active_space_convergence(
    *,
    radial_spaces: tuple[int, ...] = (2, 3, 4),
    basis_size: int = 18,
    grid_points: int = 800,
) -> tuple[ActiveSpaceConvergencePoint, ...]:
    """Probe finite-active-space convergence for neutral carbon.

    Carbon is used as the first convergence diagnostic because p^2 keeps the
    determinant spaces tractable while retaining the singlet correlation
    problem exposed by the previous spectroscopy benchmark.  No experimental
    energies are used by this routine.
    """
    if not radial_spaces:
        raise ValueError("radial_spaces cannot be empty")
    if any(value < 2 for value in radial_spaces):
        raise ValueError("each active space must contain at least two radial p orbitals")

    points = []
    for radial_orbitals in radial_spaces:
        result = solve_period2_active_p_ci(
            6,
            radial_orbitals=radial_orbitals,
            basis_size=max(basis_size, radial_orbitals + 8),
            grid_points=grid_points,
        )
        spin_orbitals = 6 * radial_orbitals
        expected_determinants = math.comb(spin_orbitals, 2)
        if result.determinant_count != expected_determinants:
            raise RuntimeError("active-space determinant count invariant failed")
        points.append(
            ActiveSpaceConvergencePoint(
                radial_orbitals=radial_orbitals,
                spin_orbitals=spin_orbitals,
                determinant_count=result.determinant_count,
                ground_term=result.ground_term,
                term_centers_cm1={
                    "^1D": result.term_energy_cm1("^1D"),
                    "^1S": result.term_energy_cm1("^1S"),
                },
            )
        )
    return tuple(points)
