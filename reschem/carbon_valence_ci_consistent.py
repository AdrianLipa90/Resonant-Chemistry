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
    _orthonormalize_columns,
    _radial_kernel_apply,
    _trap_weights,
)
from .carbon_valence_ci import (
    CarbonValenceCIResult,
    _build_valence_hamiltonian,
    _classify_even_terms,
)


@dataclass(frozen=True)
class ConsistentOrbitalState:
    r: np.ndarray
    weights: np.ndarray
    core_energy_hartree: float
    iterations: int
    core_radials: np.ndarray
    valence_p: np.ndarray
    epsilon_2s_full_core_hartree: float
    epsilon_2p_full_core_hartree: float
    h_frozen_1s_2s_hartree: float
    h_frozen_1s_2p_hartree: float


def _solve_1s2_2s2_orbitals(
    z: int = 6,
    *,
    basis_size: int = 18,
    grid_points: int = 800,
    mixing: float = 0.30,
    tolerance_hartree: float = 1.0e-9,
    max_iterations: int = 160,
) -> ConsistentOrbitalState:
    """Solve the closed 1s2 2s2 reference and expose 1s,2s,2p orbitals.

    The same closed-s-shell radial HF structure used by the preceding active-p
    layer is retained.  The resulting 2s/2p radial shapes are then reused as a
    basis for an open-valence CI, while the 2s mean field is analytically
    removed from the active one-body energies to avoid double counting.
    """
    zetas = np.geomspace(0.02, max(20.0, 4.0 * z), basis_size)
    r = np.geomspace(1.0e-8, 120.0, grid_points)
    weights = _trap_weights(r)

    s0, t0, v0, h0 = _analytic_radial_matrices(0, z, zetas)
    basis0 = _eval_slater_basis(0, zetas, r)
    _, coefficients = eigh(h0, s0, subset_by_index=[0, 1], check_finite=False)

    previous_energy = None
    converged = False
    core_energy = float("nan")
    final_fock = None
    for iteration in range(1, max_iterations + 1):
        spatial = basis0 @ coefficients
        density = 2.0 * np.sum(spatial * spatial, axis=1)
        direct = _local_matrix(basis0, _direct_potential(density, r), weights)
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
        density = 2.0 * np.sum(spatial * spatial, axis=1)
        direct_potential = _direct_potential(density, r)
        one_body_energy = 2.0 * sum(
            float(coefficients[:, column] @ (t0 + v0) @ coefficients[:, column])
            for column in range(2)
        )
        direct_energy = 0.5 * float(np.sum(weights * density * direct_potential))
        exchange_energy = 0.0
        for a in range(2):
            for b in range(2):
                product = spatial[:, a] * spatial[:, b]
                transformed = _radial_kernel_apply(product[:, None], r, 0)[:, 0]
                exchange_energy -= float(np.sum(weights * product * transformed))
        core_energy = one_body_energy + direct_energy + exchange_energy
        final_fock = fock

        if previous_energy is not None and abs(core_energy - previous_energy) < tolerance_hartree:
            converged = True
            break
        previous_energy = core_energy

    if not converged or final_fock is None:
        raise RuntimeError("1s2 2s2 reference did not converge")

    core_radials = basis0 @ coefficients
    epsilon_2s = float(coefficients[:, 1] @ final_fock @ coefficients[:, 1])

    density = 2.0 * np.sum(core_radials * core_radials, axis=1)
    direct_potential = _direct_potential(density, r)
    s1, _, _, h1 = _analytic_radial_matrices(1, z, zetas)
    basis1 = _eval_slater_basis(1, zetas, r)
    p_fock = h1 + _local_matrix(basis1, direct_potential, weights)
    for column in range(2):
        p_fock -= (1.0 / 3.0) * _exchange_matrix(
            basis1, core_radials[:, column], r, weights, 1
        )
    p_energies, p_vectors = eigh(p_fock, s1, subset_by_index=[0, 0], check_finite=False)
    valence_p = basis1 @ p_vectors[:, 0]
    epsilon_2p = float(p_energies[0])

    u2s = core_radials[:, 1]
    u2p = valence_p
    # Remove the active 2s mean field from the closed-core Fock energies.
    # For the 2s orbital itself, 2J_2s-K_2s contributes J_2s.
    j_ss_potential = _direct_potential(u2s * u2s, r)
    j_ss = float(np.sum(weights * u2s * u2s * j_ss_potential))

    # For 2p in the closed 2s^2 field, the contribution is 2J(2p,2s)-K(2p,2s).
    j_ps = float(np.sum(weights * u2p * u2p * j_ss_potential))
    product = u2p * u2s
    k1 = _radial_kernel_apply(product[:, None], r, 1)[:, 0]
    # The s-p exchange angular coefficient is 1/3 for each p magnetic state.
    k_ps = (1.0 / 3.0) * float(np.sum(weights * product * k1))

    return ConsistentOrbitalState(
        r=r,
        weights=weights,
        core_energy_hartree=core_energy,
        iterations=iteration,
        core_radials=core_radials,
        valence_p=valence_p,
        epsilon_2s_full_core_hartree=epsilon_2s,
        epsilon_2p_full_core_hartree=epsilon_2p,
        h_frozen_1s_2s_hartree=epsilon_2s - j_ss,
        h_frozen_1s_2p_hartree=epsilon_2p - (2.0 * j_ps - k_ps),
    )


def solve_carbon_valence_sp_ci_consistent(
    *,
    basis_size: int = 18,
    grid_points: int = 800,
    mixing: float = 0.30,
    tolerance_hartree: float = 1.0e-9,
    max_iterations: int = 160,
) -> CarbonValenceCIResult:
    """Open 2s/2p carbon FCI with orbitals from the established closed-core field.

    The physical 2s and 2p radial functions are taken from the converged
    1s^2 2s^2 reference used by the prior period-2 control stack.  The active
    2s mean field is then removed from the one-body energies before explicit
    2s/2p electron-electron interaction is restored by FCI.  This preserves
    radial consistency while avoiding mean-field double counting.
    """
    orbital_state = _solve_1s2_2s2_orbitals(
        6,
        basis_size=basis_size,
        grid_points=grid_points,
        mixing=mixing,
        tolerance_hartree=tolerance_hartree,
        max_iterations=max_iterations,
    )
    state = {
        "r": orbital_state.r,
        "weights": orbital_state.weights,
        "core_energy": orbital_state.core_energy_hartree,
        "iterations": orbital_state.iterations,
        "valence_s": orbital_state.core_radials[:, 1],
        "valence_p": orbital_state.valence_p,
        "epsilon_s": orbital_state.h_frozen_1s_2s_hartree,
        "epsilon_p": orbital_state.h_frozen_1s_2p_hartree,
    }
    hamiltonian, spin_orbitals, determinants, parity = _build_valence_hamiltonian(state, 4)
    terms = _classify_even_terms(hamiltonian, spin_orbitals, parity, 4)
    return CarbonValenceCIResult(
        frozen_core="1s^2",
        active_space="physical 2s + 2p FCI; radial shapes from converged 1s^2 2s^2 reference; active-2s mean field removed",
        determinant_count=len(determinants),
        core_iterations=orbital_state.iterations,
        core_energy_hartree=orbital_state.core_energy_hartree,
        valence_s_energy_hartree=orbital_state.h_frozen_1s_2s_hartree,
        valence_p_energy_hartree=orbital_state.h_frozen_1s_2p_hartree,
        even_terms=terms,
    )
