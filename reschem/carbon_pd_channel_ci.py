from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.linalg import eigh

from .atomic_hf_average import (
    _analytic_radial_matrices,
    _direct_potential,
    _eval_slater_basis,
    _exchange_matrix,
    _local_matrix,
    _radial_kernel_apply,
)
from .carbon_balanced_valence_ci import (
    _classify_terms,
    _selected_determinants,
    _selected_ls_squared,
    _selected_one_body_matrix,
)
from .carbon_valence_ci import _mixed_angular_coulomb_coefficient
from .carbon_valence_ci_consistent import _solve_1s2_2s2_orbitals
from .multiplet_angular import _apply_two_body, _wigner_3j_int


@dataclass(frozen=True)
class CarbonPDChannelResult:
    spin_orbitals: int
    even_determinants: int
    p_radial_orbitals: int
    d_radial_orbitals: int
    one_body_p_hartree: tuple[float, ...]
    one_body_d_hartree: float
    terms: tuple

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
            "schema": "RESCHEM_CARBON_PD_CHANNEL_CI_V0_1",
            "active_space": "two radial p orbitals plus one radial d orbital; two active electrons; even-parity FCI",
            "frozen_core": "1s^2 2s^2",
            "spin_orbitals": self.spin_orbitals,
            "even_determinants": self.even_determinants,
            "p_radial_orbitals": self.p_radial_orbitals,
            "d_radial_orbitals": self.d_radial_orbitals,
            "one_body_p_hartree": list(self.one_body_p_hartree),
            "one_body_d_hartree": self.one_body_d_hartree,
            "ground_term": self.ground_term,
            "terms": [item.as_dict() for item in self.terms],
            "scope": "isolated p^2 <-> d^2 angular-correlation diagnostic on the established frozen 1s^2 2s^2 core",
            "limitations": [
                "2s is frozen and cannot participate explicitly",
                "only one radial d orbital is included",
                "spin-orbit is omitted in this channel diagnostic",
                "no experimental reference values are consumed",
                "TIR and affective mappings are not applied",
            ],
            "tir_status": "NOT_APPLIED_CONTROL_BASELINE",
            "affective_status": "RESERVED_UNASSIGNED",
        }


def _build_pd_orbitals(
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
    core_density = 2.0 * np.sum(core * core, axis=1)
    direct = _direct_potential(core_density, r)
    zetas = np.geomspace(0.02, 24.0, basis_size)

    s1, _, _, h1 = _analytic_radial_matrices(1, 6, zetas)
    basis1 = _eval_slater_basis(1, zetas, r)
    fock_p = h1 + _local_matrix(basis1, direct, weights)
    for column in range(2):
        fock_p -= (1.0 / 3.0) * _exchange_matrix(
            basis1, core[:, column], r, weights, 1
        )
    eps_p, coeff_p = eigh(
        fock_p,
        s1,
        subset_by_index=[0, 1],
        check_finite=False,
    )
    p_radials = basis1 @ coeff_p

    s2, _, _, h2 = _analytic_radial_matrices(2, 6, zetas)
    basis2 = _eval_slater_basis(2, zetas, r)
    fock_d = h2 + _local_matrix(basis2, direct, weights)
    for column in range(2):
        # s-d exchange has only k=2 and angular coefficient 1/(2l+1)=1/5.
        fock_d -= (1.0 / 5.0) * _exchange_matrix(
            basis2, core[:, column], r, weights, 2
        )
    eps_d, coeff_d = eigh(
        fock_d,
        s2,
        subset_by_index=[0, 0],
        check_finite=False,
    )
    d_radial = basis2 @ coeff_d[:, 0]

    spatial = []
    for radial in range(2):
        for m in (-1, 0, 1):
            spatial.append((f"p{radial}", 1, m, p_radials[:, radial], float(eps_p[radial])))
    for m in (-2, -1, 0, 1, 2):
        spatial.append(("d0", 2, m, d_radial, float(eps_d[0])))
    return reference, spatial, tuple(float(v) for v in eps_p), float(eps_d[0])


def _spin_orbitals(spatial):
    return tuple(
        (spatial_index, group, l, m, spin2)
        for spatial_index, (group, l, m, _, _) in enumerate(spatial)
        for spin2 in (-1, 1)
    )


def _radial_integrals(spatial, r, weights):
    cache = {}
    for a, (_, l1, _, ua, _) in enumerate(spatial):
        for c, (_, l3, _, uc, _) in enumerate(spatial):
            pair_ac = ua * uc
            for k in range(0, 5):
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


def _build_hamiltonian(spatial, spin_orbitals, determinants, r, weights):
    one_body = np.zeros((len(spin_orbitals), len(spin_orbitals)), dtype=float)
    for index, (spatial_index, _, _, _, _) in enumerate(spin_orbitals):
        one_body[index, index] = spatial[spatial_index][4]
    hamiltonian = _selected_one_body_matrix(one_body, determinants)
    determinant_index = {state: index for index, state in enumerate(determinants)}
    radial = _radial_integrals(spatial, r, weights)

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
                    for k in range(0, 5):
                        rv = radial.get((a, b, c, d, k))
                        if rv is None:
                            continue
                        value += rv * _mixed_angular_coulomb_coefficient(
                            l1,
                            m1,
                            l2,
                            m2,
                            l3,
                            m3,
                            l4,
                            m4,
                            k,
                        )
                    if abs(value) > 1.0e-13:
                        integrals.append((p, q, rr, s, 0.5 * value))

    for column, determinant in enumerate(determinants):
        for p, q, rr, s, value in integrals:
            applied = _apply_two_body(determinant, p, q, rr, s)
            if applied is None:
                continue
            target, sign = applied
            row = determinant_index.get(target)
            if row is not None:
                hamiltonian[row, column] += value * sign
    return 0.5 * (hamiltonian + hamiltonian.T)


def solve_carbon_pd_channel_ci(
    *,
    basis_size: int = 18,
    grid_points: int = 800,
    tolerance_hartree: float = 1.0e-9,
) -> CarbonPDChannelResult:
    """Isolate the virtual-d correlation channel for neutral carbon."""
    reference, spatial, eps_p, eps_d = _build_pd_orbitals(
        basis_size=basis_size,
        grid_points=grid_points,
        tolerance_hartree=tolerance_hartree,
    )
    spin_orbitals = _spin_orbitals(spatial)
    p_flags = tuple(l == 1 for _, _, l, _, _ in spin_orbitals)
    determinants = _selected_determinants(len(spin_orbitals), 2, p_flags)
    hamiltonian = _build_hamiltonian(
        spatial,
        spin_orbitals,
        determinants,
        reference.r,
        reference.weights,
    )
    l2, s2 = _selected_ls_squared(spatial, spin_orbitals, determinants)
    terms = _classify_terms(hamiltonian, l2, s2)
    return CarbonPDChannelResult(
        spin_orbitals=len(spin_orbitals),
        even_determinants=len(determinants),
        p_radial_orbitals=2,
        d_radial_orbitals=1,
        one_body_p_hartree=eps_p,
        one_body_d_hartree=eps_d,
        terms=terms,
    )
