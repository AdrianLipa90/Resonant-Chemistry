from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.linalg import eigh
from scipy.sparse.linalg import eigsh

from .atomic_hf_average import (
    _analytic_radial_matrices,
    _direct_potential,
    _eval_slater_basis,
    _exchange_matrix,
    _local_matrix,
    _orthonormalize_columns,
    _trap_weights,
)
from .atomic_radial_spectroscopy import HARTREE_TO_WAVENUMBER_CM
from .carbon_balanced_valence_ci import _selected_determinants
from .carbon_sparse_multichannel_ci import (
    SparseMultichannelTerm,
    _angular_one_body_operators,
    _casimir_from_sparse_ops,
    _quantum_number,
    _sparse_one_body,
    _sparse_two_body,
)

_TERM_LETTERS = "SPDFGHIKLMNOQRTUVWXYZ"


@dataclass(frozen=True)
class CarbonSparseVirtualSCIResult:
    spin_orbitals: int
    even_determinants: int
    requested_eigenpairs: int
    hamiltonian_nnz: int
    one_body_s_eigenvalues_hartree: tuple[float, ...]
    one_body_p_eigenvalues_hartree: tuple[float, ...]
    one_body_d_hartree: float
    terms: tuple[SparseMultichannelTerm, ...]

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
            "schema": "RESCHEM_CARBON_SPARSE_VIRTUAL_S_CI_V0_1",
            "active_space": "two radial s + two radial p + one radial d orbitals; four active electrons; even parity",
            "orbital_shape_source": "closed 1s^2 2s^2 reference Fock field",
            "active_one_body_operator": "nucleus plus frozen 1s^2 field projected into the reference-shaped s/p/d orbitals",
            "frozen_core": "1s^2",
            "spin_orbitals": self.spin_orbitals,
            "even_determinants": self.even_determinants,
            "requested_eigenpairs": self.requested_eigenpairs,
            "hamiltonian_nnz": self.hamiltonian_nnz,
            "one_body_s_eigenvalues_hartree": list(self.one_body_s_eigenvalues_hartree),
            "one_body_p_eigenvalues_hartree": list(self.one_body_p_eigenvalues_hartree),
            "one_body_d_hartree": self.one_body_d_hartree,
            "ground_term": self.ground_term,
            "terms": [term.as_dict() for term in self.terms],
            "method": "sparse frozen-orbital multichannel CI with explicit virtual s, radial p and d correlation",
            "limitations": [
                "1s^2 core frozen",
                "one virtual s, one virtual p and one d radial correlation channel only",
                "no state-averaged orbital optimization",
                "spin-orbit omitted in this electrostatic layer",
                "only requested low-energy eigenpairs are classified",
                "no experimental values enter the Hamiltonian",
                "TIR and affective mappings are not applied",
            ],
            "tir_status": "NOT_APPLIED_CONTROL_BASELINE",
            "affective_status": "RESERVED_UNASSIGNED",
        }


