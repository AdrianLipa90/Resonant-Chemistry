from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.integrate import cumulative_trapezoid
from scipy.linalg import eigh

from .atomic_hf_average import (
    _W3J_SQ,
    _analytic_radial_matrices,
    _direct_potential,
    _eval_slater_basis,
    _exchange_matrix,
    _local_matrix,
    _orthonormalize_columns,
    _radial_kernel_apply,
    _trap_weights,
    subshells_for_atom,
)
from .multiplet_angular import (
    _ls_squared_matrices,
    _one_body_many_body_matrix,
    _two_body_shell_hamiltonian,
    solve_equivalent_shell_multiplets,
)
from .multiplet_spin_orbit import _j_squared_many_body, _spin_orbit_one_body

ALPHA_FINE_STRUCTURE = 7.2973525693e-3
HARTREE_TO_WAVENUMBER_CM = 219474.6313705
_TERM_LETTERS = "SPDFGHIKLMNOQRTUVWXYZ"


@dataclass(frozen=True)
class FineStructureLevel:
    relative_energy_hartree: float
    relative_energy_cm1: float
    J: float
    degeneracy: int
    approximate_L: int
    approximate_S: float

    @property
    def approximate_term(self) -> str:
        multiplicity = int(round(2.0 * self.approximate_S + 1.0))
        return f"^{multiplicity}{_TERM_LETTERS[self.approximate_L]}"

    def as_dict(self) -> dict:
        return {
            "relative_energy_hartree": self.relative_energy_hartree,
            "relative_energy_cm^-1": self.relative_energy_cm1,
            "J": self.J,
            "degeneracy": self.degeneracy,
            "approximate_LS_term": self.approximate_term,
        }


@dataclass(frozen=True)
class Period2SpectroscopyResult:
    z: int
    p_electron_count: int
    hf_energy_hartree: float
    virial_residual_hartree: float
    slater_f0_hartree: float
    slater_f2_hartree: float
    zeta_2p_hartree: float
    zeta_2p_cm1: float
    ground_LS_term: str
    ground_J: float
    levels: tuple[FineStructureLevel, ...]
    scf_iterations: int

    def as_dict(self) -> dict:
        return {
            "schema": "RESCHEM_PERIOD2_ATOM_SPECIFIC_SPECTROSCOPY_V0_1",
            "Z": self.z,
            "p_electron_count": self.p_electron_count,
            "hf_energy_hartree": self.hf_energy_hartree,
            "virial_residual_hartree": self.virial_residual_hartree,
            "radial_slater_integrals_hartree": {
                "F0": self.slater_f0_hartree,
                "F2": self.slater_f2_hartree,
            },
            "spin_orbit": {
                "zeta_2p_hartree": self.zeta_2p_hartree,
                "zeta_2p_cm^-1": self.zeta_2p_cm1,
                "model": "Pauli central-field control using nucleus plus spherical direct field of the other electrons",
            },
            "ground_LS_term": self.ground_LS_term,
            "ground_J": self.ground_J,
            "levels": [level.as_dict() for level in self.levels],
            "scf_iterations": self.scf_iterations,
            "scope": "neutral B-Ne period-2 2p^n control spectroscopy; configuration-average radial HF plus equivalent-shell electrostatic and one-electron spin-orbit algebra",
            "limitations": [
                "nonrelativistic radial HF control state",
                "spin-orbit scale is Pauli central-field rather than Dirac-Hartree-Fock",
                "correlation and configuration interaction outside the active equivalent 2p shell are omitted",
                "TIR and affective mappings are not applied",
            ],
            "tir_status": "NOT_APPLIED_CONTROL_BASELINE",
            "affective_status": "RESERVED_UNASSIGNED",
        }


def _quantum_number_from_casimir(value: float) -> float:
    return 0.5 * (-1.0 + math.sqrt(max(0.0, 1.0 + 4.0 * value)))


