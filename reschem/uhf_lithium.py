from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.linalg import eigh

LI_HF_REFERENCE_HARTREE = -7.432727
LI_EXACT_NONREL_REFERENCE_HARTREE = -7.4780603239041


def _weighted_orthonormalize(vectors: np.ndarray, h: float) -> np.ndarray:
    q, _ = np.linalg.qr(vectors * math.sqrt(h))
    return q / math.sqrt(h)


def _coulomb_kernel(r: np.ndarray, h: float) -> np.ndarray:
    return h / np.maximum(r[:, None], r[None, :])


def _build_fock(
    h_core: np.ndarray,
    kernel: np.ndarray,
    all_occupied: list[np.ndarray],
    same_spin_occupied: list[np.ndarray],
) -> np.ndarray:
    fock = h_core.copy()
    for orbital in all_occupied:
        potential = kernel @ (orbital * orbital)
        fock += np.diag(potential)
    for orbital in same_spin_occupied:
        fock -= (orbital[:, None] * kernel) * orbital[None, :]
    return 0.5 * (fock + fock.T)


def _coulomb_integral(u: np.ndarray, v: np.ndarray, kernel: np.ndarray, h: float) -> float:
    potential_v = kernel @ (v * v)
    return float(np.sum((u * u) * potential_v) * h)


def _exchange_integral(u: np.ndarray, v: np.ndarray, kernel: np.ndarray, h: float) -> float:
    exchange_v = ((v[:, None] * kernel) * v[None, :]) @ u
    return float(np.sum(u * exchange_v) * h)


def _energy_components(
    kinetic: np.ndarray,
    nuclear: np.ndarray,
    kernel: np.ndarray,
    alpha: np.ndarray,
    beta: np.ndarray,
    h: float,
) -> tuple[float, float, float, float]:
    kinetic_energy = 0.0
    nuclear_energy = 0.0
    for block in (alpha, beta):
        for column in range(block.shape[1]):
            u = block[:, column]
            kinetic_energy += float(u @ (kinetic @ u) * h)
            nuclear_energy += float(u @ (nuclear @ u) * h)

    occupied = [(alpha[:, j], 0) for j in range(alpha.shape[1])]
    occupied += [(beta[:, j], 1) for j in range(beta.shape[1])]
    electron_electron = 0.0
    for u, spin_u in occupied:
        for v, spin_v in occupied:
            electron_electron += 0.5 * _coulomb_integral(u, v, kernel, h)
            if spin_u == spin_v:
                electron_electron -= 0.5 * _exchange_integral(u, v, kernel, h)
    total = kinetic_energy + nuclear_energy + electron_electron
    return total, kinetic_energy, nuclear_energy, electron_electron


def _s2_expectation(alpha: np.ndarray, beta: np.ndarray, h: float) -> float:
    n_alpha = alpha.shape[1]
    n_beta = beta.shape[1]
    s_z = 0.5 * (n_alpha - n_beta)
    overlap = alpha.T @ beta * h
    return float(s_z * (s_z + 1.0) + n_beta - np.sum(overlap * overlap))


@dataclass(frozen=True)
class LithiumUHFResult:
    points: int
    rmax_bohr: float
    iterations: int
    converged: bool
    energy_hartree: float
    kinetic_hartree: float
    nuclear_attraction_hartree: float
    electron_electron_hartree: float
    virial_residual_hartree: float
    s2_expectation: float
    alpha_orbital_energies_hartree: tuple[float, float]
    beta_orbital_energy_hartree: float

    @property
    def spin_contamination(self) -> float:
        return self.s2_expectation - 0.75

    @property
    def relative_error_vs_hf_reference(self) -> float:
        return abs(self.energy_hartree - LI_HF_REFERENCE_HARTREE) / abs(LI_HF_REFERENCE_HARTREE)

    def as_dict(self) -> dict:
        return {
            "schema": "RESCHEM_LITHIUM_RADIAL_UHF_V0_1",
            "configuration": "1s^2 2s^1",
            "spin_occupancy": {"alpha": 2, "beta": 1},
            "points": self.points,
            "rmax_bohr": self.rmax_bohr,
            "iterations": self.iterations,
            "converged": self.converged,
            "energy_hartree": self.energy_hartree,
            "kinetic_hartree": self.kinetic_hartree,
            "nuclear_attraction_hartree": self.nuclear_attraction_hartree,
            "electron_electron_hartree": self.electron_electron_hartree,
            "virial_residual_hartree": self.virial_residual_hartree,
            "s2_expectation": self.s2_expectation,
            "spin_contamination": self.spin_contamination,
            "alpha_orbital_energies_hartree": list(self.alpha_orbital_energies_hartree),
            "beta_orbital_energy_hartree": self.beta_orbital_energy_hartree,
            "method": "spherical radial unrestricted Hartree-Fock, s orbitals only",
            "tir_status": "NOT_APPLIED_CONTROL_BASELINE",
            "epistemic_status": "OPEN_SHELL_CONTROL_APPROXIMATION",
        }


