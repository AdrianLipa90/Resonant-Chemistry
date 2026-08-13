from __future__ import annotations

import numpy as np

from .atomic_hf_average import _radial_kernel_apply
from .carbon_balanced_valence_ci import (
    CarbonBalancedCIResult,
    _build_orbitals,
    _classify_terms,
    _mixed_angular_coulomb_coefficient,
    _one_body_spin_matrix,
    _selected_determinants,
    _selected_ls_squared,
    _selected_one_body_matrix,
    _spin_orbitals,
)
from .multiplet_angular import _apply_two_body, _wigner_3j_int


def _radial_mixed_integrals_v2(spatial, r, weights):
    """Mixed-l radial multipoles for the four-field balanced spatial record."""
    cache = {}
    for a, (_, l1, _, ua) in enumerate(spatial):
        for c, (_, l3, _, uc) in enumerate(spatial):
            pair_ac = ua * uc
            for k in range(0, 3):
                if abs(_wigner_3j_int(l1, k, l3, 0, 0, 0)) < 1.0e-15:
                    continue
                transformed = _radial_kernel_apply(pair_ac[:, None], r, k)[:, 0]
                for b, (_, l2, _, ub) in enumerate(spatial):
                    for d, (_, l4, _, ud) in enumerate(spatial):
                        if abs(_wigner_3j_int(l2, k, l4, 0, 0, 0)) < 1.0e-15:
                            continue
                        cache[(a, b, c, d, k)] = float(
                            np.sum(weights * ub * ud * transformed)
                        )
    return cache


def _build_even_hamiltonian_v2(
    spatial,
    spin_orbitals,
    determinants,
    one_body,
    r,
    weights,
):
    hamiltonian = _selected_one_body_matrix(one_body, determinants)
    determinant_index = {state: index for index, state in enumerate(determinants)}
    radial = _radial_mixed_integrals_v2(spatial, r, weights)

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
                        radial_value = radial.get((a, b, c, d, k))
                        if radial_value is None:
                            continue
                        value += radial_value * _mixed_angular_coulomb_coefficient(
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


def solve_carbon_balanced_valence_ci_v2(
    *,
    basis_size: int = 18,
    grid_points: int = 800,
    tolerance_hartree: float = 1.0e-9,
) -> CarbonBalancedCIResult:
    """Validated-shape adapter for the balanced 2s + two-radial-p CI model."""
    reference, spatial, h_s, h_p = _build_orbitals(
        basis_size=basis_size,
        grid_points=grid_points,
        tolerance_hartree=tolerance_hartree,
    )
    spin_orbitals = _spin_orbitals(spatial)
    p_flags = tuple(l == 1 for _, _, l, _, _ in spin_orbitals)
    determinants = _selected_determinants(len(spin_orbitals), 4, p_flags)
    one_body = _one_body_spin_matrix(spatial, spin_orbitals, h_s, h_p)
    hamiltonian = _build_even_hamiltonian_v2(
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
        one_body_p_eigenvalues_hartree=tuple(float(value) for value in np.linalg.eigvalsh(h_p)),
    )
