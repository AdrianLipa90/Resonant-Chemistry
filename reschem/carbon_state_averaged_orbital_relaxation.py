from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.linalg import eigh

from .atomic_hf_average import (
    _analytic_radial_matrices,
    _direct_potential,
    _eval_slater_basis,
    _exchange_matrix,
    _local_matrix,
    _orthonormalize_columns,
    _trap_weights,
)
from .carbon_balanced_valence_ci import (
    _classify_terms,
    _one_body_spin_matrix,
    _selected_determinants,
    _selected_ls_squared,
    _spin_orbitals,
)
from .carbon_balanced_valence_ci_v2 import _build_even_hamiltonian_v2


@dataclass(frozen=True)
class StateAveragedPoint:
    theta_rad: float
    state_average_hartree: float
    ground_energy_hartree: float
    term_absolute_hartree: tuple[tuple[str, float], ...]
    term_relative_cm1: tuple[tuple[str, float], ...]

    def absolute(self, term: str) -> float:
        return dict(self.term_absolute_hartree)[term]

    def relative_cm1(self, term: str) -> float:
        return dict(self.term_relative_cm1)[term]

    def as_dict(self) -> dict:
        return {
            "theta_rad": self.theta_rad,
            "state_average_hartree": self.state_average_hartree,
            "ground_energy_hartree": self.ground_energy_hartree,
            "term_absolute_hartree": dict(self.term_absolute_hartree),
            "term_relative_cm^-1": dict(self.term_relative_cm1),
        }


@dataclass(frozen=True)
class CarbonStateAveragedRelaxationResult:
    objective_terms: tuple[str, ...]
    weights: tuple[float, ...]
    theta_max_rad: float
    points: tuple[StateAveragedPoint, ...]
    baseline_index: int
    best_index: int

    @property
    def baseline(self) -> StateAveragedPoint:
        return self.points[self.baseline_index]

    @property
    def best(self) -> StateAveragedPoint:
        return self.points[self.best_index]

    @property
    def improvement_hartree(self) -> float:
        return self.baseline.state_average_hartree - self.best.state_average_hartree

    def as_dict(self) -> dict:
        return {
            "schema": "RESCHEM_CARBON_STATE_AVERAGED_P_RELAXATION_V0_1",
            "status": "VARIATIONAL_ACTIVE_EXTERNAL_ORBITAL_RELAXATION_CANDIDATE",
            "objective_terms": list(self.objective_terms),
            "weights": list(self.weights),
            "theta_max_rad": self.theta_max_rad,
            "baseline_index": self.baseline_index,
            "best_index": self.best_index,
            "improvement_hartree": self.improvement_hartree,
            "baseline": self.baseline.as_dict(),
            "best": self.best.as_dict(),
            "points": [point.as_dict() for point in self.points],
            "method": (
                "closed-reference carbon orbitals; frozen 1s^2 core; physical 2s plus "
                "two active p radial orbitals; third p radial function external; one-angle "
                "active-external p rotation optimized against an internal state-average of "
                "3P, 1D and 1S absolute CI energies"
            ),
            "limitations": [
                "one active-external p rotation only; this is not full MCSCF/CASSCF",
                "1s^2 core frozen",
                "no simultaneous s or d orbital relaxation",
                "electrostatic nonrelativistic term centers only",
                "finite radial basis and grid",
                "no experimental term energies enter the objective",
                "TIR and affective mappings are absent",
            ],
            "tir_status": "NOT_APPLIED_CONTROL_BASELINE",
            "affective_status": "RESERVED_UNASSIGNED",
        }


def _normalize_weights(weights: tuple[float, ...], count: int) -> tuple[float, ...]:
    if len(weights) != count:
        raise ValueError("weights must match objective terms")
    if any((not math.isfinite(value)) or value < 0.0 for value in weights):
        raise ValueError("weights must be finite and non-negative")
    total = float(sum(weights))
    if total <= 0.0:
        raise ValueError("at least one state-average weight must be positive")
    return tuple(float(value / total) for value in weights)


