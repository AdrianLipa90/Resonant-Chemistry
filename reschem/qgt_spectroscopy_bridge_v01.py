from __future__ import annotations
import numpy as np

STATUS = {
    "promotion_state": "CANDIDATE_ONLY",
    "physical_binding": "OPEN",
    "canon_write_authority": False,
    "epistemic": "CHYBA",
    "interface": "PHASENAV_QGT_SPECTROSCOPY_BRIDGE_V0_1",
}


def qgt_from_transition_data(energies, derivative_operators, state_index: int, atol: float = 1e-14):
    E = np.asarray(energies, dtype=float)
    ops = np.asarray(derivative_operators, dtype=complex)
    if ops.ndim != 3 or ops.shape[1:] != (E.size, E.size):
        raise ValueError("derivative_operators must have shape (n_parameters,n_states,n_states)")
    n = int(state_index)
    if not 0 <= n < E.size:
        raise IndexError("state_index out of range")
    q = np.zeros((ops.shape[0], ops.shape[0]), dtype=complex)
    for m in range(E.size):
        if m == n:
            continue
        gap = E[n] - E[m]
        if abs(gap) <= atol:
            raise ValueError("degenerate transition requires a degenerate-subspace treatment")
        for mu in range(ops.shape[0]):
            for nu in range(ops.shape[0]):
                q[mu, nu] += ops[mu, n, m] * ops[nu, m, n] / (gap * gap)
    return q


def transition_operator_defect(operator_old, operator_new, promotion):
    old = np.asarray(operator_old, dtype=complex)
    new = np.asarray(operator_new, dtype=complex)
    P = np.asarray(promotion, dtype=complex)
    return new @ P - P @ old


def transition_amplitude(state_f, operator, state_i):
    sf = np.asarray(state_f, dtype=complex).reshape(-1)
    si = np.asarray(state_i, dtype=complex).reshape(-1)
    op = np.asarray(operator, dtype=complex)
    return complex(sf.conj() @ op @ si)


def promoted_transition_amplitude(state_f, state_i, operator_new, promotion):
    P = np.asarray(promotion, dtype=complex)
    return transition_amplitude(P @ state_f, operator_new, P @ state_i)


def compare_qgt(predicted, spectroscopic):
    a = np.asarray(predicted, dtype=complex)
    b = np.asarray(spectroscopic, dtype=complex)
    if a.shape != b.shape:
        raise ValueError("QGT shapes must match")
    delta = a - b
    return {
        "delta": delta,
        "frobenius_norm": float(np.linalg.norm(delta)),
        "max_abs": float(np.max(np.abs(delta))) if delta.size else 0.0,
    }
