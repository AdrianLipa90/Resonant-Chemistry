from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .atomic_radial_spectroscopy import (
    HARTREE_TO_WAVENUMBER_CM,
    solve_period2_atom_specific_spectroscopy,
)
from .multiplet_angular import _one_body_many_body_matrix
from .multiplet_spin_orbit import _spin_orbit_one_body
from .period2_active_ci import (
    _active_ci_hamiltonian,
    _expanded_ls_squared,
    _expanded_spin_orbitals,
    _frozen_core_p_basis,
    _quantum_number_from_casimir,
)

_TERM_LETTERS = "SPDFGHIKLMNOQRTUVWXYZ"


@dataclass(frozen=True)
class CorrelatedFineStructureLevel:
    relative_energy_hartree: float
    relative_energy_cm1: float
    J: float
    approximate_L: int
    approximate_S: float
    degeneracy: int

    @property
    def approximate_term(self) -> str:
        multiplicity = int(round(2.0 * self.approximate_S + 1.0))
        return f"^{multiplicity}{_TERM_LETTERS[self.approximate_L]}"

    def as_dict(self) -> dict:
        return {
            "relative_energy_hartree": self.relative_energy_hartree,
            "relative_energy_cm^-1": self.relative_energy_cm1,
            "J": self.J,
            "approximate_LS_term": self.approximate_term,
            "degeneracy": self.degeneracy,
        }


@dataclass(frozen=True)
class Period2CorrelatedSpectrumResult:
    z: int
    p_electron_count: int
    determinant_count: int
    inherited_zeta_2p_hartree: float
    inherited_zeta_2p_cm1: float
    levels: tuple[CorrelatedFineStructureLevel, ...]

    @property
    def ground_level(self) -> CorrelatedFineStructureLevel:
        return self.levels[0]

    def as_dict(self) -> dict:
        return {
            "schema": "RESCHEM_PERIOD2_CORRELATED_SPECTRUM_V0_1",
            "Z": self.z,
            "p_electron_count": self.p_electron_count,
            "determinants": self.determinant_count,
            "spin_orbit": {
                "zeta_2p_hartree": self.inherited_zeta_2p_hartree,
                "zeta_2p_cm^-1": self.inherited_zeta_2p_cm1,
                "source": "previous atom-specific Pauli central-field control solver",
                "projection": "physical lowest radial 2p channel only",
                "virtual_radial_spin_orbit": "zero in v0.1; no inferred cross-radial zeta",
            },
            "levels": [level.as_dict() for level in self.levels],
            "scope": "correlated active-p electrostatic CI with conservative projected physical-2p spin-orbit rediagonalization",
            "limitations": [
                "frozen 1s^2 2s^2 core",
                "two radial p orbitals",
                "spin-orbit scale inherited from the prior nonrelativistic atom-specific control state",
                "spin-orbit on virtual and cross-radial p channels is deliberately omitted",
                "Breit and Dirac self-consistency are omitted",
                "TIR and affective mappings are not applied",
            ],
            "tir_status": "NOT_APPLIED_CONTROL_BASELINE",
            "affective_status": "RESERVED_UNASSIGNED",
        }


def _expanded_j_squared(radial_orbitals: int, electron_count: int) -> np.ndarray:
    orbitals = _expanded_spin_orbitals(radial_orbitals)
    lookup = {orbital: index for index, orbital in enumerate(orbitals)}
    size = len(orbitals)
    jz = np.zeros((size, size), dtype=float)
    jplus = np.zeros_like(jz)
    jminus = np.zeros_like(jz)

    for index, (radial, m, spin2) in enumerate(orbitals):
        jz[index, index] = m + spin2 / 2.0
        if m < 1:
            jplus[lookup[(radial, m + 1, spin2)], index] += math.sqrt(2.0 - m * (m + 1))
        if m > -1:
            jminus[lookup[(radial, m - 1, spin2)], index] += math.sqrt(2.0 - m * (m - 1))
        if spin2 == -1:
            jplus[lookup[(radial, m, 1)], index] += 1.0
        else:
            jminus[lookup[(radial, m, -1)], index] += 1.0

    jz_mb = _one_body_many_body_matrix(jz, electron_count)
    jp_mb = _one_body_many_body_matrix(jplus, electron_count)
    jm_mb = _one_body_many_body_matrix(jminus, electron_count)
    j2 = jz_mb @ jz_mb + 0.5 * (jp_mb @ jm_mb + jm_mb @ jp_mb)
    return 0.5 * (j2 + j2.T)


