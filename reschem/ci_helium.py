from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import math

import numpy as np
from scipy.linalg import eigh_tridiagonal

HELIUM_HF_LIMIT_HARTREE = -2.861679995612
HELIUM_EXACT_NONREL_HARTREE = -2.903724377034


def _cumtrap_from_zero(y: np.ndarray, h: float) -> np.ndarray:
    y0 = np.concatenate(([0.0], y))
    return np.cumsum((y0[:-1] + y0[1:]) * (0.5 * h))


def _tailtrap_to_zero(y: np.ndarray, h: float) -> np.ndarray:
    y1 = np.concatenate((y, [0.0]))
    seg = (y1[:-1] + y1[1:]) * (0.5 * h)
    return np.cumsum(seg[::-1])[::-1]


def _radial_coulomb_from_pair(pair: np.ndarray, r: np.ndarray, h: float) -> np.ndarray:
    q_inside = _cumtrap_from_zero(pair, h)
    outer = _tailtrap_to_zero(pair / r, h)
    return q_inside / r + outer


def _normalize(u: np.ndarray, h: float) -> np.ndarray:
    return u / math.sqrt(float(np.sum(u * u) * h))


@dataclass(frozen=True)
class RadialCISnapshot:
    nuclear_charge: int
    points: int
    rmax_bohr: float
    spatial_orbitals: int
    scf_iterations: int
    rhf_energy_hartree: float
    ci_energy_hartree: float
    converged: bool

    @property
    def correlation_lowering_hartree(self) -> float:
        return self.rhf_energy_hartree - self.ci_energy_hartree

    @property
    def recovered_fraction_of_exact_correlation(self) -> float | None:
        if self.nuclear_charge != 2:
            return None
        denominator = HELIUM_HF_LIMIT_HARTREE - HELIUM_EXACT_NONREL_HARTREE
        return max(0.0, (HELIUM_HF_LIMIT_HARTREE - self.ci_energy_hartree) / denominator)


def _rhf_fock_basis(
    nuclear_charge: int,
    *,
    points: int,
    rmax_bohr: float,
    spatial_orbitals: int,
    mixing: float,
    tolerance_hartree: float,
    max_iterations: int,
):
    if nuclear_charge <= 0:
        raise ValueError("nuclear_charge must be positive")
    if points < 80:
        raise ValueError("points must be >= 80")
    if spatial_orbitals < 2:
        raise ValueError("spatial_orbitals must be >= 2")
    if spatial_orbitals >= points:
        raise ValueError("spatial_orbitals must be smaller than points")
    if not (0.0 < mixing <= 1.0):
        raise ValueError("mixing must be in (0,1]")

    h = rmax_bohr / (points + 1)
    r = h * np.arange(1, points + 1, dtype=float)
    off = np.full(points - 1, -0.5 / h**2)
    core_diag = 1.0 / h**2 - float(nuclear_charge) / r

    zeta0 = max(0.2, float(nuclear_charge) - 5.0 / 16.0)
    u = _normalize(2.0 * zeta0**1.5 * r * np.exp(-zeta0 * r), h)

    previous_energy = None
    converged = False
    total_energy = float("nan")
    for iteration in range(1, max_iterations + 1):
        j = _radial_coulomb_from_pair(u * u, r, h)
        _, eigenvectors = eigh_tridiagonal(
            core_diag + j,
            off,
            select="i",
            select_range=(0, spatial_orbitals - 1),
            check_finite=False,
        )
        candidate = _normalize(eigenvectors[:, 0], h)
        if float(np.dot(candidate, u)) < 0.0:
            candidate = -candidate
        mixed = _normalize((1.0 - mixing) * u + mixing * candidate, h)

        j_mixed = _radial_coulomb_from_pair(mixed * mixed, r, h)
        h_mixed = core_diag * mixed
        h_mixed[:-1] += off * mixed[1:]
        h_mixed[1:] += off * mixed[:-1]
        h_expect = float(np.sum(mixed * h_mixed) * h)
        coulomb = float(np.sum((mixed * mixed) * j_mixed) * h)
        total_energy = 2.0 * h_expect + coulomb

        if previous_energy is not None and abs(total_energy - previous_energy) < tolerance_hartree:
            u = mixed
            converged = True
            break
        u = mixed
        previous_energy = total_energy

    j = _radial_coulomb_from_pair(u * u, r, h)
    _, vectors = eigh_tridiagonal(
        core_diag + j,
        off,
        select="i",
        select_range=(0, spatial_orbitals - 1),
        check_finite=False,
    )
    orbitals = vectors / math.sqrt(h)
    if float(np.dot(orbitals[:, 0], u)) < 0.0:
        orbitals[:, 0] *= -1.0

    h_orbitals = core_diag[:, None] * orbitals
    h_orbitals[:-1, :] += off[:, None] * orbitals[1:, :]
    h_orbitals[1:, :] += off[:, None] * orbitals[:-1, :]
    one_body = orbitals.T @ h_orbitals * h
    return r, h, orbitals, one_body, total_energy, iteration, converged


def _two_electron_integrals_s(
    orbitals: np.ndarray,
    r: np.ndarray,
    h: float,
) -> np.ndarray:
    """Return (ij|kl) for spherical s orbitals.

    With u_i(r)=r R_i(r), angular integration reduces the Coulomb kernel
    to 1/max(r1,r2). This therefore captures radial correlation only.
    """
    m = orbitals.shape[1]
    pair = {(i, j): orbitals[:, i] * orbitals[:, j] for i in range(m) for j in range(m)}
    potentials = {
        (k, l): _radial_coulomb_from_pair(pair[(k, l)], r, h)
        for k in range(m)
        for l in range(m)
    }
    eri = np.empty((m, m, m, m), dtype=float)
    for i in range(m):
        for j in range(m):
            f = pair[(i, j)]
            for k in range(m):
                for l in range(m):
                    eri[i, j, k, l] = float(np.sum(f * potentials[(k, l)]) * h)
    return eri


