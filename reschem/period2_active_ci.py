from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.linalg import eigh

from .atomic_hf_average import (
    _analytic_radial_matrices,
    _direct_potential,
    _eval_slater_basis,
    _exchange_matrix,
    _local_matrix,
    _orthonormalize_columns,
    _radial_kernel_apply,
    _trap_weights,
)
from .atomic_radial_spectroscopy import HARTREE_TO_WAVENUMBER_CM
from .multiplet_angular import (
    _angular_coulomb_coefficient,
    _apply_two_body,
    _determinant_basis,
    _one_body_many_body_matrix,
)

_TERM_LETTERS = "SPDFGHIKLMNOQRTUVWXYZ"


@dataclass(frozen=True)
class CorrelatedTermCenter:
    term: str
    relative_energy_hartree: float
    relative_energy_cm1: float
    degeneracy: int

    def as_dict(self) -> dict:
        return {
            "term": self.term,
            "relative_energy_hartree": self.relative_energy_hartree,
            "relative_energy_cm^-1": self.relative_energy_cm1,
            "degeneracy": self.degeneracy,
        }


@dataclass(frozen=True)
class Period2ActiveCIResult:
    z: int
    p_electron_count: int
    radial_orbitals: int
    determinant_count: int
    frozen_core_iterations: int
    frozen_core_energy_hartree: float
    p_orbital_energies_hartree: tuple[float, ...]
    term_centers: tuple[CorrelatedTermCenter, ...]

    @property
    def ground_term(self) -> str:
        return self.term_centers[0].term

    def term_energy_cm1(self, term: str) -> float:
        for item in self.term_centers:
            if item.term == term:
                return item.relative_energy_cm1
        raise KeyError(term)

    def as_dict(self) -> dict:
        return {
            "schema": "RESCHEM_PERIOD2_ACTIVE_P_CI_V0_1",
            "Z": self.z,
            "p_electron_count": self.p_electron_count,
            "active_space": {
                "frozen_core": "1s^2 2s^2",
                "l": 1,
                "radial_p_orbitals": self.radial_orbitals,
                "determinants": self.determinant_count,
                "virtual_configuration_mixing": "enabled automatically by FCI in the active p space",
            },
            "frozen_core_iterations": self.frozen_core_iterations,
            "frozen_core_energy_hartree": self.frozen_core_energy_hartree,
            "p_orbital_energies_hartree": list(self.p_orbital_energies_hartree),
            "ground_term": self.ground_term,
            "term_centers": [item.as_dict() for item in self.term_centers],
            "scope": "frozen-core nonrelativistic active-space CI for neutral B-Ne; two or more radial p orbitals; electrostatic term centers",
            "limitations": [
                "1s^2 2s^2 core is frozen and does not relax against the correlated active state",
                "default v0.1 active space contains only two radial p orbitals",
                "s/d virtual correlation and core-valence correlation are omitted",
                "spin-orbit fine structure is not rediagonalized in this layer",
                "no experimental reference values are consumed by the solver",
                "TIR and affective mappings are not applied",
            ],
            "tir_status": "NOT_APPLIED_CONTROL_BASELINE",
            "affective_status": "RESERVED_UNASSIGNED",
        }


