from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
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
    _apply_two_body,
    _determinant_basis,
    _one_body_many_body_matrix,
    _wigner_3j_int,
)

_TERM_LETTERS = "SPDFGHIKLMNOQRTUVWXYZ"


@dataclass(frozen=True)
class CarbonValenceTerm:
    term: str
    parity: int
    relative_energy_hartree: float
    relative_energy_cm1: float
    degeneracy: int

    def as_dict(self) -> dict:
        return {
            "term": self.term,
            "parity": "even" if self.parity > 0 else "odd",
            "relative_energy_hartree": self.relative_energy_hartree,
            "relative_energy_cm^-1": self.relative_energy_cm1,
            "degeneracy": self.degeneracy,
        }


@dataclass(frozen=True)
class CarbonValenceCIResult:
    frozen_core: str
    active_space: str
    determinant_count: int
    core_iterations: int
    core_energy_hartree: float
    valence_s_energy_hartree: float
    valence_p_energy_hartree: float
    even_terms: tuple[CarbonValenceTerm, ...]

    @property
    def ground_term(self) -> str:
        return self.even_terms[0].term

    def term_energy_cm1(self, term: str) -> float:
        for item in self.even_terms:
            if item.term == term:
                return item.relative_energy_cm1
        raise KeyError(term)

    def as_dict(self) -> dict:
        return {
            "schema": "RESCHEM_CARBON_VALENCE_SP_CI_V0_1",
            "frozen_core": self.frozen_core,
            "active_space": self.active_space,
            "determinants": self.determinant_count,
            "core_iterations": self.core_iterations,
            "core_energy_hartree": self.core_energy_hartree,
            "valence_orbital_energies_hartree": {
                "2s": self.valence_s_energy_hartree,
                "2p": self.valence_p_energy_hartree,
            },
            "ground_term": self.ground_term,
            "even_terms": [item.as_dict() for item in self.even_terms],
            "scope": "neutral carbon frozen-1s2 full CI over the physical 2s and 2p valence shells",
            "limitations": [
                "1s^2 core is frozen",
                "no virtual 3s/3p/3d orbitals in v0.1",
                "electrostatic nonrelativistic term centers only",
                "spin-orbit is outside this layer",
                "no experimental reference values are consumed",
                "TIR and affective mappings are not applied",
            ],
            "tir_status": "NOT_APPLIED_CONTROL_BASELINE",
            "affective_status": "RESERVED_UNASSIGNED",
        }


@lru_cache(maxsize=None)
def _mixed_angular_coulomb_coefficient(
    l1: int,
    m1: int,
    l2: int,
    m2: int,
    l3: int,
    m3: int,
    l4: int,
    m4: int,
    k: int,
) -> float:
    """Angular factor for <l1m1,l2m2|r12^-1|l3m3,l4m4>."""
    if k < 0:
        return 0.0
    zero1 = _wigner_3j_int(l1, k, l3, 0, 0, 0)
    zero2 = _wigner_3j_int(l2, k, l4, 0, 0, 0)
    if abs(zero1) < 1.0e-15 or abs(zero2) < 1.0e-15:
        return 0.0
    pref1 = math.sqrt((2 * l1 + 1) * (2 * k + 1) * (2 * l3 + 1) / (4.0 * math.pi))
    pref2 = math.sqrt((2 * l2 + 1) * (2 * k + 1) * (2 * l4 + 1) / (4.0 * math.pi))
    total = 0.0
    for q in range(-k, k + 1):
        first = (
            (-1) ** (m1 + q)
            * pref1
            * zero1
            * _wigner_3j_int(l1, k, l3, -m1, -q, m3)
        )
        second = (
            (-1) ** m2
            * pref2
            * zero2
            * _wigner_3j_int(l2, k, l4, -m2, q, m4)
        )
        total += (4.0 * math.pi / (2 * k + 1)) * first * second
    return total


