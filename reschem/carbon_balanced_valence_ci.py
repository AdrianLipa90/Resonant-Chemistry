from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import math

import numpy as np
from scipy.linalg import eigh

from .atomic_hf_average import (
    _analytic_radial_matrices,
    _direct_potential,
    _eval_slater_basis,
    _exchange_matrix,
    _local_matrix,
    _radial_kernel_apply,
    _trap_weights,
)
from .atomic_radial_spectroscopy import HARTREE_TO_WAVENUMBER_CM
from .carbon_valence_ci import (
    _mixed_angular_coulomb_coefficient,
    _radial_mixed_integrals,
)
from .carbon_valence_ci_consistent import _solve_1s2_2s2_orbitals
from .multiplet_angular import _apply_one_body, _apply_two_body

_TERM_LETTERS = "SPDFGHIKLMNOQRTUVWXYZ"


@dataclass(frozen=True)
class CarbonBalancedTerm:
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
class CarbonBalancedCIResult:
    p_radial_orbitals: int
    spin_orbitals: int
    even_determinants: int
    terms: tuple[CarbonBalancedTerm, ...]
    one_body_s_hartree: float
    one_body_p_eigenvalues_hartree: tuple[float, ...]

    @property
    def ground_term(self) -> str:
        return self.terms[0].term

    def term_energy_cm1(self, term: str) -> float:
        for item in self.terms:
            if item.term == term:
                return item.relative_energy_cm1
        raise KeyError(term)

    def as_dict(self) -> dict:
        return {
            "schema": "RESCHEM_CARBON_BALANCED_VALENCE_CI_V0_1",
            "active_space": "physical 2s plus two radial p orbitals; four active electrons; even-parity full CI",
            "p_radial_orbitals": self.p_radial_orbitals,
            "spin_orbitals": self.spin_orbitals,
            "even_determinants": self.even_determinants,
            "one_body_s_hartree": self.one_body_s_hartree,
            "one_body_p_eigenvalues_hartree": list(self.one_body_p_eigenvalues_hartree),
            "ground_term": self.ground_term,
            "terms": [item.as_dict() for item in self.terms],
            "scope": "neutral carbon frozen-1s2 balanced valence correlation combining 2s participation with radial-p configuration interaction",
            "limitations": [
                "1s^2 core frozen",
                "two radial p orbitals only",
                "no virtual s or d orbitals beyond physical 2s",
                "electrostatic nonrelativistic term centers only",
                "TIR and affective mappings absent",
            ],
            "tir_status": "NOT_APPLIED_CONTROL_BASELINE",
            "affective_status": "RESERVED_UNASSIGNED",
        }


def _selected_determinants(n_spin_orbitals: int, electron_count: int, p_flags: tuple[bool, ...]):
    determinants = []
    for occupied in combinations(range(n_spin_orbitals), electron_count):
        p_count = sum(1 for index in occupied if p_flags[index])
        if p_count % 2 == 0:
            determinants.append(sum(1 << index for index in occupied))
    return tuple(determinants)


def _selected_one_body_matrix(one_body: np.ndarray, determinants: tuple[int, ...]) -> np.ndarray:
    lookup = {state: index for index, state in enumerate(determinants)}
    matrix = np.zeros((len(determinants), len(determinants)), dtype=float)
    nonzero = np.argwhere(np.abs(one_body) > 1.0e-14)
    for p, q in nonzero:
        value = float(one_body[p, q])
        for column, state in enumerate(determinants):
            applied = _apply_one_body(state, int(p), int(q))
            if applied is None:
                continue
            target, sign = applied
            row = lookup.get(target)
            if row is not None:
                matrix[row, column] += value * sign
    return matrix