def _frozen_core_p_basis(
    z: int,
    *,
    radial_orbitals: int,
    basis_size: int,
    grid_points: int,
    mixing: float,
    tolerance_hartree: float,
    max_iterations: int,
):
    if not (5 <= z <= 10):
        raise ValueError("period-2 active CI supports neutral B-Ne (Z=5..10)")
    if radial_orbitals < 2:
        raise ValueError("radial_orbitals must be >= 2")
    if basis_size < radial_orbitals + 6:
        raise ValueError("basis_size is too small for the requested active space")
    if grid_points < 400:
        raise ValueError("grid_points must be >= 400")
    if not (0.0 < mixing <= 1.0):
        raise ValueError("mixing must be in (0,1]")

    zetas = np.geomspace(0.02, max(20.0, 4.0 * z), basis_size)
    r = np.geomspace(1.0e-8, 120.0, grid_points)
    weights = _trap_weights(r)

    s0, t0, v0, h0 = _analytic_radial_matrices(0, z, zetas)
    basis0 = _eval_slater_basis(0, zetas, r)
    _, coefficients = eigh(h0, s0, subset_by_index=[0, 1], check_finite=False)

    previous_energy = None
    converged = False
    core_energy = float("nan")
    for iteration in range(1, max_iterations + 1):
        spatial = basis0 @ coefficients
        core_density = 2.0 * np.sum(spatial * spatial, axis=1)
        direct = _local_matrix(basis0, _direct_potential(core_density, r), weights)
        exchange = np.zeros_like(h0)
        for column in range(2):
            exchange += _exchange_matrix(basis0, spatial[:, column], r, weights, 0)
        fock = h0 + direct - exchange
        _, candidate = eigh(fock, s0, subset_by_index=[0, 1], check_finite=False)
        for column in range(2):
            if float(coefficients[:, column] @ s0 @ candidate[:, column]) < 0.0:
                candidate[:, column] *= -1.0
        coefficients = _orthonormalize_columns(
            (1.0 - mixing) * coefficients + mixing * candidate,
            s0,
        )

        spatial = basis0 @ coefficients
        core_density = 2.0 * np.sum(spatial * spatial, axis=1)
        direct_potential = _direct_potential(core_density, r)
        one_body_energy = 2.0 * sum(
            float(coefficients[:, column] @ (t0 + v0) @ coefficients[:, column])
            for column in range(2)
        )
        direct_energy = 0.5 * float(np.sum(weights * core_density * direct_potential))
        exchange_energy = 0.0
        for a in range(2):
            for b in range(2):
                product = spatial[:, a] * spatial[:, b]
                transformed = _radial_kernel_apply(product[:, None], r, 0)[:, 0]
                exchange_energy -= float(np.sum(weights * product * transformed))
        core_energy = one_body_energy + direct_energy + exchange_energy

        if previous_energy is not None and abs(core_energy - previous_energy) < tolerance_hartree:
            converged = True
            break
        previous_energy = core_energy

    if not converged:
        raise RuntimeError(f"frozen 1s2 2s2 core did not converge for Z={z}")

    core_spatial = basis0 @ coefficients
    core_density = 2.0 * np.sum(core_spatial * core_spatial, axis=1)

    s1, _, _, h1 = _analytic_radial_matrices(1, z, zetas)
    basis1 = _eval_slater_basis(1, zetas, r)
    p_fock = h1 + _local_matrix(basis1, _direct_potential(core_density, r), weights)
    for column in range(2):
        # For a p electron interacting with a closed s shell, exchange is the k=1 channel.
        p_fock -= (1.0 / 3.0) * _exchange_matrix(
            basis1,
            core_spatial[:, column],
            r,
            weights,
            1,
        )

    orbital_energies, p_coefficients = eigh(
        p_fock,
        s1,
        subset_by_index=[0, radial_orbitals - 1],
        check_finite=False,
    )
    p_radials = basis1 @ p_coefficients
    return {
        "r": r,
        "weights": weights,
        "p_radials": p_radials,
        "p_orbital_energies": orbital_energies,
        "core_energy": core_energy,
        "core_iterations": iteration,
    }


def _radial_multipoles(p_radials: np.ndarray, r: np.ndarray, weights: np.ndarray):
    n = p_radials.shape[1]
    out: dict[tuple[int, int, int, int, int], float] = {}
    for a in range(n):
        for c in range(n):
            pair_ac = p_radials[:, a] * p_radials[:, c]
            for k in (0, 2):
                transformed = _radial_kernel_apply(pair_ac[:, None], r, k)[:, 0]
                for b in range(n):
                    for d in range(n):
                        pair_bd = p_radials[:, b] * p_radials[:, d]
                        out[(a, b, c, d, k)] = float(
                            np.sum(weights * pair_bd * transformed)
                        )
    return out


def _expanded_spin_orbitals(radial_orbitals: int):
    return tuple(
        (radial, m, spin2)
        for radial in range(radial_orbitals)
        for m in (-1, 0, 1)
        for spin2 in (-1, 1)
    )