def _solve_frozen_1s_core(
    z: int,
    *,
    basis_size: int,
    grid_points: int,
    mixing: float,
    tolerance_hartree: float,
    max_iterations: int,
):
    zetas = np.geomspace(0.02, max(20.0, 4.0 * z), basis_size)
    r = np.geomspace(1.0e-8, 120.0, grid_points)
    weights = _trap_weights(r)

    s0, t0, v0, h0 = _analytic_radial_matrices(0, z, zetas)
    basis0 = _eval_slater_basis(0, zetas, r)
    _, vectors = eigh(h0, s0, subset_by_index=[0, 0], check_finite=False)
    core = vectors[:, 0].copy()

    previous_energy = None
    converged = False
    core_energy = float("nan")
    for iteration in range(1, max_iterations + 1):
        u = basis0 @ core
        density = 2.0 * u * u
        direct = _local_matrix(basis0, _direct_potential(density, r), weights)
        exchange = _exchange_matrix(basis0, u, r, weights, 0)
        fock = h0 + direct - exchange
        _, candidate = eigh(fock, s0, subset_by_index=[0, 0], check_finite=False)
        candidate = candidate[:, 0]
        if float(core @ s0 @ candidate) < 0.0:
            candidate *= -1.0
        core = _orthonormalize_columns(
            ((1.0 - mixing) * core + mixing * candidate)[:, None],
            s0,
        )[:, 0]

        u = basis0 @ core
        density = 2.0 * u * u
        h_expect = float(core @ (t0 + v0) @ core)
        j = _direct_potential(u * u, r)
        coulomb = float(np.sum(weights * u * u * j))
        core_energy = 2.0 * h_expect + coulomb
        if previous_energy is not None and abs(core_energy - previous_energy) < tolerance_hartree:
            converged = True
            break
        previous_energy = core_energy

    if not converged:
        raise RuntimeError("carbon frozen 1s2 core did not converge")

    core_u = basis0 @ core
    core_density = 2.0 * core_u * core_u
    direct_potential = _direct_potential(core_density, r)

    # Closed-core one-electron Fock operators for the valence shells.
    fock_s = h0 + _local_matrix(basis0, direct_potential, weights) - _exchange_matrix(
        basis0, core_u, r, weights, 0
    )
    s_energies, s_vectors = eigh(fock_s, s0, subset_by_index=[0, 1], check_finite=False)
    valence_s = s_vectors[:, 1]

    s1, _, _, h1 = _analytic_radial_matrices(1, z, zetas)
    basis1 = _eval_slater_basis(1, zetas, r)
    fock_p = h1 + _local_matrix(basis1, direct_potential, weights) - (1.0 / 3.0) * _exchange_matrix(
        basis1, core_u, r, weights, 1
    )
    p_energies, p_vectors = eigh(fock_p, s1, subset_by_index=[0, 0], check_finite=False)
    valence_p = p_vectors[:, 0]

    return {
        "r": r,
        "weights": weights,
        "core_energy": core_energy,
        "iterations": iteration,
        "valence_s": basis0 @ valence_s,
        "valence_p": basis1 @ valence_p,
        "epsilon_s": float(s_energies[1]),
        "epsilon_p": float(p_energies[0]),
    }


def _active_spatial_orbitals(state):
    # shell index, l, m, radial function, one-body energy
    out = [(0, 0, 0, state["valence_s"], state["epsilon_s"])]
    for m in (-1, 0, 1):
        out.append((1, 1, m, state["valence_p"], state["epsilon_p"]))
    return tuple(out)


def _active_spin_orbitals(spatial):
    return tuple(
        (spatial_index, l, m, spin2)
        for spatial_index, (_, l, m, _, _) in enumerate(spatial)
        for spin2 in (-1, 1)
    )


def _radial_mixed_integrals(spatial, r, weights):
    cache = {}
    for a, (_, l1, _, ua, _) in enumerate(spatial):
        for c, (_, l3, _, uc, _) in enumerate(spatial):
            pair_ac = ua * uc
            for k in range(0, 3):
                if abs(_wigner_3j_int(l1, k, l3, 0, 0, 0)) < 1.0e-15:
                    continue
                transformed = _radial_kernel_apply(pair_ac[:, None], r, k)[:, 0]
                for b, (_, l2, _, ub, _) in enumerate(spatial):
                    for d, (_, l4, _, ud, _) in enumerate(spatial):
                        if abs(_wigner_3j_int(l2, k, l4, 0, 0, 0)) < 1.0e-15:
                            continue
                        cache[(a, b, c, d, k)] = float(
                            np.sum(weights * ub * ud * transformed)
                        )
    return cache


