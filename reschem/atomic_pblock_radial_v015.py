"""Neutral p-block radial state extractor for Resonant Chemistry v0.15 Stage-F.

This module lifts the existing B-Ne `_solve_period2_radial_state` implementation
onto an explicit active p shell while preserving the same one-body basis,
direct and exchange construction, SCF update, mixing, convergence criterion,
density normalization, and virial bookkeeping. No spectral observations are
accepted by this module.
"""
from __future__ import annotations

import math
import re

import numpy as np
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
from .atomic_radial_spectroscopy import ALPHA_FINE_STRUCTURE, _pauli_central_zeta

SCHEMA = "RESCHEM_NEUTRAL_PBLOCK_RADIAL_STATE_V0_15"
EXPOSURE_SCHEMA = "RESCHEM_NEUTRAL_PBLOCK_RADIAL_EXPOSURE_CONTROL_V0_15"
_ACTIVE_P_SHELL = re.compile(r"^(\d+)p$")


class AtomicPBlockRadialV015Error(ValueError):
    pass


def _active_n(active_p_shell: str) -> int:
    match = _ACTIVE_P_SHELL.fullmatch(str(active_p_shell).strip())
    if match is None:
        raise AtomicPBlockRadialV015Error("active_p_shell must have the form '<n>p'")
    n = int(match.group(1))
    if n < 2:
        raise AtomicPBlockRadialV015Error("active p shell must have n >= 2")
    return n


