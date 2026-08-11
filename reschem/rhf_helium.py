from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

HELIUM_HF_LIMIT_HARTREE = -2.861679995612


def _cumtrap_from_zero(y: np.ndarray, h: float) -> np.ndarray:
    y0 = np.concatenate(([0.0], y))
    return np.cumsum((y0[:-1] + y0[1:]) * (0.5 * h))


def _tailtrap_to_zero(y: np.ndarray, h: float) -> np.ndarray:
    y1 = np.concatenate((y, [0.0]))
    seg = (y1[:-1] + y1[1:]) * (0.5 * h)
    return np.cumsum(seg[::-1])[::-1]


def _coulomb_potential(u: np.ndarray, r: np.ndarray, h: float) -> np.ndarray:
    rho = u * u
    q_inside = _cumtrap_from_zero(rho, h)
    outer = _tailtrap_to_zero(rho / r, h)
    return q_inside / r + outer


@dataclass(frozen=True)
class RHFResult:
    nuclear_charge: int
    points: int
    rmax_bohr: float
    iterations: int
    energy_hartree: float
    orbital_energy_hartree: float
    converged: bool

    @property
    def relative_error_vs_helium_hf_limit(self) -> float | None:
        if self.nuclear_charge != 2:
            return None
        return abs(self.energy_hartree - HELIUM_HF_LIMIT_HARTREE) / abs(HELIUM_HF_LIMIT_HARTREE)


def solve_two_electron_rhf(
    nuclear_charge: int = 2,
    *,
    points: int = 399,
    rmax_bohr: float = 20.0,
    max_iterations: int = 80,
    mixing: float = 0.40,
    tolerance_hartree: float = 1e-10,
) -> RHFResult:
    """Spherical restricted-Hartree-Fock solver for a helium-like 1s^2 ion.

    The doubly occupied spatial orbital is represented by u(r)=r R(r).
    Each electron sees the Coulomb field of the opposite-spin electron.
    TIR terms are deliberately absent: this is the conventional control layer.
    """
    if nuclear_charge <= 0:
        raise ValueError("nuclear_charge must be positive")
    if points < 40:
        raise ValueError("points must be >= 40")
    if rmax_bohr <= 0:
        raise ValueError("rmax_bohr must be positive")
    if not (0.0 < mixing <= 1.0):
        raise ValueError("mixing must be in (0,1]")

    h = rmax_bohr / (points + 1)
    r = h * np.arange(1, points + 1, dtype=float)

    zeta0 = max(0.2, float(nuclear_charge) - 5.0 / 16.0)
    u = 2.0 * zeta0**1.5 * r * np.exp(-zeta0 * r)
    u /= math.sqrt(float(np.sum(u * u) * h))

    off = np.full(points - 1, -0.5 / h**2)
    core_diag = 1.0 / h**2 - float(nuclear_charge) / r
    h_core = np.diag(core_diag) + np.diag(off, 1) + np.diag(off, -1)

    previous_energy = None
    converged = False
    orbital_energy = float("nan")

    for iteration in range(1, max_iterations + 1):
        j = _coulomb_potential(u, r, h)
        fock = h_core + np.diag(j)
        eigenvalues, eigenvectors = np.linalg.eigh(fock)
        candidate = eigenvectors[:, 0]
        orbital_energy = float(eigenvalues[0])

        if float(np.dot(candidate, u)) < 0.0:
            candidate = -candidate
        candidate /= math.sqrt(float(np.sum(candidate * candidate) * h))

        mixed = (1.0 - mixing) * u + mixing * candidate
        mixed /= math.sqrt(float(np.sum(mixed * mixed) * h))

        j_mixed = _coulomb_potential(mixed, r, h)
        h_expect = float(mixed @ (h_core @ mixed) * h)
        coulomb = float(np.sum((mixed * mixed) * j_mixed) * h)
        total_energy = 2.0 * h_expect + coulomb

        if previous_energy is not None and abs(total_energy - previous_energy) < tolerance_hartree:
            u = mixed
            converged = True
            break

        u = mixed
        previous_energy = total_energy

    return RHFResult(
        nuclear_charge=nuclear_charge,
        points=points,
        rmax_bohr=rmax_bohr,
        iterations=iteration,
        energy_hartree=total_energy,
        orbital_energy_hartree=orbital_energy,
        converged=converged,
    )


@dataclass(frozen=True)
class RichardsonRHFResult:
    coarse: RHFResult
    fine: RHFResult
    extrapolated_energy_hartree: float

    @property
    def relative_error_vs_helium_hf_limit(self) -> float | None:
        if self.coarse.nuclear_charge != 2:
            return None
        return abs(self.extrapolated_energy_hartree - HELIUM_HF_LIMIT_HARTREE) / abs(HELIUM_HF_LIMIT_HARTREE)


def solve_two_electron_rhf_richardson(
    nuclear_charge: int = 2,
    *,
    coarse_points: int = 399,
    rmax_bohr: float = 20.0,
    **kwargs,
) -> RichardsonRHFResult:
    """Second-order grid extrapolation using h and h/2."""
    fine_points = 2 * coarse_points + 1
    coarse = solve_two_electron_rhf(
        nuclear_charge,
        points=coarse_points,
        rmax_bohr=rmax_bohr,
        **kwargs,
    )
    fine = solve_two_electron_rhf(
        nuclear_charge,
        points=fine_points,
        rmax_bohr=rmax_bohr,
        **kwargs,
    )
    extrapolated = (4.0 * fine.energy_hartree - coarse.energy_hartree) / 3.0
    return RichardsonRHFResult(coarse=coarse, fine=fine, extrapolated_energy_hartree=extrapolated)