def _mixed_ls_squared(spin_orbitals, electron_count: int):
    lookup = {orbital: index for index, orbital in enumerate(spin_orbitals)}
    size = len(spin_orbitals)
    lz = np.zeros((size, size), dtype=float)
    lp = np.zeros_like(lz)
    lm = np.zeros_like(lz)
    sz = np.zeros_like(lz)
    sp = np.zeros_like(lz)
    sm = np.zeros_like(lz)

    # Map (shell/spatial identity by l manifold, m, spin) within the physical s/p set.
    by_l_m_spin = {}
    for index, (spatial_index, l, m, spin2) in enumerate(spin_orbitals):
        by_l_m_spin[(l, m, spin2)] = index
        lz[index, index] = m
        sz[index, index] = spin2 / 2.0

    for index, (_, l, m, spin2) in enumerate(spin_orbitals):
        if m < l and (l, m + 1, spin2) in by_l_m_spin:
            lp[by_l_m_spin[(l, m + 1, spin2)], index] = math.sqrt(l * (l + 1) - m * (m + 1))
        if m > -l and (l, m - 1, spin2) in by_l_m_spin:
            lm[by_l_m_spin[(l, m - 1, spin2)], index] = math.sqrt(l * (l + 1) - m * (m - 1))
        if spin2 == -1:
            sp[by_l_m_spin[(l, m, 1)], index] = 1.0
        else:
            sm[by_l_m_spin[(l, m, -1)], index] = 1.0

    lz_mb = _one_body_many_body_matrix(lz, electron_count)
    lp_mb = _one_body_many_body_matrix(lp, electron_count)
    lm_mb = _one_body_many_body_matrix(lm, electron_count)
    sz_mb = _one_body_many_body_matrix(sz, electron_count)
    sp_mb = _one_body_many_body_matrix(sp, electron_count)
    sm_mb = _one_body_many_body_matrix(sm, electron_count)
    l2 = lz_mb @ lz_mb + 0.5 * (lp_mb @ lm_mb + lm_mb @ lp_mb)
    s2 = sz_mb @ sz_mb + 0.5 * (sp_mb @ sm_mb + sm_mb @ sp_mb)
    return 0.5 * (l2 + l2.T), 0.5 * (s2 + s2.T)


def _quantum_number_from_casimir(value: float) -> float:
    return 0.5 * (-1.0 + math.sqrt(max(0.0, 1.0 + 4.0 * value)))