def solve_neutral_pblock_radial_state(
    z: int,
    active_p_shell: str,
    *,
    basis_size: int = 24,
    grid_points: int = 1500,
    mixing: float = 0.32,
    tolerance_hartree: float = 5.0e-8,
    max_iterations: int = 120,
) -> dict[str, object]:
    """Return the Stage-B-equivalent radial state for one explicit neutral p shell."""
    zz = int(z)
    if zz <= 0:
        raise AtomicPBlockRadialV015Error("Z must be positive")
    n_active = _active_n(active_p_shell)
    if basis_size < 12:
        raise AtomicPBlockRadialV015Error("basis_size must be >= 12")
    if grid_points < 500:
        raise AtomicPBlockRadialV015Error("grid_points must be >= 500")
    if not (0.0 < float(mixing) <= 1.0):
        raise AtomicPBlockRadialV015Error("mixing must be in (0,1]")
    if float(tolerance_hartree) <= 0.0:
        raise AtomicPBlockRadialV015Error("tolerance_hartree must be positive")
    if int(max_iterations) < 1:
        raise AtomicPBlockRadialV015Error("max_iterations must be positive")

    subshells = subshells_for_atom(zz, 0)
    occupied_p_shells = [shell for shell in subshells if shell.l == 1 and shell.occupancy > 0]
    p_shell = max(occupied_p_shells, key=lambda shell: shell.n, default=None)
    if p_shell is None or p_shell.label != active_p_shell:
        raise AtomicPBlockRadialV015Error(
            f"active p shell {active_p_shell!r} is not the outermost occupied p shell for neutral Z={zz}"
        )

    active_l = sorted({shell.l for shell in subshells})
    zetas = np.geomspace(0.02, max(20.0, 4.0 * zz), int(basis_size))
    r = np.geomspace(1.0e-8, 120.0, int(grid_points))
    weights = _trap_weights(r)

    overlap: dict[int, np.ndarray] = {}
    kinetic: dict[int, np.ndarray] = {}
    nuclear: dict[int, np.ndarray] = {}
    one_body: dict[int, np.ndarray] = {}
    basis: dict[int, np.ndarray] = {}
    for ell in active_l:
        overlap[ell], kinetic[ell], nuclear[ell], one_body[ell] = _analytic_radial_matrices(ell, zz, zetas)
        basis[ell] = _eval_slater_basis(ell, zetas, r)

    occupation: dict[tuple[int, int, str], int] = {}
    orbitals: dict[tuple[int, int, str], np.ndarray] = {}
    for ell in active_l:
        highest_index = max(shell.n - ell - 1 for shell in subshells if shell.l == ell)
        _, vectors = eigh(one_body[ell], overlap[ell], subset_by_index=[0, highest_index], check_finite=False)
        for shell in subshells:
            if shell.l != ell:
                continue
            index = shell.n - ell - 1
            if shell.alpha_occupancy:
                key = (shell.n, ell, "alpha")
                occupation[key] = shell.alpha_occupancy
                orbitals[key] = vectors[:, index].copy()
            if shell.beta_occupancy:
                key = (shell.n, ell, "beta")
                occupation[key] = shell.beta_occupancy
                orbitals[key] = vectors[:, index].copy()

    def radial_orbital(key: tuple[int, int, str]) -> np.ndarray:
        return basis[key[1]] @ orbitals[key]

    def energy_components() -> tuple[float, float, float, float, float, np.ndarray]:
        density = np.zeros_like(r)
        cache: dict[tuple[int, int, str], np.ndarray] = {}
        kinetic_energy = 0.0
        nuclear_energy = 0.0
        for key, count in occupation.items():
            u = radial_orbital(key)
            cache[key] = u
            density += count * u * u
            ell = key[1]
            c = orbitals[key]
            kinetic_energy += count * float(c @ kinetic[ell] @ c)
            nuclear_energy += count * float(c @ nuclear[ell] @ c)

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
                    exchange_energy -= 0.5 * count_a * count_b * angular * float(np.sum(weights * product * transformed))
        total = kinetic_energy + nuclear_energy + direct_energy + exchange_energy
        return total, kinetic_energy, nuclear_energy, direct_energy, exchange_energy, density

    previous_energy: float | None = None
    converged = False
    iteration = 0
    for iteration in range(1, int(max_iterations) + 1):
        density = np.zeros_like(r)
        orbital_cache: dict[tuple[int, int, str], np.ndarray] = {}
        for key, count in occupation.items():
            u = radial_orbital(key)
            orbital_cache[key] = u
            density += count * u * u
        direct_potential = _direct_potential(density, r)
        updated: dict[tuple[int, int, str], np.ndarray] = {}

        for ell in active_l:
            direct_matrix = _local_matrix(basis[ell], direct_potential, weights)
            for spin in ("alpha", "beta"):
                targets = sorted(key for key in occupation if key[1] == ell and key[2] == spin)
                if not targets:
                    continue
                exchange = np.zeros_like(one_body[ell])
                for source_key, source_count in occupation.items():
                    _, source_l, source_spin = source_key
                    if source_spin != spin:
                        continue
                    source = orbital_cache[source_key]
                    for multipole_k, angular in _W3J_SQ[(ell, source_l)].items():
                        exchange += source_count * angular * _exchange_matrix(basis[ell], source, r, weights, multipole_k)
                fock = one_body[ell] + direct_matrix - exchange
                highest_index = max(key[0] - ell - 1 for key in targets)
                _, vectors = eigh(fock, overlap[ell], subset_by_index=[0, highest_index], check_finite=False)
                candidate = np.column_stack([vectors[:, key[0] - ell - 1] for key in targets])
                current = np.column_stack([orbitals[key] for key in targets])
                for column in range(candidate.shape[1]):
                    if float(current[:, column] @ overlap[ell] @ candidate[:, column]) < 0.0:
                        candidate[:, column] *= -1.0
                mixed = _orthonormalize_columns((1.0 - float(mixing)) * current + float(mixing) * candidate, overlap[ell])
                for column, key in enumerate(targets):
                    updated[key] = mixed[:, column]

        orbitals.update(updated)
        total, _, _, _, _, _ = energy_components()
        if previous_energy is not None and abs(total - previous_energy) < float(tolerance_hartree):
            converged = True
            break
        previous_energy = total

    if not converged:
        raise RuntimeError(f"neutral p-block radial SCF did not converge for Z={zz}, shell={active_p_shell}")

    total, kinetic_energy, nuclear_energy, direct_energy, exchange_energy, density = energy_components()
    p_density = np.zeros_like(r)
    for spin, count in (("alpha", p_shell.alpha_occupancy), ("beta", p_shell.beta_occupancy)):
        if not count:
            continue
        key = (n_active, 1, spin)
        u = radial_orbital(key)
        p_density += count * u * u
    one_p_density = p_density / float(p_shell.occupancy)
    one_p_normalization = float(np.sum(weights * one_p_density))
    if not math.isfinite(one_p_normalization) or one_p_normalization <= 0.0:
        raise RuntimeError("active one-p radial density normalization failed")
    one_p_density /= one_p_normalization

    # Preserve exact 2p legacy replay while making the lifted n>2 state
    # decomposition-consistent on the numerical quadrature used by observables.
    if n_active > 2:
        other_density = density - p_density
        if float(np.min(other_density)) < -1.0e-12:
            raise RuntimeError("non-active radial density became negative beyond roundoff tolerance")
        density = np.maximum(other_density, 0.0) + float(p_shell.occupancy) * one_p_density

    return {
        "schema": SCHEMA,
        "Z": zz,
        "active_p_shell": active_p_shell,
        "r": r,
        "weights": weights,
        "density": density,
        "one_p_density": one_p_density,
        "p_electron_count": int(p_shell.occupancy),
        "energy_hartree": float(total),
        "virial_residual_hartree": float(2.0 * kinetic_energy + nuclear_energy + direct_energy + exchange_energy),
        "iterations": int(iteration),
        "converged": True,
        "basis_size": int(basis_size),
        "grid_points": int(grid_points),
        "mixing": float(mixing),
        "tolerance_hartree": float(tolerance_hartree),
        "max_iterations": int(max_iterations),
        "spectral_input": "NONE",
        "fit_parameters": [],
        "calibration_parameters": [],
        "epistemic_operator": "CHYBA",
        "canon_allowed": False,
    }


def pblock_radial_control_exposure(z: int, active_p_shell: str, **solver_kwargs: object) -> dict[str, object]:
    state = solve_neutral_pblock_radial_state(z, active_p_shell, **solver_kwargs)
    zeta = _pauli_central_zeta(int(z), state["density"], state["one_p_density"], state["r"], state["weights"])
    exposure = 2.0 * float(zeta) / (ALPHA_FINE_STRUCTURE**2)
    return {
        "schema": EXPOSURE_SCHEMA,
        "Z": int(z),
        "active_p_shell": active_p_shell,
        "radial_nuclear_exposure": exposure,
        "zeta_p_hartree": float(zeta),
        "hf_energy_hartree": float(state["energy_hartree"]),
        "virial_residual_hartree": float(state["virial_residual_hartree"]),
        "scf_iterations": int(state["iterations"]),
        "control_source": "reschem.atomic_pblock_radial_v015",
        "status": "CONTROL_RADIAL_EXPOSURE_AVAILABLE",
        "spectral_input": "NONE",
        "fit_parameters": [],
        "calibration_parameters": [],
        "epistemic_operator": "CHYBA",
        "canon_allowed": False,
    }