def _solve_period2_radial_state(
    z: int,
    *,
    basis_size: int,
    grid_points: int,
    mixing: float,
    tolerance_hartree: float,
    max_iterations: int,
):
    if not (5 <= z <= 10):
        raise ValueError("period-2 spectroscopy v0.1 supports neutral B-Ne (Z=5..10)")

    subshells = subshells_for_atom(z, 0)
    active_l = sorted({shell.l for shell in subshells})
    zetas = np.geomspace(0.02, max(20.0, 4.0 * z), basis_size)
    r = np.geomspace(1.0e-8, 120.0, grid_points)
    weights = _trap_weights(r)

    overlap = {}
    kinetic = {}
    nuclear = {}
    one_body = {}
    basis = {}
    for l in active_l:
        overlap[l], kinetic[l], nuclear[l], one_body[l] = _analytic_radial_matrices(l, z, zetas)
        basis[l] = _eval_slater_basis(l, zetas, r)

    occupation = {}
    orbitals = {}
    for l in active_l:
        highest_index = max(shell.n - l - 1 for shell in subshells if shell.l == l)
        _, vectors = eigh(
            one_body[l],
            overlap[l],
            subset_by_index=[0, highest_index],
            check_finite=False,
        )
        for shell in subshells:
            if shell.l != l:
                continue
            index = shell.n - l - 1
            if shell.alpha_occupancy:
                key = (shell.n, l, "alpha")
                occupation[key] = shell.alpha_occupancy
                orbitals[key] = vectors[:, index].copy()
            if shell.beta_occupancy:
                key = (shell.n, l, "beta")
                occupation[key] = shell.beta_occupancy
                orbitals[key] = vectors[:, index].copy()

    def radial_orbital(key):
        return basis[key[1]] @ orbitals[key]

    def energy_components():
        density = np.zeros_like(r)
        cache = {}
        kinetic_energy = 0.0
        nuclear_energy = 0.0
        for key, count in occupation.items():
            u = radial_orbital(key)
            cache[key] = u
            density += count * u * u
            l = key[1]
            c = orbitals[key]
            kinetic_energy += count * float(c @ kinetic[l] @ c)
            nuclear_energy += count * float(c @ nuclear[l] @ c)

        direct_potential = _direct_potential(density, r)
        direct_energy = 0.5 * float(np.sum(weights * density * direct_potential))
        exchange_energy = 0.0
        for key_a, count_a in occupation.items():
            _, l_a, spin_a = key_a
            u_a = cache[key_a]
            for key_b, count_b in occupation.items():
                _, l_b, spin_b = key_b
                if spin_a != spin_b:
                    continue
                product = u_a * cache[key_b]
                for multipole_k, angular in _W3J_SQ[(l_a, l_b)].items():
                    transformed = _radial_kernel_apply(product[:, None], r, multipole_k)[:, 0]
                    exchange_energy -= 0.5 * count_a * count_b * angular * float(
                        np.sum(weights * product * transformed)
                    )
        total = kinetic_energy + nuclear_energy + direct_energy + exchange_energy
        return total, kinetic_energy, nuclear_energy, direct_energy, exchange_energy, density

    previous_energy = None
    converged = False
    for iteration in range(1, max_iterations + 1):
        density = np.zeros_like(r)
        orbital_cache = {}
        for key, count in occupation.items():
            u = radial_orbital(key)
            orbital_cache[key] = u
            density += count * u * u
        direct_potential = _direct_potential(density, r)
        updated = {}

        for l in active_l:
            direct_matrix = _local_matrix(basis[l], direct_potential, weights)
            for spin in ("alpha", "beta"):
                targets = sorted(key for key in occupation if key[1] == l and key[2] == spin)
                if not targets:
                    continue
                exchange = np.zeros_like(one_body[l])
                for source_key, source_count in occupation.items():
                    _, source_l, source_spin = source_key
                    if source_spin != spin:
                        continue
                    source = orbital_cache[source_key]
                    for multipole_k, angular in _W3J_SQ[(l, source_l)].items():
                        exchange += source_count * angular * _exchange_matrix(
                            basis[l], source, r, weights, multipole_k
                        )
                fock = one_body[l] + direct_matrix - exchange
                highest_index = max(key[0] - l - 1 for key in targets)
                _, vectors = eigh(
                    fock,
                    overlap[l],
                    subset_by_index=[0, highest_index],
                    check_finite=False,
                )
                candidate = np.column_stack([vectors[:, key[0] - l - 1] for key in targets])
                current = np.column_stack([orbitals[key] for key in targets])
                for column in range(candidate.shape[1]):
                    if float(current[:, column] @ overlap[l] @ candidate[:, column]) < 0.0:
                        candidate[:, column] *= -1.0
                mixed = _orthonormalize_columns(
                    (1.0 - mixing) * current + mixing * candidate,
                    overlap[l],
                )
                for column, key in enumerate(targets):
                    updated[key] = mixed[:, column]

        orbitals.update(updated)
        total, _, _, _, _, _ = energy_components()
        if previous_energy is not None and abs(total - previous_energy) < tolerance_hartree:
            converged = True
            break
        previous_energy = total

    if not converged:
        raise RuntimeError(f"period-2 radial SCF did not converge for Z={z}")

    total, kinetic_energy, nuclear_energy, direct_energy, exchange_energy, density = energy_components()
    p_shell = next(shell for shell in subshells if shell.label == "2p")
    p_density = np.zeros_like(r)
    for spin, count in (("alpha", p_shell.alpha_occupancy), ("beta", p_shell.beta_occupancy)):
        if not count:
            continue
        key = (2, 1, spin)
        u = radial_orbital(key)
        p_density += count * u * u
    one_p_density = p_density / float(p_shell.occupancy)
    one_p_density /= float(np.sum(weights * one_p_density))

    return {
        "r": r,
        "weights": weights,
        "density": density,
        "one_p_density": one_p_density,
        "p_electron_count": p_shell.occupancy,
        "energy_hartree": total,
        "virial_residual_hartree": 2.0 * kinetic_energy + nuclear_energy + direct_energy + exchange_energy,
        "iterations": iteration,
    }