def _closed_reference_orbitals(
    *,
    basis_size: int,
    grid_points: int,
    tolerance_hartree: float,
    mixing: float = 0.30,
    max_iterations: int = 160,
):
    z = 6
    zetas = np.geomspace(0.02, 24.0, basis_size)
    r = np.geomspace(1.0e-8, 120.0, grid_points)
    weights = _trap_weights(r)

    s0, _, _, h0 = _analytic_radial_matrices(0, z, zetas)
    basis0 = _eval_slater_basis(0, zetas, r)
    _, coefficients = eigh(h0, s0, subset_by_index=[0, 1], check_finite=False)
    previous_energy = None
    converged = False
    final_fock_s = None

    for _iteration in range(1, max_iterations + 1):
        radials = basis0 @ coefficients
        density = 2.0 * np.sum(radials * radials, axis=1)
        direct = _local_matrix(basis0, _direct_potential(density, r), weights)
        exchange = np.zeros_like(h0)
        for column in range(2):
            exchange += _exchange_matrix(basis0, radials[:, column], r, weights, 0)
        fock_s = h0 + direct - exchange
        _, candidate = eigh(fock_s, s0, subset_by_index=[0, 1], check_finite=False)
        for column in range(2):
            if float(coefficients[:, column] @ s0 @ candidate[:, column]) < 0.0:
                candidate[:, column] *= -1.0
        coefficients = _orthonormalize_columns(
            (1.0 - mixing) * coefficients + mixing * candidate,
            s0,
        )
        radials = basis0 @ coefficients
        density = 2.0 * np.sum(radials * radials, axis=1)
        # SCF convergence diagnostic uses the sum of occupied Fock expectations;
        # only stationarity is needed here, not a separate total-energy receipt.
        energy_marker = sum(float(coefficients[:, c] @ fock_s @ coefficients[:, c]) for c in range(2))
        final_fock_s = fock_s
        if previous_energy is not None and abs(energy_marker - previous_energy) < tolerance_hartree:
            converged = True
            break
        previous_energy = energy_marker

    if not converged or final_fock_s is None:
        raise RuntimeError("closed carbon 1s2 2s2 orbital reference did not converge")

    occupied_radials = basis0 @ coefficients
    u1s = occupied_radials[:, 0]

    # Canonical full-reference s orbitals supply physical 2s and a first virtual s.
    eps_s_full, vec_s_full = eigh(
        final_fock_s,
        s0,
        subset_by_index=[0, 2],
        check_finite=False,
    )
    cs = vec_s_full[:, 1:3]
    s_radials = basis0 @ cs

    density_full = 2.0 * np.sum(occupied_radials * occupied_radials, axis=1)
    density_1s = 2.0 * u1s * u1s
    direct_full = _direct_potential(density_full, r)
    direct_1s = _direct_potential(density_1s, r)

    # Frozen-1s one-body operator in the chosen s reference-shaped subspace.
    fock_s_1s = h0 + _local_matrix(basis0, direct_1s, weights) - _exchange_matrix(
        basis0, u1s, r, weights, 0
    )
    h_s = cs.T @ fock_s_1s @ cs
    h_s = 0.5 * (h_s + h_s.T)

    # Two radial p orbitals shaped by the closed full reference, but evaluate
    # the active one-body block in the frozen-1s operator.
    s1, _, _, h1 = _analytic_radial_matrices(1, z, zetas)
    basis1 = _eval_slater_basis(1, zetas, r)
    fock_p_full = h1 + _local_matrix(basis1, direct_full, weights)
    for column in range(2):
        fock_p_full -= (1.0 / 3.0) * _exchange_matrix(
            basis1, occupied_radials[:, column], r, weights, 1
        )
    _, cp = eigh(fock_p_full, s1, subset_by_index=[0, 1], check_finite=False)
    p_radials = basis1 @ cp
    fock_p_1s = h1 + _local_matrix(basis1, direct_1s, weights) - (1.0 / 3.0) * _exchange_matrix(
        basis1, u1s, r, weights, 1
    )
    h_p = cp.T @ fock_p_1s @ cp
    h_p = 0.5 * (h_p + h_p.T)

    # One radial d orbital, again shaped by full reference and evaluated in
    # the frozen-1s active one-body operator.
    s2, _, _, h2 = _analytic_radial_matrices(2, z, zetas)
    basis2 = _eval_slater_basis(2, zetas, r)
    fock_d_full = h2 + _local_matrix(basis2, direct_full, weights)
    for column in range(2):
        fock_d_full -= (1.0 / 5.0) * _exchange_matrix(
            basis2, occupied_radials[:, column], r, weights, 2
        )
    _, cd = eigh(fock_d_full, s2, subset_by_index=[0, 0], check_finite=False)
    d_radial = basis2 @ cd[:, 0]
    fock_d_1s = h2 + _local_matrix(basis2, direct_1s, weights) - (1.0 / 5.0) * _exchange_matrix(
        basis2, u1s, r, weights, 2
    )
    h_d = float(cd[:, 0] @ fock_d_1s @ cd[:, 0])

    spatial = []
    for radial in range(2):
        spatial.append((f"s{radial}", 0, 0, s_radials[:, radial]))
    for radial in range(2):
        for m in (-1, 0, 1):
            spatial.append((f"p{radial}", 1, m, p_radials[:, radial]))
    for m in (-2, -1, 0, 1, 2):
        spatial.append(("d0", 2, m, d_radial))

    return r, weights, tuple(spatial), h_s, h_p, h_d


def _spin_orbitals(spatial):
    return tuple(
        (spatial_index, group, l, m, spin2)
        for spatial_index, (group, l, m, _) in enumerate(spatial)
        for spin2 in (-1, 1)
    )