def _expanded_ls_squared(radial_orbitals: int, electron_count: int):
    orbitals = _expanded_spin_orbitals(radial_orbitals)
    lookup = {orbital: index for index, orbital in enumerate(orbitals)}
    size = len(orbitals)

    lz = np.zeros((size, size), dtype=float)
    lplus = np.zeros_like(lz)
    lminus = np.zeros_like(lz)
    sz = np.zeros_like(lz)
    splus = np.zeros_like(lz)
    sminus = np.zeros_like(lz)

    for index, (radial, m, spin2) in enumerate(orbitals):
        lz[index, index] = m
        sz[index, index] = spin2 / 2.0
        if m < 1:
            lplus[lookup[(radial, m + 1, spin2)], index] = math.sqrt(2.0 - m * (m + 1))
        if m > -1:
            lminus[lookup[(radial, m - 1, spin2)], index] = math.sqrt(2.0 - m * (m - 1))
        if spin2 == -1:
            splus[lookup[(radial, m, 1)], index] = 1.0
        else:
            sminus[lookup[(radial, m, -1)], index] = 1.0

    lz_mb = _one_body_many_body_matrix(lz, electron_count)
    lp_mb = _one_body_many_body_matrix(lplus, electron_count)
    lm_mb = _one_body_many_body_matrix(lminus, electron_count)
    sz_mb = _one_body_many_body_matrix(sz, electron_count)
    sp_mb = _one_body_many_body_matrix(splus, electron_count)
    sm_mb = _one_body_many_body_matrix(sminus, electron_count)

    l2 = lz_mb @ lz_mb + 0.5 * (lp_mb @ lm_mb + lm_mb @ lp_mb)
    s2 = sz_mb @ sz_mb + 0.5 * (sp_mb @ sm_mb + sm_mb @ sp_mb)
    return 0.5 * (l2 + l2.T), 0.5 * (s2 + s2.T)


def _quantum_number_from_casimir(value: float) -> float:
    return 0.5 * (-1.0 + math.sqrt(max(0.0, 1.0 + 4.0 * value)))


def _active_ci_hamiltonian(
    electron_count: int,
    orbital_energies: np.ndarray,
    p_radials: np.ndarray,
    r: np.ndarray,
    weights: np.ndarray,
):
    radial_orbitals = p_radials.shape[1]
    orbitals = _expanded_spin_orbitals(radial_orbitals)
    determinants = _determinant_basis(len(orbitals), electron_count)
    determinant_index = {det: index for index, det in enumerate(determinants)}

    one_body = np.zeros((len(orbitals), len(orbitals)), dtype=float)
    for index, (radial, _, _) in enumerate(orbitals):
        one_body[index, index] = float(orbital_energies[radial])
    hamiltonian = _one_body_many_body_matrix(one_body, electron_count)

    radial = _radial_multipoles(p_radials, r, weights)
    integrals = []
    for p, (a, m1, spin1) in enumerate(orbitals):
        for q, (b, m2, spin2) in enumerate(orbitals):
            for rr, (c, m3, spin3) in enumerate(orbitals):
                if spin1 != spin3:
                    continue
                for s, (d, m4, spin4) in enumerate(orbitals):
                    if spin2 != spin4:
                        continue
                    value = 0.0
                    for k in (0, 2):
                        value += radial[(a, b, c, d, k)] * _angular_coulomb_coefficient(
                            1, m1, m2, m3, m4, k
                        )
                    if abs(value) > 1.0e-13:
                        integrals.append((p, q, rr, s, 0.5 * value))

    for column, determinant in enumerate(determinants):
        for p, q, rr, s, value in integrals:
            applied = _apply_two_body(determinant, p, q, rr, s)
            if applied is None:
                continue
            target, sign = applied
            hamiltonian[determinant_index[target], column] += value * sign

    return 0.5 * (hamiltonian + hamiltonian.T), len(determinants)


