"""Executable helpers for RELATIONAL_INVARIANT_CONTRACT_V0_1.

These routines expose representation-invariant objects and gauge-fixing
operations used by Resonant Chemistry. They do not introduce new physics.
"""
from __future__ import annotations

import numpy as np

INVARIANT_CONTRACT_ID = "RELATIONAL_INVARIANT_CONTRACT_V0_1"
OES_ORBITAL_UNITARY_BASIS_PROFILE_ID = "OES_ORBITAL_UNITARY_BASIS_V0_1"


class RelationalInvariantError(ValueError):
    pass


def _matrix(name: str, value, *, square: bool = False) -> np.ndarray:
    out = np.asarray(value, dtype=complex)
    if out.ndim != 2 or out.shape[0] == 0 or out.shape[1] == 0:
        raise RelationalInvariantError(f"{name} must be a non-empty 2D matrix")
    if square and out.shape[0] != out.shape[1]:
        raise RelationalInvariantError(f"{name} must be square")
    if not np.all(np.isfinite(out.real)) or not np.all(np.isfinite(out.imag)):
        raise RelationalInvariantError(f"{name} must be finite")
    return out


def _positive_metric(overlap) -> np.ndarray:
    s = _matrix("overlap", overlap, square=True)
    if not np.allclose(s, s.conjugate().T, rtol=0.0, atol=1e-12):
        raise RelationalInvariantError("overlap must be Hermitian")
    eigenvalues = np.linalg.eigvalsh(s)
    if np.min(eigenvalues) <= 0.0:
        raise RelationalInvariantError("overlap must be positive definite")
    return s


def s_metric_projector(coefficients, overlap) -> np.ndarray:
    """Project onto span(C) in the positive S metric.

    P_S = C (C^† S C)^-1 C^† S is invariant under C -> C U for every
    invertible change of basis U inside the represented subspace.
    """

    c = _matrix("coefficients", coefficients)
    s = _positive_metric(overlap)
    if c.shape[0] != s.shape[0]:
        raise RelationalInvariantError("coefficient row count must match overlap dimension")
    gram = c.conjugate().T @ s @ c
    if not np.allclose(gram, gram.conjugate().T, rtol=0.0, atol=1e-12):
        raise RelationalInvariantError("coefficient Gram matrix must be Hermitian")
    if np.min(np.linalg.eigvalsh(gram)) <= 1e-14:
        raise RelationalInvariantError("coefficients must have full S-metric column rank")
    return c @ np.linalg.solve(gram, c.conjugate().T @ s)


def s_metric_projector_residual(coefficients_a, coefficients_b, overlap) -> float:
    pa = s_metric_projector(coefficients_a, overlap)
    pb = s_metric_projector(coefficients_b, overlap)
    return float(np.max(np.abs(pa - pb)))


def align_s_metric_subspace(current, candidate, overlap) -> tuple[np.ndarray, np.ndarray]:
    """Right-align candidate to current by S-metric orthogonal Procrustes.

    This is numerical gauge fixing only. The returned rotation is unitary and
    the candidate subspace projector is unchanged.
    """

    old = _matrix("current", current)
    new = _matrix("candidate", candidate)
    s = _positive_metric(overlap)
    if old.shape != new.shape:
        raise RelationalInvariantError("current and candidate must have the same shape")
    if old.shape[0] != s.shape[0]:
        raise RelationalInvariantError("coefficient row count must match overlap dimension")

    metric_overlap = old.conjugate().T @ s @ new
    u, _, vh = np.linalg.svd(metric_overlap, full_matrices=False)
    rotation = vh.conjugate().T @ u.conjugate().T
    aligned = new @ rotation

    if not np.allclose(
        rotation.conjugate().T @ rotation,
        np.eye(rotation.shape[0]),
        rtol=0.0,
        atol=1e-12,
    ):
        raise RelationalInvariantError("Procrustes rotation lost unitarity")
    return aligned, rotation


def oes_representation_contract_block() -> dict[str, object]:
    """Return the additive RC -> OES representation-contract declaration."""

    return {
        "schema": INVARIANT_CONTRACT_ID,
        "profile": OES_ORBITAL_UNITARY_BASIS_PROFILE_ID,
        "orbital_gauge_group": "U(n)",
        "transition_rdm_covariance": "T'=U^T T U^*",
        "transition_density_status": "INVARIANT_UNDER_MATCHED_ORBITAL_UNITARY_BASIS_CHANGE",
        "state_ray_phase_status": (
            "GLOBAL_U1_COVARIANT__AMPLITUDE_NODES_RELATIVE_PHASE_INTENSITY_INVARIANT"
        ),
    }


__all__ = [
    "INVARIANT_CONTRACT_ID",
    "OES_ORBITAL_UNITARY_BASIS_PROFILE_ID",
    "RelationalInvariantError",
    "s_metric_projector",
    "s_metric_projector_residual",
    "align_s_metric_subspace",
    "oes_representation_contract_block",
]
