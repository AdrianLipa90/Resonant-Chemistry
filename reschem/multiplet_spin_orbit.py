from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

import numpy as np

from .multiplet_angular import (
    ShellMultipletResult,
    _one_body_many_body_matrix,
    _spin_orbitals,
    _two_body_shell_hamiltonian,
    solve_equivalent_shell_multiplets,
)


@dataclass(frozen=True)
class SpinOrbitGroundResult:
    l: int
    electron_count: int
    zeta_units: float
    J: float
    degeneracy: int
    energy_units: float
    LS_ground_term: str

    def as_dict(self) -> dict:
        return {
            "schema": "RESCHEM_SPIN_ORBIT_GROUND_V0_1",
            "l": self.l,
            "electron_count": self.electron_count,
            "zeta_units": self.zeta_units,
            "LS_ground_term": self.LS_ground_term,
            "J": self.J,
            "degeneracy": self.degeneracy,
            "energy_units": self.energy_units,
            "scope": "dimensionless weak spin-orbit ordering on electrostatic shell multiplets",
            "absolute_fine_structure_splitting": "OPEN_ATOM_SPECIFIC_ZETA",
            "tir_status": "NOT_APPLIED_CONTROL_BASELINE",
            "affective_status": "NOT_APPLIED_CONTROL_BASELINE",
        }


def _spin_orbit_one_body(l: int) -> np.ndarray:
    orbitals = _spin_orbitals(l)
    lookup = {orbital: index for index, orbital in enumerate(orbitals)}
    matrix = np.zeros((len(orbitals), len(orbitals)), dtype=float)

    for index, (m, spin2) in enumerate(orbitals):
        matrix[index, index] += m * (spin2 / 2.0)

        # 1/2 L+ S-
        if spin2 == 1 and m < l:
            target = lookup[(m + 1, -1)]
            matrix[target, index] += 0.5 * sqrt(l * (l + 1) - m * (m + 1))

        # 1/2 L- S+
        if spin2 == -1 and m > -l:
            target = lookup[(m - 1, 1)]
            matrix[target, index] += 0.5 * sqrt(l * (l + 1) - m * (m - 1))

    return 0.5 * (matrix + matrix.T)


def _j_squared_many_body(l: int, electron_count: int) -> np.ndarray:
    orbitals = _spin_orbitals(l)
    lookup = {orbital: index for index, orbital in enumerate(orbitals)}
    size = len(orbitals)

    jz = np.zeros((size, size), dtype=float)
    jplus = np.zeros_like(jz)
    jminus = np.zeros_like(jz)

    for index, (m, spin2) in enumerate(orbitals):
        jz[index, index] = m + spin2 / 2.0

        if m < l:
            jplus[lookup[(m + 1, spin2)], index] += sqrt(l * (l + 1) - m * (m + 1))
        if m > -l:
            jminus[lookup[(m - 1, spin2)], index] += sqrt(l * (l + 1) - m * (m - 1))
        if spin2 == -1:
            jplus[lookup[(m, 1)], index] += 1.0
        else:
            jminus[lookup[(m, -1)], index] += 1.0

    jz_mb = _one_body_many_body_matrix(jz, electron_count)
    jp_mb = _one_body_many_body_matrix(jplus, electron_count)
    jm_mb = _one_body_many_body_matrix(jminus, electron_count)
    j2 = jz_mb @ jz_mb + 0.5 * (jp_mb @ jm_mb + jm_mb @ jp_mb)
    return 0.5 * (j2 + j2.T)


def _quantum_number_from_casimir(value: float) -> float:
    return 0.5 * (-1.0 + sqrt(max(0.0, 1.0 + 4.0 * value)))


def solve_spin_orbit_ground(
    l: int,
    electron_count: int,
    *,
    slater_parameters: dict[int, float] | None = None,
    zeta_units: float = 1.0e-3,
    ground_tolerance: float = 1.0e-8,
) -> SpinOrbitGroundResult:
    """Resolve the lowest J branch after weak one-electron l.s coupling.

    ``zeta_units`` is deliberately dimensionless in v0.1.  This resolves the
    angular ordering of J branches without claiming atom-specific fine-
    structure magnitudes.
    """
    if zeta_units <= 0.0:
        raise ValueError("zeta_units must be positive")

    ls_result: ShellMultipletResult = solve_equivalent_shell_multiplets(
        l,
        electron_count,
        slater_parameters=slater_parameters,
    )
    slater = ls_result.slater_parameters
    coulomb = _two_body_shell_hamiltonian(l, electron_count, slater)
    spin_orbit = _one_body_many_body_matrix(_spin_orbit_one_body(l), electron_count)
    j2 = _j_squared_many_body(l, electron_count)

    hamiltonian = coulomb + zeta_units * spin_orbit
    energies, eigenvectors = np.linalg.eigh(hamiltonian)
    ground_energy = float(energies[0])
    stop = 1
    while stop < len(energies) and abs(float(energies[stop]) - ground_energy) < ground_tolerance:
        stop += 1

    ground_vectors = eigenvectors[:, :stop]
    j2_values = np.linalg.eigvalsh(ground_vectors.T @ j2 @ ground_vectors)
    J = round(2.0 * _quantum_number_from_casimir(float(np.mean(j2_values)))) / 2.0

    return SpinOrbitGroundResult(
        l=l,
        electron_count=electron_count,
        zeta_units=zeta_units,
        J=J,
        degeneracy=stop,
        energy_units=ground_energy,
        LS_ground_term=ls_result.ground_term.symbol,
    )


def p_shell_ground_J_sequence() -> tuple[float, ...]:
    return tuple(solve_spin_orbit_ground(1, n).J for n in range(1, 7))


def d_shell_ground_J_sequence() -> tuple[float, ...]:
    return tuple(solve_spin_orbit_ground(2, n).J for n in range(1, 11))
