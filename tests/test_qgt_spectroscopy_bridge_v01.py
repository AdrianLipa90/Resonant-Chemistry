import numpy as np
from reschem.qgt_spectroscopy_bridge_v01 import (
    STATUS, qgt_from_transition_data, transition_operator_defect,
    transition_amplitude, promoted_transition_amplitude, compare_qgt,
)


def test_status_fail_closed():
    assert STATUS["promotion_state"] == "CANDIDATE_ONLY"
    assert STATUS["physical_binding"] == "OPEN"


def test_qgt_two_level_matches_direct_expression():
    E = np.array([0.0, 2.0])
    dx = np.array([[0, 3],[3, 0]],dtype=complex)
    dy = np.array([[0, 1j],[-1j, 0]],dtype=complex)
    q = qgt_from_transition_data(E, np.stack([dx,dy]), 0)
    assert np.isclose(q[0,0], 9/4)
    assert np.isclose(q[1,1], 1/4)
    assert np.isclose(q[0,1], -0.75j)


def test_transition_amplitude_preserved_when_operator_intertwines():
    P = np.vstack([np.eye(2), np.zeros((2,2))]).astype(complex)
    mu = np.array([[0,1],[1,0]],dtype=complex)
    mu_new = np.block([[mu,np.zeros((2,2))],[np.zeros((2,2)),np.zeros((2,2))]])
    assert np.allclose(transition_operator_defect(mu,mu_new,P),0)
    i=np.array([1,0],dtype=complex); f=np.array([0,1],dtype=complex)
    assert np.isclose(transition_amplitude(f,mu,i), promoted_transition_amplitude(f,i,mu_new,P))


def test_compare_qgt_zero_for_match():
    q=np.array([[1,1j],[-1j,2]],dtype=complex)
    out=compare_qgt(q,q.copy())
    assert np.isclose(out["frobenius_norm"],0)
    assert np.isclose(out["max_abs"],0)