def solve_lithium_radial_uhf(
    *,
    points: int = 400,
    rmax_bohr: float = 30.0,
    mixing: float = 0.40,
    tolerance_hartree: float = 2e-9,
    max_iterations: int = 100,
) -> LithiumUHFResult:
    if points < 80:
        raise ValueError("points must be >= 80")
    if rmax_bohr <= 0.0:
        raise ValueError("rmax_bohr must be positive")
    if not (0.0 < mixing <= 1.0):
        raise ValueError("mixing must be in (0,1]")

    z = 3.0
    h = rmax_bohr / (points + 1)
    r = h * np.arange(1, points + 1, dtype=float)
    off = np.full(points - 1, -0.5 / h**2)
    kinetic = np.diag(np.full(points, 1.0 / h**2)) + np.diag(off, 1) + np.diag(off, -1)
    nuclear = np.diag(-z / r)
    h_core = kinetic + nuclear
    kernel = _coulomb_kernel(r, h)

    _, initial_vectors = eigh(h_core, subset_by_index=[0, 1], check_finite=False)
    alpha = _weighted_orthonormalize(initial_vectors[:, :2], h)
    beta = _weighted_orthonormalize(initial_vectors[:, :1], h)

    previous_energy = None
    converged = False
    alpha_energies = np.array([float("nan"), float("nan")])
    beta_energies = np.array([float("nan")])

    for iteration in range(1, max_iterations + 1):
        all_occupied = [alpha[:, j] for j in range(2)] + [beta[:, 0]]
        f_alpha = _build_fock(h_core, kernel, all_occupied, [alpha[:, j] for j in range(2)])
        f_beta = _build_fock(h_core, kernel, all_occupied, [beta[:, 0]])

        alpha_energies, candidate_alpha = eigh(
            f_alpha,
            subset_by_index=[0, 1],
            check_finite=False,
        )
        beta_energies, candidate_beta = eigh(
            f_beta,
            subset_by_index=[0, 0],
            check_finite=False,
        )
        candidate_alpha = _weighted_orthonormalize(candidate_alpha, h)
        candidate_beta = _weighted_orthonormalize(candidate_beta, h)

        for column in range(2):
            if float(np.dot(candidate_alpha[:, column], alpha[:, column]) * h) < 0.0:
                candidate_alpha[:, column] *= -1.0
        if float(np.dot(candidate_beta[:, 0], beta[:, 0]) * h) < 0.0:
            candidate_beta[:, 0] *= -1.0

        alpha_new = _weighted_orthonormalize(
            (1.0 - mixing) * alpha + mixing * candidate_alpha,
            h,
        )
        beta_new = _weighted_orthonormalize(
            (1.0 - mixing) * beta + mixing * candidate_beta,
            h,
        )

        total, kinetic_energy, nuclear_energy, electron_electron = _energy_components(
            kinetic,
            nuclear,
            kernel,
            alpha_new,
            beta_new,
            h,
        )
        if previous_energy is not None and abs(total - previous_energy) < tolerance_hartree:
            alpha = alpha_new
            beta = beta_new
            converged = True
            break
        alpha = alpha_new
        beta = beta_new
        previous_energy = total

    total, kinetic_energy, nuclear_energy, electron_electron = _energy_components(
        kinetic,
        nuclear,
        kernel,
        alpha,
        beta,
        h,
    )
    s2 = _s2_expectation(alpha, beta, h)
    return LithiumUHFResult(
        points=points,
        rmax_bohr=rmax_bohr,
        iterations=iteration,
        converged=converged,
        energy_hartree=total,
        kinetic_hartree=kinetic_energy,
        nuclear_attraction_hartree=nuclear_energy,
        electron_electron_hartree=electron_electron,
        virial_residual_hartree=2.0 * kinetic_energy + nuclear_energy + electron_electron,
        s2_expectation=s2,
        alpha_orbital_energies_hartree=(float(alpha_energies[0]), float(alpha_energies[1])),
        beta_orbital_energy_hartree=float(beta_energies[0]),
    )


@dataclass(frozen=True)
class RichardsonLithiumUHFResult:
    coarse: LithiumUHFResult
    fine: LithiumUHFResult
    extrapolated_energy_hartree: float

    @property
    def relative_error_vs_hf_reference(self) -> float:
        return abs(self.extrapolated_energy_hartree - LI_HF_REFERENCE_HARTREE) / abs(LI_HF_REFERENCE_HARTREE)


def solve_lithium_radial_uhf_richardson(
    *,
    coarse_points: int = 400,
    rmax_bohr: float = 30.0,
    **kwargs,
) -> RichardsonLithiumUHFResult:
    fine_points = 2 * coarse_points + 1
    coarse = solve_lithium_radial_uhf(points=coarse_points, rmax_bohr=rmax_bohr, **kwargs)
    fine = solve_lithium_radial_uhf(points=fine_points, rmax_bohr=rmax_bohr, **kwargs)
    extrapolated = (4.0 * fine.energy_hartree - coarse.energy_hartree) / 3.0
    return RichardsonLithiumUHFResult(coarse=coarse, fine=fine, extrapolated_energy_hartree=extrapolated)