def _classify_term_centers(
    hamiltonian: np.ndarray,
    radial_orbitals: int,
    electron_count: int,
    *,
    energy_tolerance_hartree: float = 1.0e-7,
):
    energies, eigenvectors = np.linalg.eigh(hamiltonian)
    l2, s2 = _expanded_ls_squared(radial_orbitals, electron_count)

    classified: list[tuple[float, int, float, int]] = []
    start = 0
    while start < len(energies):
        stop = start + 1
        while stop < len(energies) and abs(float(energies[stop] - energies[start])) < energy_tolerance_hartree:
            stop += 1
        energy_vectors = eigenvectors[:, start:stop]
        l_values, l_rotation = np.linalg.eigh(energy_vectors.T @ l2 @ energy_vectors)
        l_vectors = energy_vectors @ l_rotation

        l_start = 0
        while l_start < len(l_values):
            l_stop = l_start + 1
            while l_stop < len(l_values) and abs(float(l_values[l_stop] - l_values[l_start])) < 1.0e-6:
                l_stop += 1
            L = int(round(_quantum_number_from_casimir(float(l_values[l_start]))))
            fixed_l = l_vectors[:, l_start:l_stop]
            s_values = np.linalg.eigvalsh(fixed_l.T @ s2 @ fixed_l)

            s_start = 0
            while s_start < len(s_values):
                s_stop = s_start + 1
                while s_stop < len(s_values) and abs(float(s_values[s_stop] - s_values[s_start])) < 1.0e-6:
                    s_stop += 1
                S = round(2.0 * _quantum_number_from_casimir(float(s_values[s_start]))) / 2.0
                classified.append((float(energies[start]), L, S, s_stop - s_start))
                s_start = s_stop
            l_start = l_stop
        start = stop

    classified.sort(key=lambda item: (item[0], item[1], item[2]))
    ground = classified[0][0]
    seen: set[str] = set()
    terms: list[CorrelatedTermCenter] = []
    for energy, L, S, degeneracy in classified:
        multiplicity = int(round(2.0 * S + 1.0))
        symbol = f"^{multiplicity}{_TERM_LETTERS[L]}"
        if symbol in seen:
            continue
        seen.add(symbol)
        relative = energy - ground
        terms.append(
            CorrelatedTermCenter(
                term=symbol,
                relative_energy_hartree=relative,
                relative_energy_cm1=relative * HARTREE_TO_WAVENUMBER_CM,
                degeneracy=degeneracy,
            )
        )
    return tuple(terms)


def solve_period2_active_p_ci(
    z: int,
    *,
    radial_orbitals: int = 2,
    basis_size: int = 18,
    grid_points: int = 800,
    mixing: float = 0.30,
    tolerance_hartree: float = 1.0e-8,
    max_iterations: int = 120,
) -> Period2ActiveCIResult:
    """Frozen-core active-space CI for neutral period-2 p-shell atoms.

    The core is solved self-consistently as 1s^2 2s^2.  The active one-electron
    p basis is obtained from that frozen-core Fock operator.  Electron-electron
    interaction among the active p electrons is then diagonalized exactly in
    the finite determinant space using radial multipoles R^0 and R^2.

    No empirical term energies, NIST values, fitted Slater parameters, TIR
    corrections, or affective parameters enter the Hamiltonian.
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
    hamiltonian, determinant_count = _active_ci_hamiltonian(
        p_electrons,
        state["p_orbital_energies"],
        state["p_radials"],
        state["r"],
        state["weights"],
    )
    terms = _classify_term_centers(hamiltonian, radial_orbitals, p_electrons)
    return Period2ActiveCIResult(
        z=z,
        p_electron_count=p_electrons,
        radial_orbitals=radial_orbitals,
        determinant_count=determinant_count,
        frozen_core_iterations=int(state["core_iterations"]),
        frozen_core_energy_hartree=float(state["core_energy"]),
        p_orbital_energies_hartree=tuple(float(value) for value in state["p_orbital_energies"]),
        term_centers=terms,
    )


def solve_b_to_f_active_ci(**kwargs) -> tuple[Period2ActiveCIResult, ...]:
    return tuple(solve_period2_active_p_ci(z, **kwargs) for z in range(5, 10))
