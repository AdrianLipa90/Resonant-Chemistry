from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.linalg import eigh
from scipy.sparse import coo_matrix, csr_matrix
from scipy.sparse.linalg import eigsh

from .atomic_hf_average import (
    _analytic_radial_matrices,
    _direct_potential,
    _eval_slater_basis,
    _exchange_matrix,
    _local_matrix,
    _radial_kernel_apply,
)
from .atomic_radial_spectroscopy import HARTREE_TO_WAVENUMBER_CM
from .carbon_balanced_valence_ci import (
    _build_orbitals,
    _selected_determinants,
)
from .carbon_valence_ci import _mixed_angular_coulomb_coefficient
from .multiplet_angular import (
    _apply_one_body,
    _apply_two_body,
    _wigner_3j_int,
)

_TERM_LETTERS = "SPDFGHIKLMNOQRTUVWXYZ"


@dataclass(frozen=True)
class SparseMultichannelTerm:
    term: str
    relative_energy_hartree: float
    relative_energy_cm1: float
    L: int
    S: float

    def as_dict(self) -> dict:
        return {
            "term": self.term,
            "L": self.L,
            "S": self.S,
            "relative_energy_hartree": self.relative_energy_hartree,
            "relative_energy_cm^-1": self.relative_energy_cm1,
        }


@dataclass(frozen=True)
class CarbonSparseMultichannelCIResult:
    spin_orbitals: int
    even_determinants: int
    requested_eigenpairs: int
    one_body_s_hartree: float
    one_body_p_eigenvalues_hartree: tuple[float, ...]
    one_body_d_hartree: float
    hamiltonian_nnz: int
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
            "schema": "RESCHEM_CARBON_SPARSE_MULTICHANNEL_CI_V0_1",
            "active_space": "physical 2s + two radial p orbitals + one radial d orbital; four active electrons; even parity",
            "frozen_core": "1s^2",
            "spin_orbitals": self.spin_orbitals,
            "even_determinants": self.even_determinants,
            "requested_eigenpairs": self.requested_eigenpairs,
            "hamiltonian_nnz": self.hamiltonian_nnz,
            "one_body_s_hartree": self.one_body_s_hartree,
            "one_body_p_eigenvalues_hartree": list(self.one_body_p_eigenvalues_hartree),
            "one_body_d_hartree": self.one_body_d_hartree,
            "ground_term": self.ground_term,
            "terms": [term.as_dict() for term in self.terms],
            "method": "sparse symmetry-preserving CI; lowest eigenpairs from scipy.sparse.linalg.eigsh; LS labels from Casimir expectations",
            "limitations": [
                "1s^2 core frozen",
                "only one radial d orbital",
                "only two radial p orbitals",
                "no virtual s beyond physical 2s",
                "electrostatic nonrelativistic term centers only",
                "spin-orbit omitted in this layer",
                "only the requested low-energy eigenpairs are classified",
                "no experimental values enter the Hamiltonian",
                "TIR and affective mappings are not applied",
            ],
            "tir_status": "NOT_APPLIED_CONTROL_BASELINE",
            "affective_status": "RESERVED_UNASSIGNED",
        }


