from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import math

import numpy as np

from .ci_helium import (
    _annihilate,
    _create,
    _rhf_fock_basis,
    _two_electron_integrals_s,
)


@dataclass(frozen=True)
class OneBodyStateObservables:
    energy_hartree: float
    natural_occupations: tuple[float, ...]
    one_body_entropy_nats: float
    one_body_linear_entropy: float
    trace: float
    spatial_orbitals: int
    points: int

    def as_dict(self) -> dict:
        return {
            "schema": "RESCHEM_ONE_BODY_STATE_OBSERVABLES_V0_1",
            "energy_hartree": self.energy_hartree,
            "natural_occupations": list(self.natural_occupations),
            "occupation_trace": self.trace,
            "one_body_entropy_nats": self.one_body_entropy_nats,
            "one_body_linear_entropy": self.one_body_linear_entropy,
            "spatial_orbitals": self.spatial_orbitals,
            "points": self.points,
            "status": "STANDARD_QM_STATE_DERIVED_CONTROL",
            "tir_status": "AVAILABLE_AS_INPUT_NOT_INTERPRETED",
        }


def _fci_ground_state(one_body: np.ndarray, eri: np.ndarray):
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
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    return float(eigenvalues[0]), eigenvectors[:, 0], determinants, det_index


def _spin_summed_one_rdm(
    coefficients: np.ndarray,
    determinants: list[int],
    det_index: dict[int, int],
    spatial_orbitals: int,
) -> np.ndarray:
    gamma = np.zeros((spatial_orbitals, spatial_orbitals), dtype=float)
    for col, det in enumerate(determinants):
        c_ket = float(coefficients[col])
        for i in range(spatial_orbitals):
            for j in range(spatial_orbitals):
                for spin in (0, 1):
                    p = 2 * i + spin
                    q = 2 * j + spin
                    step = _annihilate(det, q)
                    if step is None:
                        continue
                    d1, s1 = step
                    step = _create(d1, p)
                    if step is None:
                        continue
                    d2, s2 = step
                    gamma[i, j] += float(coefficients[det_index[d2]]) * c_ket * s1 * s2
    return 0.5 * (gamma + gamma.T)


def helium_ci_one_body_observables(
    *,
    points: int = 399,
    rmax_bohr: float = 20.0,
    spatial_orbitals: int = 5,
    mixing: float = 0.40,
    tolerance_hartree: float = 1e-10,
    max_iterations: int = 80,
) -> OneBodyStateObservables:
    r, h, orbitals, one_body, _, _, converged = _rhf_fock_basis(
        2,
        points=points,
        rmax_bohr=rmax_bohr,
        spatial_orbitals=spatial_orbitals,
        mixing=mixing,
        tolerance_hartree=tolerance_hartree,
        max_iterations=max_iterations,
    )
    if not converged:
        raise RuntimeError("RHF control state did not converge")
    eri = _two_electron_integrals_s(orbitals, r, h)
    energy, coefficients, determinants, det_index = _fci_ground_state(one_body, eri)
    gamma = _spin_summed_one_rdm(coefficients, determinants, det_index, spatial_orbitals)
    occupations = np.linalg.eigvalsh(gamma)[::-1]
    occupations = np.clip(occupations, 0.0, None)
    trace = float(np.sum(occupations))
    probabilities = occupations / trace
    nonzero = probabilities > 1e-15
    entropy = -float(np.sum(probabilities[nonzero] * np.log(probabilities[nonzero])))
    linear_entropy = 1.0 - float(np.sum(probabilities * probabilities))
    return OneBodyStateObservables(
        energy_hartree=energy,
        natural_occupations=tuple(float(x) for x in occupations),
        one_body_entropy_nats=entropy,
        one_body_linear_entropy=linear_entropy,
        trace=trace,
        spatial_orbitals=spatial_orbitals,
        points=points,
    )
