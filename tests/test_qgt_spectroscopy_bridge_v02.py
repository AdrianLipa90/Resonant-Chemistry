import numpy as np

from reschem.qgt_spectroscopy_bridge_v01 import (
    compare_qgt,
    qgt_from_transition_data,
    transition_operator_defect,
)


def _two_parameter_fixture(dim: int):
    energies = np.arange(dim, dtype=float) + 0.5
    operators = np.zeros((2, dim, dim), dtype=complex)
    for m in range(1, dim):
        coeff = 1.0 / (m + 1)
        operators[0, 0, m] = 1.0
        operators[0, m, 0] = 1.0
        operators[1, 0, m] = 1j * coeff
        operators[1, m, 0] = -1j * coeff
    return energies, operators


def _expected_qgt(dim: int):
    q00 = sum(1.0 / (m * m) for m in range(1, dim))
    q11 = sum((1.0 / (m + 1)) ** 2 / (m * m) for m in range(1, dim))
    cross = sum((1.0 / (m + 1)) / (m * m) for m in range(1, dim))
    return np.array([[q00, -1j * cross], [1j * cross, q11]], dtype=complex)


def test_qgt_reconstruction_scales_to_4q_state_space():
    for dim in (2, 4, 8, 16):
        energies, operators = _two_parameter_fixture(dim)
        reconstructed = qgt_from_transition_data(energies, operators, state_index=0)
        expected = _expected_qgt(dim)
        assert np.allclose(reconstructed, expected, atol=1e-12)
        residual = compare_qgt(expected, reconstructed)
        assert residual["frobenius_norm"] < 1e-12
        assert residual["max_abs"] < 1e-12


def test_transition_operator_intertwiner_scales_across_promotions():
    for dim_old in (2, 4, 8):
        promotion = np.vstack([np.eye(dim_old), np.zeros((dim_old, dim_old))]).astype(complex)
        operator_old = np.diag(np.arange(1, dim_old + 1)).astype(complex)
        operator_new = np.block([
            [operator_old, np.zeros((dim_old, dim_old))],
            [np.zeros((dim_old, dim_old)), np.zeros((dim_old, dim_old))],
        ])
        assert np.allclose(
            transition_operator_defect(operator_old, operator_new, promotion),
            0.0,
            atol=1e-12,
        )
