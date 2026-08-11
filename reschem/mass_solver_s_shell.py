from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np
from scipy.linalg import eigh


@dataclass(frozen=True)
class SShellSpecies:
    label: str
    nuclear_charge: int
    electron_count: int

    @property
    def spin_occupancy(self) -> tuple[int, int]:
        if not (1 <= self.electron_count <= 4):
            raise ValueError("v0.1 s-shell mass solver supports 1..4 electrons")
        return ((self.electron_count + 1) // 2, self.electron_count // 2)

    @property
    def default_rmax_bohr(self) -> float:
        # Physics-motivated compactness scaling; no reference energies enter.
        return 30.0 * self.electron_count / self.nuclear_charge


@dataclass(frozen=True)
class SShellUHFResult:
    species: SShellSpecies
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

    @property
    def n_alpha(self) -> int:
        return self.species.spin_occupancy[0]

    @property
    def n_beta(self) -> int:
        return self.species.spin_occupancy[1]

    @property
    def target_s2(self) -> float:
        s = 0.5 * (self.n_alpha - self.n_beta)
        return s * (s + 1.0)

    @property
    def spin_contamination(self) -> float:
        return self.s2_expectation - self.target_s2


@dataclass(frozen=True)
class RichardsonSShellResult:
    coarse: SShellUHFResult
    fine: SShellUHFResult
    extrapolated_energy_hartree: float


def _weighted_orthonormalize(vectors: np.ndarray, h: float) -> np.ndarray:
    if vectors.shape[1] == 0:
        return vectors
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
        fock += np.diag(kernel @ (orbital * orbital))
    for orbital in same_spin_occupied:
        fock -= (orbital[:, None] * kernel) * orbital[None, :]
    return 0.5 * (fock + fock.T)


def _coulomb_integral(u: np.ndarray, v: np.ndarray, kernel: np.ndarray, h: float) -> float:
    return float(np.sum((u * u) * (kernel @ (v * v))) * h)


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


def solve_s_shell_uhf(
    species: SShellSpecies,
    *,
    points: int = 400,
    rmax_bohr: float | None = None,
    mixing: float = 0.40,
    tolerance_hartree: float = 2e-9,
    max_iterations: int = 100,
) -> SShellUHFResult:
    if species.nuclear_charge <= 0:
        raise ValueError("nuclear_charge must be positive")
    if not (1 <= species.electron_count <= min(4, species.nuclear_charge)):
        raise ValueError("supported domain is 1..4 electrons with Ne <= Z")
    if points < 80:
        raise ValueError("points must be >= 80")
    if not (0.0 < mixing <= 1.0):
        raise ValueError("mixing must be in (0,1]")

    n_alpha, n_beta = species.spin_occupancy
    rmax = species.default_rmax_bohr if rmax_bohr is None else rmax_bohr
    if rmax <= 0.0:
        raise ValueError("rmax_bohr must be positive")

    h = rmax / (points + 1)
    r = h * np.arange(1, points + 1, dtype=float)
    off = np.full(points - 1, -0.5 / h**2)
    kinetic = np.diag(np.full(points, 1.0 / h**2)) + np.diag(off, 1) + np.diag(off, -1)
    nuclear = np.diag(-float(species.nuclear_charge) / r)
    h_core = kinetic + nuclear
    kernel = _coulomb_kernel(r, h)

    max_occ = max(n_alpha, n_beta)
    _, initial_vectors = eigh(h_core, subset_by_index=[0, max_occ - 1], check_finite=False)
    alpha = _weighted_orthonormalize(initial_vectors[:, :n_alpha], h)
    beta = _weighted_orthonormalize(initial_vectors[:, :n_beta], h)

    previous_energy = None
    converged = False
    for iteration in range(1, max_iterations + 1):
        all_occupied = [alpha[:, j] for j in range(n_alpha)] + [beta[:, j] for j in range(n_beta)]

        f_alpha = _build_fock(h_core, kernel, all_occupied, [alpha[:, j] for j in range(n_alpha)])
        _, candidate_alpha = eigh(f_alpha, subset_by_index=[0, n_alpha - 1], check_finite=False)
        candidate_alpha = _weighted_orthonormalize(candidate_alpha, h)
        for column in range(n_alpha):
            if float(np.dot(candidate_alpha[:, column], alpha[:, column]) * h) < 0.0:
                candidate_alpha[:, column] *= -1.0

        if n_beta:
            f_beta = _build_fock(h_core, kernel, all_occupied, [beta[:, j] for j in range(n_beta)])
            _, candidate_beta = eigh(f_beta, subset_by_index=[0, n_beta - 1], check_finite=False)
            candidate_beta = _weighted_orthonormalize(candidate_beta, h)
            for column in range(n_beta):
                if float(np.dot(candidate_beta[:, column], beta[:, column]) * h) < 0.0:
                    candidate_beta[:, column] *= -1.0
        else:
            candidate_beta = beta

        alpha_new = _weighted_orthonormalize((1.0 - mixing) * alpha + mixing * candidate_alpha, h)
        beta_new = _weighted_orthonormalize((1.0 - mixing) * beta + mixing * candidate_beta, h)

        total, kinetic_energy, nuclear_energy, electron_electron = _energy_components(
            kinetic, nuclear, kernel, alpha_new, beta_new, h
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
        kinetic, nuclear, kernel, alpha, beta, h
    )
    return SShellUHFResult(
        species=species,
        points=points,
        rmax_bohr=rmax,
        iterations=iteration,
        converged=converged,
        energy_hartree=total,
        kinetic_hartree=kinetic_energy,
        nuclear_attraction_hartree=nuclear_energy,
        electron_electron_hartree=electron_electron,
        virial_residual_hartree=2.0 * kinetic_energy + nuclear_energy + electron_electron,
        s2_expectation=_s2_expectation(alpha, beta, h),
    )


def solve_s_shell_richardson(
    species: SShellSpecies,
    *,
    coarse_points: int = 400,
    **kwargs,
) -> RichardsonSShellResult:
    fine_points = 2 * coarse_points + 1
    coarse = solve_s_shell_uhf(species, points=coarse_points, **kwargs)
    fine = solve_s_shell_uhf(species, points=fine_points, **kwargs)
    extrapolated = (4.0 * fine.energy_hartree - coarse.energy_hartree) / 3.0
    return RichardsonSShellResult(coarse=coarse, fine=fine, extrapolated_energy_hartree=extrapolated)


def first_blind_batch() -> tuple[SShellSpecies, ...]:
    return (
        SShellSpecies("H", 1, 1),
        SShellSpecies("He+", 2, 1),
        SShellSpecies("Li2+", 3, 1),
        SShellSpecies("Be3+", 4, 1),
        SShellSpecies("He", 2, 2),
        SShellSpecies("Li+", 3, 2),
        SShellSpecies("Be2+", 4, 2),
        SShellSpecies("Li", 3, 3),
        SShellSpecies("Be+", 4, 3),
        SShellSpecies("Be", 4, 4),
    )


def solve_first_blind_batch(*, coarse_points: int = 400) -> tuple[RichardsonSShellResult, ...]:
    return tuple(solve_s_shell_richardson(species, coarse_points=coarse_points) for species in first_blind_batch())