def _build_orbitals(
    *,
    basis_size: int,
    grid_points: int,
    tolerance_hartree: float,
):
    reference = _solve_1s2_2s2_orbitals(
        6,
        basis_size=basis_size,
        grid_points=grid_points,
        tolerance_hartree=tolerance_hartree,
    )
    r = reference.r
    weights = reference.weights
    core = reference.core_radials
    u2s = core[:, 1]

    zetas = np.geomspace(0.02, max(20.0, 24.0), basis_size)
    s1, _, _, h1 = _analytic_radial_matrices(1, 6, zetas)
    basis1 = _eval_slater_basis(1, zetas, r)
    core_density = 2.0 * np.sum(core * core, axis=1)
    p_fock = h1 + _local_matrix(basis1, _direct_potential(core_density, r), weights)
    for column in range(2):
        p_fock -= (1.0 / 3.0) * _exchange_matrix(
            basis1, core[:, column], r, weights, 1
        )
    p_full_energies, p_coefficients = eigh(
        p_fock, s1, subset_by_index=[0, 1], check_finite=False
    )
    p_radials = basis1 @ p_coefficients

    # Remove active 2s^2 mean field from the p block.  The resulting one-body
    # operator is expressed in the two canonical p radial functions and may
    # therefore be non-diagonal after subtraction.
    v_2s = _direct_potential(u2s * u2s, r)
    j_matrix = p_radials.T @ ((weights * v_2s)[:, None] * p_radials)
    k_matrix = np.zeros((2, 2), dtype=float)
    for a in range(2):
        for b in range(2):
            product_a = p_radials[:, a] * u2s
            transformed = _radial_kernel_apply(product_a[:, None], r, 1)[:, 0]
            k_matrix[a, b] = (1.0 / 3.0) * float(
                np.sum(weights * u2s * p_radials[:, b] * transformed)
            )
    k_matrix = 0.5 * (k_matrix + k_matrix.T)
    h_p = np.diag(p_full_energies) - (2.0 * j_matrix - k_matrix)
    h_p = 0.5 * (h_p + h_p.T)

    # Remove the 2s self J contribution from its full-core Fock energy.
    j_ss = float(np.sum(weights * u2s * u2s * v_2s))
    h_s = reference.epsilon_2s_full_core_hartree - j_ss

    spatial = [("s0", 0, 0, u2s)]
    for radial in range(2):
        for m in (-1, 0, 1):
            spatial.append((f"p{radial}", 1, m, p_radials[:, radial]))
    return reference, spatial, h_s, h_p


def _spin_orbitals(spatial):
    return tuple(
        (index, group, l, m, spin2)
        for index, (group, l, m, _) in enumerate(spatial)
        for spin2 in (-1, 1)
    )


def _one_body_spin_matrix(spatial, spin_orbitals, h_s: float, h_p: np.ndarray):
    matrix = np.zeros((len(spin_orbitals), len(spin_orbitals)), dtype=float)
    for i, (si, gi, li, mi, spi) in enumerate(spin_orbitals):
        for j, (sj, gj, lj, mj, spj) in enumerate(spin_orbitals):
            if spi != spj or li != lj or mi != mj:
                continue
            if li == 0:
                if si == sj:
                    matrix[i, j] = h_s
            else:
                ri = int(gi[1:])
                rj = int(gj[1:])
                matrix[i, j] = h_p[ri, rj]
    return matrix


def _selected_ls_squared(spatial, spin_orbitals, determinants):
    lookup = {(group, l, m, spin2): index for index, (_, group, l, m, spin2) in enumerate(spin_orbitals)}
    size = len(spin_orbitals)
    lz = np.zeros((size, size), dtype=float)
    lp = np.zeros_like(lz)
    lm = np.zeros_like(lz)
    sz = np.zeros_like(lz)
    sp = np.zeros_like(lz)
    sm = np.zeros_like(lz)

    for index, (_, group, l, m, spin2) in enumerate(spin_orbitals):
        lz[index, index] = m
        sz[index, index] = spin2 / 2.0
        if m < l:
            target = lookup[(group, l, m + 1, spin2)]
            lp[target, index] = math.sqrt(l * (l + 1) - m * (m + 1))
        if m > -l:
            target = lookup[(group, l, m - 1, spin2)]
            lm[target, index] = math.sqrt(l * (l + 1) - m * (m - 1))
        if spin2 == -1:
            sp[lookup[(group, l, m, 1)], index] = 1.0
        else:
            sm[lookup[(group, l, m, -1)], index] = 1.0

    lz_mb = _selected_one_body_matrix(lz, determinants)
    lp_mb = _selected_one_body_matrix(lp, determinants)
    lm_mb = _selected_one_body_matrix(lm, determinants)
    sz_mb = _selected_one_body_matrix(sz, determinants)
    sp_mb = _selected_one_body_matrix(sp, determinants)
    sm_mb = _selected_one_body_matrix(sm, determinants)
    l2 = lz_mb @ lz_mb + 0.5 * (lp_mb @ lm_mb + lm_mb @ lp_mb)
    s2 = sz_mb @ sz_mb + 0.5 * (sp_mb @ sm_mb + sm_mb @ sp_mb)
    return 0.5 * (l2 + l2.T), 0.5 * (s2 + s2.T)


def _quantum_number(value: float) -> float:
    return 0.5 * (-1.0 + math.sqrt(max(0.0, 1.0 + 4.0 * value)))