def _build_valence_hamiltonian(state, electron_count: int = 4):
    spatial = _active_spatial_orbitals(state)
    spin_orbitals = _active_spin_orbitals(spatial)
    determinants = _determinant_basis(len(spin_orbitals), electron_count)
    det_index = {det: index for index, det in enumerate(determinants)}

    one_body = np.zeros((len(spin_orbitals), len(spin_orbitals)), dtype=float)
    for index, (spatial_index, _, _, _) in enumerate(spin_orbitals):
        one_body[index, index] = spatial[spatial_index][4]
    hamiltonian = _one_body_many_body_matrix(one_body, electron_count)

    radial = _radial_mixed_integrals(spatial, state["r"], state["weights"])
    integrals = []
    for p, (a, l1, m1, spin1) in enumerate(spin_orbitals):
        for q, (b, l2, m2, spin2) in enumerate(spin_orbitals):
            for rr, (c, l3, m3, spin3) in enumerate(spin_orbitals):
                if spin1 != spin3:
                    continue
                for s, (d, l4, m4, spin4) in enumerate(spin_orbitals):
                    if spin2 != spin4:
                        continue
                    value = 0.0
                    for k in range(0, 3):
                        radial_value = radial.get((a, b, c, d, k))
                        if radial_value is None:
                            continue
                        value += radial_value * _mixed_angular_coulomb_coefficient(
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
            hamiltonian[det_index[target], column] += value * sign

    # Parity = (-1)^(number of p electrons) for this s/p active space.
    parity = np.empty(len(determinants), dtype=float)
    for index, determinant in enumerate(determinants):
        p_count = 0
        for orbital_index, (_, l, _, _) in enumerate(spin_orbitals):
            if l == 1 and ((determinant >> orbital_index) & 1):
                p_count += 1
        parity[index] = 1.0 if p_count % 2 == 0 else -1.0

    return 0.5 * (hamiltonian + hamiltonian.T), spin_orbitals, determinants, parity


def _classify_even_terms(hamiltonian, spin_orbitals, parity_diag, electron_count: int = 4):
    energies, eigenvectors = np.linalg.eigh(hamiltonian)
    l2, s2 = _mixed_ls_squared(spin_orbitals, electron_count)
    parity_matrix = np.diag(parity_diag)
    classified = []

    start = 0
    while start < len(energies):
        stop = start + 1
        while stop < len(energies) and abs(float(energies[stop] - energies[start])) < 1.0e-8:
            stop += 1
        block = eigenvectors[:, start:stop]
        parity_values, parity_rotation = np.linalg.eigh(block.T @ parity_matrix @ block)
        parity_vectors = block @ parity_rotation

        p_start = 0
        while p_start < len(parity_values):
            p_stop = p_start + 1
            while p_stop < len(parity_values) and abs(float(parity_values[p_stop] - parity_values[p_start])) < 1.0e-7:
                p_stop += 1
            parity = 1 if float(parity_values[p_start]) >= 0.0 else -1
            fixed_p = parity_vectors[:, p_start:p_stop]
            l_values, l_rotation = np.linalg.eigh(fixed_p.T @ l2 @ fixed_p)
            l_vectors = fixed_p @ l_rotation

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
                    classified.append((float(energies[start]), parity, L, S, s_stop - s_start))
                    s_start = s_stop
                l_start = l_stop
            p_start = p_stop
        start = stop

    even = [item for item in classified if item[1] > 0]
    even.sort(key=lambda item: (item[0], item[2], item[3]))
    ground = even[0][0]
    seen = set()
    terms = []
    for energy, parity, L, S, degeneracy in even:
        multiplicity = int(round(2.0 * S + 1.0))
        symbol = f"^{multiplicity}{_TERM_LETTERS[L]}"
        if symbol in seen:
            continue
        seen.add(symbol)
        relative = energy - ground
        terms.append(
            CarbonValenceTerm(
                term=symbol,
                parity=parity,
                relative_energy_hartree=relative,
                relative_energy_cm1=relative * HARTREE_TO_WAVENUMBER_CM,
                degeneracy=degeneracy,
            )
        )
    return tuple(terms)


def solve_carbon_valence_sp_ci(
    *,
    basis_size: int = 18,
    grid_points: int = 800,
    mixing: float = 0.30,
    tolerance_hartree: float = 1.0e-9,
    max_iterations: int = 120,
) -> CarbonValenceCIResult:
    """Frozen-1s2 FCI over physical carbon 2s and 2p valence shells."""
    state = _solve_frozen_1s_core(
        6,
        basis_size=basis_size,
        grid_points=grid_points,
        mixing=mixing,
        tolerance_hartree=tolerance_hartree,
        max_iterations=max_iterations,
    )
    hamiltonian, spin_orbitals, determinants, parity = _build_valence_hamiltonian(state, 4)
    terms = _classify_even_terms(hamiltonian, spin_orbitals, parity, 4)
    return CarbonValenceCIResult(
        frozen_core="1s^2",
        active_space="physical 2s + 2p; four active valence electrons; full CI",
        determinant_count=len(determinants),
        core_iterations=int(state["iterations"]),
        core_energy_hartree=float(state["core_energy"]),
        valence_s_energy_hartree=float(state["epsilon_s"]),
        valence_p_energy_hartree=float(state["epsilon_p"]),
        even_terms=terms,
    )