def _annihilate(det: int, q: int):
    if not ((det >> q) & 1):
        return None
    sign = -1 if (det & ((1 << q) - 1)).bit_count() % 2 else 1
    return det ^ (1 << q), sign


def _create(det: int, p: int):
    if (det >> p) & 1:
        return None
    sign = -1 if (det & ((1 << p) - 1)).bit_count() % 2 else 1
    return det | (1 << p), sign


def _fci_two_electron_ground_energy(one_body: np.ndarray, eri: np.ndarray) -> float:
    """Exact diagonalization within the supplied finite s-orbital basis."""
    m = one_body.shape[0]
    nso = 2 * m
    determinants = [sum(1 << p for p in occ) for occ in combinations(range(nso), 2)]
    det_index = {det: idx for idx, det in enumerate(determinants)}
    matrix = np.zeros((len(determinants), len(determinants)), dtype=float)

    for col, det in enumerate(determinants):
        for p in range(nso):
            ip, spin_p = divmod(p, 2)
            for q in range(nso):
                iq, spin_q = divmod(q, 2)
                if spin_p != spin_q:
                    continue
                step = _annihilate(det, q)
                if step is None:
                    continue
                d1, s1 = step
                step = _create(d1, p)
                if step is None:
                    continue
                d2, s2 = step
                matrix[det_index[d2], col] += one_body[ip, iq] * s1 * s2

        for p in range(nso):
            ip, spin_p = divmod(p, 2)
            for q in range(nso):
                iq, spin_q = divmod(q, 2)
                if spin_p != spin_q:
                    continue
                for rr in range(nso):
                    ir, spin_r = divmod(rr, 2)
                    for s in range(nso):
                        is_, spin_s = divmod(s, 2)
                        if spin_r != spin_s:
                            continue
                        value = 0.5 * eri[ip, iq, ir, is_]
                        if abs(value) < 1e-15:
                            continue
                        step = _annihilate(det, q)
                        if step is None:
                            continue
                        d1, s1 = step
                        step = _annihilate(d1, s)
                        if step is None:
                            continue
                        d2, s2 = step
                        step = _create(d2, rr)
                        if step is None:
                            continue
                        d3, s3 = step
                        step = _create(d3, p)
                        if step is None:
                            continue
                        d4, s4 = step
                        matrix[det_index[d4], col] += value * s1 * s2 * s3 * s4

    matrix = 0.5 * (matrix + matrix.T)
    return float(np.linalg.eigvalsh(matrix)[0])


def solve_helium_radial_ci(
    nuclear_charge: int = 2,
    *,
    points: int = 399,
    rmax_bohr: float = 20.0,
    spatial_orbitals: int = 5,
    mixing: float = 0.40,
    tolerance_hartree: float = 1e-10,
    max_iterations: int = 80,
) -> RadialCISnapshot:
    r, h, orbitals, one_body, rhf_energy, iterations, converged = _rhf_fock_basis(
        nuclear_charge,
        points=points,
        rmax_bohr=rmax_bohr,
        spatial_orbitals=spatial_orbitals,
        mixing=mixing,
        tolerance_hartree=tolerance_hartree,
        max_iterations=max_iterations,
    )
    eri = _two_electron_integrals_s(orbitals, r, h)
    ci_energy = _fci_two_electron_ground_energy(one_body, eri)
    return RadialCISnapshot(
        nuclear_charge=nuclear_charge,
        points=points,
        rmax_bohr=rmax_bohr,
        spatial_orbitals=spatial_orbitals,
        scf_iterations=iterations,
        rhf_energy_hartree=rhf_energy,
        ci_energy_hartree=ci_energy,
        converged=converged,
    )


@dataclass(frozen=True)
class RichardsonCIResult:
    coarse: RadialCISnapshot
    fine: RadialCISnapshot
    extrapolated_ci_energy_hartree: float

    @property
    def correlation_lowering_vs_hf_limit_hartree(self) -> float | None:
        if self.coarse.nuclear_charge != 2:
            return None
        return HELIUM_HF_LIMIT_HARTREE - self.extrapolated_ci_energy_hartree

    @property
    def recovered_fraction_of_exact_correlation(self) -> float | None:
        if self.coarse.nuclear_charge != 2:
            return None
        full = HELIUM_HF_LIMIT_HARTREE - HELIUM_EXACT_NONREL_HARTREE
        return max(0.0, self.correlation_lowering_vs_hf_limit_hartree / full)


def solve_helium_radial_ci_richardson(
    nuclear_charge: int = 2,
    *,
    coarse_points: int = 399,
    rmax_bohr: float = 20.0,
    spatial_orbitals: int = 5,
    **kwargs,
) -> RichardsonCIResult:
    fine_points = 2 * coarse_points + 1
    coarse = solve_helium_radial_ci(
        nuclear_charge,
        points=coarse_points,
        rmax_bohr=rmax_bohr,
        spatial_orbitals=spatial_orbitals,
        **kwargs,
    )
    fine = solve_helium_radial_ci(
        nuclear_charge,
        points=fine_points,
        rmax_bohr=rmax_bohr,
        spatial_orbitals=spatial_orbitals,
        **kwargs,
    )
    extrapolated = (4.0 * fine.ci_energy_hartree - coarse.ci_energy_hartree) / 3.0
    return RichardsonCIResult(
        coarse=coarse,
        fine=fine,
        extrapolated_ci_energy_hartree=extrapolated,
    )