def _extend_balanced_orbitals_with_d(
    *,
    basis_size: int,
    grid_points: int,
    tolerance_hartree: float,
):
    reference, spatial, h_s, h_p = _build_orbitals(
        basis_size=basis_size,
        grid_points=grid_points,
        tolerance_hartree=tolerance_hartree,
    )
    r = reference.r
    weights = reference.weights
    core = reference.core_radials
    u2s = core[:, 1]
    core_density = 2.0 * np.sum(core * core, axis=1)
    direct = _direct_potential(core_density, r)
    zetas = np.geomspace(0.02, 24.0, basis_size)

    s2, _, _, h2 = _analytic_radial_matrices(2, 6, zetas)
    basis2 = _eval_slater_basis(2, zetas, r)
    fock_d = h2 + _local_matrix(basis2, direct, weights)
    for column in range(2):
        fock_d -= (1.0 / 5.0) * _exchange_matrix(
            basis2, core[:, column], r, weights, 2
        )
    eps_d_full, coeff_d = eigh(
        fock_d,
        s2,
        subset_by_index=[0, 0],
        check_finite=False,
    )
    d_radial = basis2 @ coeff_d[:, 0]

    # Remove the active physical 2s^2 mean field from the d one-body energy.
    v_2s = _direct_potential(u2s * u2s, r)
    j_ds = float(np.sum(weights * d_radial * d_radial * v_2s))
    product = d_radial * u2s
    transformed = _radial_kernel_apply(product[:, None], r, 2)[:, 0]
    k_ds = (1.0 / 5.0) * float(np.sum(weights * product * transformed))
    h_d = float(eps_d_full[0]) - (2.0 * j_ds - k_ds)

    extended = list(spatial)
    for m in (-2, -1, 0, 1, 2):
        extended.append(("d0", 2, m, d_radial))
    return reference, tuple(extended), float(h_s), np.array(h_p, dtype=float), h_d


def _spin_orbitals(spatial):
    return tuple(
        (spatial_index, group, l, m, spin2)
        for spatial_index, (group, l, m, _) in enumerate(spatial)
        for spin2 in (-1, 1)
    )


def _one_body_spin_matrix(spatial, spin_orbitals, h_s: float, h_p: np.ndarray, h_d: float):
    matrix = np.zeros((len(spin_orbitals), len(spin_orbitals)), dtype=float)
    for i, (si, gi, li, mi, spi) in enumerate(spin_orbitals):
        for j, (sj, gj, lj, mj, spj) in enumerate(spin_orbitals):
            if spi != spj or li != lj or mi != mj:
                continue
            if li == 0:
                if si == sj:
                    matrix[i, j] = h_s
            elif li == 1:
                ri = int(gi[1:])
                rj = int(gj[1:])
                matrix[i, j] = h_p[ri, rj]
            elif li == 2 and gi == gj:
                matrix[i, j] = h_d
    return matrix


def _radial_integrals(spatial, r, weights):
    cache = {}
    for a, (_, l1, _, ua) in enumerate(spatial):
        for c, (_, l3, _, uc) in enumerate(spatial):
            pair_ac = ua * uc
            for k in range(0, 5):
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


def _sparse_one_body(one_body: np.ndarray, determinants: tuple[int, ...]) -> csr_matrix:
    lookup = {state: index for index, state in enumerate(determinants)}
    by_q = {}
    for p, q in np.argwhere(np.abs(one_body) > 1.0e-14):
        by_q.setdefault(int(q), []).append((int(p), float(one_body[p, q])))

    rows = []
    cols = []
    data = []
    for column, state in enumerate(determinants):
        occupied = [i for i in range(one_body.shape[0]) if (state >> i) & 1]
        for q in occupied:
            for p, value in by_q.get(q, ()): 
                applied = _apply_one_body(state, p, q)
                if applied is None:
                    continue
                target, sign = applied
                row = lookup.get(target)
                if row is not None:
                    rows.append(row)
                    cols.append(column)
                    data.append(value * sign)
    matrix = coo_matrix((data, (rows, cols)), shape=(len(determinants), len(determinants)))
    matrix.sum_duplicates()
    return matrix.tocsr()


def _two_body_by_annihilation_pair(spatial, spin_orbitals, r, weights):
    radial = _radial_integrals(spatial, r, weights)
    by_rs = {}
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
                        radial_value = radial.get((a, b, c, d, k))
                        if radial_value is None:
                            continue
                        value += radial_value * _mixed_angular_coulomb_coefficient(
                            l1, m1, l2, m2, l3, m3, l4, m4, k
                        )
                    if abs(value) > 1.0e-13:
                        by_rs.setdefault((rr, s), []).append((p, q, 0.5 * value))
    return by_rs