def _reference_with_external_p(
    *,
    basis_size: int,
    grid_points: int,
    tolerance_hartree: float,
    mixing: float = 0.30,
    max_iterations: int = 160,
):
    """Closed carbon reference with physical 2s and three orthonormal p radials.

    The orbital shapes are generated from the common closed 1s^2 2s^2 field.  The
    active Hamiltonian is then evaluated in the frozen-1s^2 field so that opening
    valence correlation does not double-count the closed-reference mean field.
    """
    z = 6
    zetas = np.geomspace(0.02, 24.0, basis_size)
    r = np.geomspace(1.0e-8, 120.0, grid_points)
    weights = _trap_weights(r)

    s0, _, _, h0 = _analytic_radial_matrices(0, z, zetas)
    basis0 = _eval_slater_basis(0, zetas, r)
    _, coefficients = eigh(h0, s0, subset_by_index=[0, 1], check_finite=False)
    previous_marker = None
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
        marker = sum(
            float(coefficients[:, column] @ fock_s @ coefficients[:, column])
            for column in range(2)
        )
        final_fock_s = fock_s
        if previous_marker is not None and abs(marker - previous_marker) < tolerance_hartree:
            converged = True
            break
        previous_marker = marker

    if not converged or final_fock_s is None:
        raise RuntimeError("closed carbon 1s2 2s2 reference did not converge")

    occupied_radials = basis0 @ coefficients
    u1s = occupied_radials[:, 0]

    # Physical 2s shape from the common closed reference.
    _, vec_s_full = eigh(final_fock_s, s0, subset_by_index=[0, 1], check_finite=False)
    c2s = vec_s_full[:, 1]
    u2s = basis0 @ c2s

    density_full = 2.0 * np.sum(occupied_radials * occupied_radials, axis=1)
    density_1s = 2.0 * u1s * u1s
    direct_full = _direct_potential(density_full, r)
    direct_1s = _direct_potential(density_1s, r)

    fock_s_1s = h0 + _local_matrix(basis0, direct_1s, weights) - _exchange_matrix(
        basis0, u1s, r, weights, 0
    )
    h_s = float(c2s @ fock_s_1s @ c2s)

    # Three p radials span active(2)+external(1).  Shapes come from the common
    # closed reference, while matrix elements use the frozen 1s^2 field.
    s1, _, _, h1 = _analytic_radial_matrices(1, z, zetas)
    basis1 = _eval_slater_basis(1, zetas, r)
    fock_p_full = h1 + _local_matrix(basis1, direct_full, weights)
    for column in range(2):
        fock_p_full -= (1.0 / 3.0) * _exchange_matrix(
            basis1, occupied_radials[:, column], r, weights, 1
        )
    _, cp3 = eigh(fock_p_full, s1, subset_by_index=[0, 2], check_finite=False)
    p_radials3 = basis1 @ cp3

    fock_p_1s = h1 + _local_matrix(basis1, direct_1s, weights) - (1.0 / 3.0) * _exchange_matrix(
        basis1, u1s, r, weights, 1
    )
    h_p3 = cp3.T @ fock_p_1s @ cp3
    h_p3 = 0.5 * (h_p3 + h_p3.T)

    return r, weights, u2s, p_radials3, h_s, h_p3


def _active_p_rotation(theta: float) -> np.ndarray:
    """Map three reference p radials to two active radials.

    p0 is retained.  The second active radial is cos(theta) p1 + sin(theta) p2,
    so theta=0 is the frozen two-p reference and p2 is the external direction.
    """
    c = math.cos(theta)
    s = math.sin(theta)
    return np.asarray([[1.0, 0.0], [0.0, c], [0.0, s]], dtype=float)