def _projected_physical_2p_spin_orbit(
    radial_orbitals: int,
    electron_count: int,
    zeta_2p_hartree: float,
) -> np.ndarray:
    if zeta_2p_hartree <= 0.0:
        raise ValueError("zeta_2p_hartree must be positive")
    orbitals = _expanded_spin_orbitals(radial_orbitals)
    one_body = np.zeros((len(orbitals), len(orbitals)), dtype=float)

    # _expanded_spin_orbitals stores the six m/spin states of radial channel 0
    # first.  Reuse the validated l=1 one-electron angular l.s operator there
    # and deliberately leave all virtual/cross-radial blocks zero.
    physical_block = _spin_orbit_one_body(1)
    one_body[: physical_block.shape[0], : physical_block.shape[1]] = (
        zeta_2p_hartree * physical_block
    )
    return _one_body_many_body_matrix(one_body, electron_count)


def _classify_correlated_levels(
    hamiltonian: np.ndarray,
    radial_orbitals: int,
    electron_count: int,
    *,
    degeneracy_tolerance_hartree: float = 1.0e-9,
):
    energies, eigenvectors = np.linalg.eigh(hamiltonian)
    l2, s2 = _expanded_ls_squared(radial_orbitals, electron_count)
    j2 = _expanded_j_squared(radial_orbitals, electron_count)
    ground = float(energies[0])

    levels: list[CorrelatedFineStructureLevel] = []
    start = 0
    while start < len(energies):
        stop = start + 1
        while stop < len(energies) and abs(float(energies[stop] - energies[start])) < degeneracy_tolerance_hartree:
            stop += 1
        vectors = eigenvectors[:, start:stop]
        j2_mean = float(np.mean(np.linalg.eigvalsh(vectors.T @ j2 @ vectors)))
        l2_mean = float(np.mean(np.linalg.eigvalsh(vectors.T @ l2 @ vectors)))
        s2_mean = float(np.mean(np.linalg.eigvalsh(vectors.T @ s2 @ vectors)))
        J = round(2.0 * _quantum_number_from_casimir(j2_mean)) / 2.0
        L = int(round(_quantum_number_from_casimir(l2_mean)))
        S = round(2.0 * _quantum_number_from_casimir(s2_mean)) / 2.0
        relative = float(energies[start]) - ground
        levels.append(
            CorrelatedFineStructureLevel(
                relative_energy_hartree=relative,
                relative_energy_cm1=relative * HARTREE_TO_WAVENUMBER_CM,
                J=J,
                approximate_L=L,
                approximate_S=S,
                degeneracy=stop - start,
            )
        )
        start = stop
    return tuple(levels)


def solve_period2_correlated_spectrum(
    z: int,
    *,
    radial_orbitals: int = 2,
    basis_size: int = 18,
    grid_points: int = 800,
    mixing: float = 0.30,
    tolerance_hartree: float = 1.0e-8,
    max_iterations: int = 120,
    spectroscopy_basis_size: int = 24,
    spectroscopy_grid_points: int = 1500,
) -> Period2CorrelatedSpectrumResult:
    """Rediagonalize the established physical-2p spin-orbit term in the CI space.

    The electrostatic Hamiltonian is the reference-isolated two-radial-p active
    CI model.  The only spin-orbit parameter is the atom-specific 2p zeta
    already derived by the preceding Pauli central-field control solver.  It is
    projected onto radial channel 0; no virtual or cross-radial zeta is invented.
    """
    state = _frozen_core_p_basis(
        z,
        radial_orbitals=radial_orbitals,
        basis_size=basis_size,
        grid_points=grid_points,
        mixing=mixing,
        tolerance_hartree=tolerance_hartree,
        max_iterations=max_iterations,
    )
    p_electrons = z - 4
    electrostatic, determinant_count = _active_ci_hamiltonian(
        p_electrons,
        state["p_orbital_energies"],
        state["p_radials"],
        state["r"],
        state["weights"],
    )
    previous = solve_period2_atom_specific_spectroscopy(
        z,
        basis_size=spectroscopy_basis_size,
        grid_points=spectroscopy_grid_points,
    )
    spin_orbit = _projected_physical_2p_spin_orbit(
        radial_orbitals,
        p_electrons,
        previous.zeta_2p_hartree,
    )
    levels = _classify_correlated_levels(
        electrostatic + spin_orbit,
        radial_orbitals,
        p_electrons,
    )
    return Period2CorrelatedSpectrumResult(
        z=z,
        p_electron_count=p_electrons,
        determinant_count=determinant_count,
        inherited_zeta_2p_hartree=previous.zeta_2p_hartree,
        inherited_zeta_2p_cm1=previous.zeta_2p_cm1,
        levels=levels,
    )


def solve_b_to_f_correlated_spectra(**kwargs) -> tuple[Period2CorrelatedSpectrumResult, ...]:
    return tuple(solve_period2_correlated_spectrum(z, **kwargs) for z in range(5, 10))