def _build_even_hamiltonian(spatial, spin_orbitals, determinants, one_body, r, weights):
    hamiltonian = _selected_one_body_matrix(one_body, determinants)
    det_index = {state: index for index, state in enumerate(determinants)}
    radial = _radial_mixed_integrals(spatial, r, weights)

    integrals = []
    for p, (a, _, l1, m1, spin1) in enumerate(spin_orbitals):
        for q, (b, _, l2, m2, spin2) in enumerate(spin_orbitals):
            for rr, (c, _, l3, m3, spin3) in enumerate(spin_orbitals):
                if spin1 != spin3:
                    continue
                for s, (d, _, l4, m4, spin4) in enumerate(spin_orbitals):
                    if spin2 != spin4:
                        continue
                    value = 0.0
                    for k in range(0, 3):
                        rv = radial.get((a, b, c, d, k))
                        if rv is None:
                            continue
                        value += rv * _mixed_angular_coulomb_coefficient(
                            l1, m1, l2, m2, l3, m3, l4, m4, k
                        )
                    if abs(value) > 1.0e-13:
                        integrals.append((p, q, rr, s, 0.5 * value))

    for column, determinant in enumerate(determinants):
        for p, q, rr, s, value in integrals:
            applied = _apply_two_body(determinant, p, q, rr, s)
            if applied is None:
                continue
            target, sign = applied
            row = det_index.get(target)
            if row is not None:
                hamiltonian[row, column] += value * sign
    return 0.5 * (hamiltonian + hamiltonian.T)


def _classify_terms(hamiltonian, l2, s2):
    energies, eigenvectors = np.linalg.eigh(hamiltonian)
    classified = []
    start = 0
    while start < len(energies):
        stop = start + 1
        while stop < len(energies) and abs(float(energies[stop] - energies[start])) < 1.0e-8:
            stop += 1
        block = eigenvectors[:, start:stop]
        l_values, l_rotation = np.linalg.eigh(block.T @ l2 @ block)
        l_vectors = block @ l_rotation
        l_start = 0
        while l_start < len(l_values):
            l_stop = l_start + 1
            while l_stop < len(l_values) and abs(float(l_values[l_stop] - l_values[l_start])) < 1.0e-6:
                l_stop += 1
            L = int(round(_quantum_number(float(l_values[l_start]))))
            fixed_l = l_vectors[:, l_start:l_stop]
            s_values = np.linalg.eigvalsh(fixed_l.T @ s2 @ fixed_l)
            s_start = 0
            while s_start < len(s_values):
                s_stop = s_start + 1
                while s_stop < len(s_values) and abs(float(s_values[s_stop] - s_values[s_start])) < 1.0e-6:
                    s_stop += 1
                S = round(2.0 * _quantum_number(float(s_values[s_start]))) / 2.0
                classified.append((float(energies[start]), L, S, s_stop - s_start))
                s_start = s_stop
            l_start = l_stop
        start = stop

    classified.sort(key=lambda item: (item[0], item[1], item[2]))
    ground = classified[0][0]
    seen = set()
    terms = []
    for energy, L, S, degeneracy in classified:
        symbol = f"^{int(round(2*S+1))}{_TERM_LETTERS[L]}"
        if symbol in seen:
            continue
        seen.add(symbol)
        relative = energy - ground
        terms.append(
            CarbonBalancedTerm(
                term=symbol,
                relative_energy_hartree=relative,
                relative_energy_cm1=relative * HARTREE_TO_WAVENUMBER_CM,
                degeneracy=degeneracy,
            )
        )
    return tuple(terms)


def solve_carbon_balanced_valence_ci(
    *,
    basis_size: int = 18,
    grid_points: int = 800,
    tolerance_hartree: float = 1.0e-9,
) -> CarbonBalancedCIResult:
    """Combine explicit 2s valence participation with two-radial-p CI."""
    reference, spatial, h_s, h_p = _build_orbitals(
        basis_size=basis_size,
        grid_points=grid_points,
        tolerance_hartree=tolerance_hartree,
    )
    spin_orbitals = _spin_orbitals(spatial)
    p_flags = tuple(l == 1 for _, _, l, _, _ in spin_orbitals)
    determinants = _selected_determinants(len(spin_orbitals), 4, p_flags)
    one_body = _one_body_spin_matrix(spatial, spin_orbitals, h_s, h_p)
    hamiltonian = _build_even_hamiltonian(
        spatial,
        spin_orbitals,
        determinants,
        one_body,
        reference.r,
        reference.weights,
    )
    l2, s2 = _selected_ls_squared(spatial, spin_orbitals, determinants)
    terms = _classify_terms(hamiltonian, l2, s2)
    return CarbonBalancedCIResult(
        p_radial_orbitals=2,
        spin_orbitals=len(spin_orbitals),
        even_determinants=len(determinants),
        terms=terms,
        one_body_s_hartree=float(h_s),
        one_body_p_eigenvalues_hartree=tuple(float(v) for v in np.linalg.eigvalsh(h_p)),
    )