def _point_for_theta(
    theta: float,
    *,
    r: np.ndarray,
    weights_grid: np.ndarray,
    u2s: np.ndarray,
    p_radials3: np.ndarray,
    h_s: float,
    h_p3: np.ndarray,
    objective_terms: tuple[str, ...],
    objective_weights: tuple[float, ...],
) -> StateAveragedPoint:
    rotation = _active_p_rotation(theta)
    active_p = p_radials3 @ rotation
    h_p = rotation.T @ h_p3 @ rotation
    h_p = 0.5 * (h_p + h_p.T)

    spatial = [("s0", 0, 0, u2s)]
    for radial in range(2):
        for m in (-1, 0, 1):
            spatial.append((f"p{radial}", 1, m, active_p[:, radial]))

    spin_orbitals = _spin_orbitals(spatial)
    p_flags = tuple(l == 1 for _, _, l, _, _ in spin_orbitals)
    determinants = _selected_determinants(len(spin_orbitals), 4, p_flags)
    one_body = _one_body_spin_matrix(spatial, spin_orbitals, h_s, h_p)
    hamiltonian = _build_even_hamiltonian_v2(
        spatial,
        spin_orbitals,
        determinants,
        one_body,
        r,
        weights_grid,
    )
    l2, s2 = _selected_ls_squared(spatial, spin_orbitals, determinants)
    terms = _classify_terms(hamiltonian, l2, s2)
    ground = float(np.linalg.eigvalsh(hamiltonian)[0])

    relative_hartree = {item.term: float(item.relative_energy_hartree) for item in terms}
    relative_cm1 = {item.term: float(item.relative_energy_cm1) for item in terms}
    missing = [term for term in objective_terms if term not in relative_hartree]
    if missing:
        raise RuntimeError(f"state-average target term(s) absent from CI spectrum: {missing}")

    absolute = {
        term: ground + relative_hartree[term]
        for term in objective_terms
    }
    average = float(sum(weight * absolute[term] for term, weight in zip(objective_terms, objective_weights)))
    return StateAveragedPoint(
        theta_rad=float(theta),
        state_average_hartree=average,
        ground_energy_hartree=ground,
        term_absolute_hartree=tuple((term, absolute[term]) for term in objective_terms),
        term_relative_cm1=tuple((term, relative_cm1[term]) for term in objective_terms),
    )


def solve_carbon_state_averaged_p_relaxation(
    *,
    basis_size: int = 18,
    grid_points: int = 800,
    tolerance_hartree: float = 1.0e-9,
    theta_max_rad: float = 0.35,
    angle_points: int = 9,
    objective_terms: tuple[str, ...] = ("^3P", "^1D", "^1S"),
    weights: tuple[float, ...] = (1.0, 1.0, 1.0),
) -> CarbonStateAveragedRelaxationResult:
    """First variational state-averaged orbital-relaxation gate for carbon.

    This is deliberately narrower than MCSCF: only one active-external radial-p
    rotation is varied.  Because the external p direction is not retained in the
    active CI space, this changes the active subspace and is not a unitary gauge
    rotation of a fixed full-CI space.
    """
    if angle_points < 3 or angle_points % 2 == 0:
        raise ValueError("angle_points must be an odd integer >= 3 so theta=0 is sampled")
    if not math.isfinite(theta_max_rad) or theta_max_rad <= 0.0 or theta_max_rad >= math.pi / 2:
        raise ValueError("theta_max_rad must lie in (0, pi/2)")

    objective_weights = _normalize_weights(weights, len(objective_terms))
    r, weights_grid, u2s, p_radials3, h_s, h_p3 = _reference_with_external_p(
        basis_size=basis_size,
        grid_points=grid_points,
        tolerance_hartree=tolerance_hartree,
    )

    angles = np.linspace(-theta_max_rad, theta_max_rad, angle_points)
    points = tuple(
        _point_for_theta(
            float(theta),
            r=r,
            weights_grid=weights_grid,
            u2s=u2s,
            p_radials3=p_radials3,
            h_s=h_s,
            h_p3=h_p3,
            objective_terms=objective_terms,
            objective_weights=objective_weights,
        )
        for theta in angles
    )
    baseline_index = int(np.argmin(np.abs(angles)))
    best_index = int(np.argmin([point.state_average_hartree for point in points]))
    return CarbonStateAveragedRelaxationResult(
        objective_terms=objective_terms,
        weights=objective_weights,
        theta_max_rad=float(theta_max_rad),
        points=points,
        baseline_index=baseline_index,
        best_index=best_index,
    )