def _one_body_matrix(spin_orbitals, h_s: np.ndarray, h_p: np.ndarray, h_d: float):
    matrix = np.zeros((len(spin_orbitals), len(spin_orbitals)), dtype=float)
    for i, (si, gi, li, mi, spi) in enumerate(spin_orbitals):
        for j, (sj, gj, lj, mj, spj) in enumerate(spin_orbitals):
            if spi != spj or li != lj or mi != mj:
                continue
            if li == 0:
                matrix[i, j] = h_s[int(gi[1:]), int(gj[1:])]
            elif li == 1:
                matrix[i, j] = h_p[int(gi[1:]), int(gj[1:])]
            elif li == 2 and gi == gj:
                matrix[i, j] = h_d
    return matrix


def solve_carbon_sparse_virtual_s_ci(
    *,
    basis_size: int = 18,
    grid_points: int = 800,
    tolerance_hartree: float = 1.0e-9,
    eigenpairs: int = 32,
) -> CarbonSparseVirtualSCIResult:
    """Sparse balanced carbon CI after opening the first virtual s channel."""
    r, weights, spatial, h_s, h_p, h_d = _closed_reference_orbitals(
        basis_size=basis_size,
        grid_points=grid_points,
        tolerance_hartree=tolerance_hartree,
    )
    spin_orbitals = _spin_orbitals(spatial)
    p_flags = tuple(l == 1 for _, _, l, _, _ in spin_orbitals)
    determinants = _selected_determinants(len(spin_orbitals), 4, p_flags)
    one_body = _one_body_matrix(spin_orbitals, h_s, h_p, h_d)
    hamiltonian = _sparse_one_body(one_body, determinants) + _sparse_two_body(
        spatial,
        spin_orbitals,
        determinants,
        r,
        weights,
    )
    hamiltonian = 0.5 * (hamiltonian + hamiltonian.T)

    k = min(eigenpairs, len(determinants) - 2)
    energies, vectors = eigsh(
        hamiltonian,
        k=k,
        which="SA",
        tol=1.0e-9,
        maxiter=12000,
    )
    order = np.argsort(energies)
    energies = energies[order]
    vectors = vectors[:, order]

    lz, lp, lm, sz, sp, sm = _angular_one_body_operators(spin_orbitals)
    lz_mb = _sparse_one_body(lz, determinants)
    lp_mb = _sparse_one_body(lp, determinants)
    lm_mb = _sparse_one_body(lm, determinants)
    sz_mb = _sparse_one_body(sz, determinants)
    sp_mb = _sparse_one_body(sp, determinants)
    sm_mb = _sparse_one_body(sm, determinants)

    ground = float(energies[0])
    best_by_term = {}
    for index in range(k):
        vector = vectors[:, index]
        l2 = _casimir_from_sparse_ops(vector, lz_mb, lp_mb, lm_mb)
        s2 = _casimir_from_sparse_ops(vector, sz_mb, sp_mb, sm_mb)
        L = int(round(_quantum_number(l2)))
        S = round(2.0 * _quantum_number(s2)) / 2.0
        symbol = f"^{int(round(2.0*S+1.0))}{_TERM_LETTERS[L]}"
        energy = float(energies[index])
        if symbol not in best_by_term or energy < best_by_term[symbol][0]:
            best_by_term[symbol] = (energy, L, S)

    terms = []
    for symbol, (energy, L, S) in sorted(best_by_term.items(), key=lambda item: item[1][0]):
        relative = energy - ground
        terms.append(
            SparseMultichannelTerm(
                term=symbol,
                relative_energy_hartree=relative,
                relative_energy_cm1=relative * HARTREE_TO_WAVENUMBER_CM,
                L=L,
                S=S,
            )
        )

    return CarbonSparseVirtualSCIResult(
        spin_orbitals=len(spin_orbitals),
        even_determinants=len(determinants),
        requested_eigenpairs=k,
        hamiltonian_nnz=int(hamiltonian.nnz),
        one_body_s_eigenvalues_hartree=tuple(float(v) for v in np.linalg.eigvalsh(h_s)),
        one_body_p_eigenvalues_hartree=tuple(float(v) for v in np.linalg.eigvalsh(h_p)),
        one_body_d_hartree=float(h_d),
        terms=tuple(terms),
    )