def _slater_integral(one_electron_radial_density: np.ndarray, r: np.ndarray, weights: np.ndarray, k: int) -> float:
    transformed = _radial_kernel_apply(one_electron_radial_density[:, None], r, k)[:, 0]
    return float(np.sum(weights * one_electron_radial_density * transformed))


def _pauli_central_zeta(
    z: int,
    total_radial_density: np.ndarray,
    one_active_electron_density: np.ndarray,
    r: np.ndarray,
    weights: np.ndarray,
) -> float:
    other_electron_density = total_radial_density - one_active_electron_density
    enclosed_other_charge = cumulative_trapezoid(other_electron_density, r, initial=0.0)
    one_over_r_dv_dr = (float(z) - enclosed_other_charge) / (r ** 3)
    return 0.5 * ALPHA_FINE_STRUCTURE**2 * float(
        np.sum(weights * one_active_electron_density * one_over_r_dv_dr)
    )


def _fine_structure_levels(
    p_electron_count: int,
    f0_hartree: float,
    f2_hartree: float,
    zeta_hartree: float,
    *,
    degeneracy_tolerance_hartree: float = 1.0e-9,
) -> tuple[FineStructureLevel, ...]:
    slater = {0: f0_hartree, 2: f2_hartree}
    coulomb = _two_body_shell_hamiltonian(1, p_electron_count, slater)
    spin_orbit = _one_body_many_body_matrix(_spin_orbit_one_body(1), p_electron_count)
    j2 = _j_squared_many_body(1, p_electron_count)
    l2, s2 = _ls_squared_matrices(1, p_electron_count)

    hamiltonian = coulomb + zeta_hartree * spin_orbit
    energies, eigenvectors = np.linalg.eigh(hamiltonian)
    ground = float(energies[0])

    levels = []
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
            FineStructureLevel(
                relative_energy_hartree=relative,
                relative_energy_cm1=relative * HARTREE_TO_WAVENUMBER_CM,
                J=J,
                degeneracy=stop - start,
                approximate_L=L,
                approximate_S=S,
            )
        )
        start = stop
    return tuple(levels)


def solve_period2_atom_specific_spectroscopy(
    z: int,
    *,
    basis_size: int = 24,
    grid_points: int = 1500,
    mixing: float = 0.32,
    tolerance_hartree: float = 5.0e-8,
    max_iterations: int = 120,
) -> Period2SpectroscopyResult:
    state = _solve_period2_radial_state(
        z,
        basis_size=basis_size,
        grid_points=grid_points,
        mixing=mixing,
        tolerance_hartree=tolerance_hartree,
        max_iterations=max_iterations,
    )
    r = state["r"]
    weights = state["weights"]
    one_p = state["one_p_density"]
    f0 = _slater_integral(one_p, r, weights, 0)
    f2 = _slater_integral(one_p, r, weights, 2)
    zeta = _pauli_central_zeta(z, state["density"], one_p, r, weights)
    p_count = int(state["p_electron_count"])

    ls_result = solve_equivalent_shell_multiplets(
        1,
        p_count,
        slater_parameters={0: f0, 2: f2},
    )
    levels = _fine_structure_levels(p_count, f0, f2, zeta)
    return Period2SpectroscopyResult(
        z=z,
        p_electron_count=p_count,
        hf_energy_hartree=float(state["energy_hartree"]),
        virial_residual_hartree=float(state["virial_residual_hartree"]),
        slater_f0_hartree=f0,
        slater_f2_hartree=f2,
        zeta_2p_hartree=zeta,
        zeta_2p_cm1=zeta * HARTREE_TO_WAVENUMBER_CM,
        ground_LS_term=ls_result.ground_term.symbol,
        ground_J=levels[0].J,
        levels=levels,
        scf_iterations=int(state["iterations"]),
    )


def solve_b_to_f_spectroscopy(**kwargs) -> tuple[Period2SpectroscopyResult, ...]:
    return tuple(solve_period2_atom_specific_spectroscopy(z, **kwargs) for z in range(5, 10))