def _sparse_two_body(spatial, spin_orbitals, determinants, r, weights) -> csr_matrix:
    lookup = {state: index for index, state in enumerate(determinants)}
    by_rs = _two_body_by_annihilation_pair(spatial, spin_orbitals, r, weights)
    rows = []
    cols = []
    data = []
    n_orbitals = len(spin_orbitals)
    for column, state in enumerate(determinants):
        occupied = [i for i in range(n_orbitals) if (state >> i) & 1]
        for rr in occupied:
            for s in occupied:
                if rr == s:
                    continue
                for p, q, value in by_rs.get((rr, s), ()): 
                    applied = _apply_two_body(state, p, q, rr, s)
                    if applied is None:
                        continue
                    target, sign = applied
                    row = lookup.get(target)
                    if row is not None:
                        rows.append(row)
                        cols.append(column)
                        data.append(value * sign)
    matrix = coo_matrix((data, (rows, cols)), shape=(len(determinants), len(determinants)))
    matrix.sum_duplicates()
    return matrix.tocsr()


def _angular_one_body_operators(spin_orbitals):
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
            lp[lookup[(group, l, m + 1, spin2)], index] = math.sqrt(l * (l + 1) - m * (m + 1))
        if m > -l:
            lm[lookup[(group, l, m - 1, spin2)], index] = math.sqrt(l * (l + 1) - m * (m - 1))
        if spin2 == -1:
            sp[lookup[(group, l, m, 1)], index] = 1.0
        else:
            sm[lookup[(group, l, m, -1)], index] = 1.0
    return lz, lp, lm, sz, sp, sm


def _casimir_from_sparse_ops(vector, z_op, plus_op, minus_op) -> float:
    zv = z_op @ vector
    pv = plus_op @ vector
    mv = minus_op @ vector
    return float(np.vdot(zv, zv).real + 0.5 * (np.vdot(pv, pv).real + np.vdot(mv, mv).real))


def _quantum_number(casimir: float) -> float:
    return 0.5 * (-1.0 + math.sqrt(max(0.0, 1.0 + 4.0 * casimir)))


def solve_carbon_sparse_multichannel_ci(
    *,
    basis_size: int = 18,
    grid_points: int = 800,
    tolerance_hartree: float = 1.0e-9,
    eigenpairs: int = 32,
) -> CarbonSparseMultichannelCIResult:
    """Sparse low-spectrum CI for the balanced carbon 2s + p(radial) + d space."""
    reference, spatial, h_s, h_p, h_d = _extend_balanced_orbitals_with_d(
        basis_size=basis_size,
        grid_points=grid_points,
        tolerance_hartree=tolerance_hartree,
    )
    spin_orbitals = _spin_orbitals(spatial)
    p_flags = tuple(l == 1 for _, _, l, _, _ in spin_orbitals)
    determinants = _selected_determinants(len(spin_orbitals), 4, p_flags)
    one_body = _one_body_spin_matrix(spatial, spin_orbitals, h_s, h_p, h_d)
    hamiltonian = _sparse_one_body(one_body, determinants) + _sparse_two_body(
        spatial,
        spin_orbitals,
        determinants,
        reference.r,
        reference.weights,
    )
    hamiltonian = 0.5 * (hamiltonian + hamiltonian.T)

    k = min(eigenpairs, len(determinants) - 2)
    energies, vectors = eigsh(
        hamiltonian,
        k=k,
        which="SA",
        tol=1.0e-9,
        maxiter=10000,
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

    return CarbonSparseMultichannelCIResult(
        spin_orbitals=len(spin_orbitals),
        even_determinants=len(determinants),
        requested_eigenpairs=k,
        one_body_s_hartree=float(h_s),
        one_body_p_eigenvalues_hartree=tuple(float(v) for v in np.linalg.eigvalsh(h_p)),
        one_body_d_hartree=float(h_d),
        hamiltonian_nnz=int(hamiltonian.nnz),
        terms=tuple(terms),
    )
