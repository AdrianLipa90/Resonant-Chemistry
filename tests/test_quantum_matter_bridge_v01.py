import math

import numpy as np
import pytest

from reschem.relational_holonomy_spectroscopy import (
    cycle_rank,
    phase_dressed_hamiltonian,
    spectral_eigenvalues,
)
from reschem.quantum_matter_bridge_v01 import (
    QuantumMatterBridgeError,
    common_mode_perturbation,
    first_order_energy_shift,
    h2plus_total_born_oppenheimer_energy,
    transition_angular_shift,
    validate_hermitian_operator,
    validate_state,
)


def test_normalized_state_and_hermitian_operator_are_admitted():
    psi = validate_state([1.0, 0.0])
    op = validate_hermitian_operator([[1.0, 0.2j], [-0.2j, 2.0]])
    assert psi.shape == (2,)
    assert op.shape == (2, 2)


def test_non_normalized_or_non_hermitian_inputs_fail_closed():
    with pytest.raises(QuantumMatterBridgeError):
        validate_state([1.0, 1.0])
    with pytest.raises(QuantumMatterBridgeError):
        validate_hermitian_operator([[0.0, 1.0], [0.0, 0.0]])


def test_first_order_shift_is_standard_expectation_value():
    psi = np.array([1.0, 0.0], dtype=np.complex128)
    perturbation = np.diag([1.25, 4.0])
    assert math.isclose(
        first_order_energy_shift(psi, perturbation),
        1.25,
        rel_tol=0.0,
        abs_tol=1e-12,
    )


def test_common_mode_perturbation_has_exact_transition_null():
    lower = np.array([1.0, 0.0], dtype=np.complex128)
    upper = np.array([0.0, 1.0], dtype=np.complex128)
    perturbation = common_mode_perturbation(2, 3.2)
    assert transition_angular_shift(lower, upper, perturbation) == 0.0


def test_differential_state_coupling_changes_transition_frequency():
    lower = np.array([1.0, 0.0], dtype=np.complex128)
    upper = np.array([0.0, 1.0], dtype=np.complex128)
    perturbation = np.diag([1.0, 3.0])
    assert math.isclose(
        transition_angular_shift(lower, upper, perturbation, hbar=2.0),
        1.0,
        rel_tol=0.0,
        abs_tol=1e-12,
    )


def test_h2plus_born_oppenheimer_bookkeeping_adds_nuclear_repulsion():
    assert math.isclose(
        h2plus_total_born_oppenheimer_energy(-1.5, 2.0),
        -1.0,
        rel_tol=0.0,
        abs_tol=1e-12,
    )


@pytest.mark.parametrize("distance", [0.0, -1.0, float("inf"), float("nan")])
def test_h2plus_distance_domain_fails_closed(distance):
    with pytest.raises(QuantumMatterBridgeError):
        h2plus_total_born_oppenheimer_energy(-1.0, distance)


def test_minimal_two_centre_graph_is_exact_holonomy_negative_control():
    edges = [(0, 1)]
    assert cycle_rank(2, edges) == 0

    h_zero = phase_dressed_hamiltonian(
        [0.0, 1.0],
        edges,
        [0.4],
        [0.0],
    )
    h_phase = phase_dressed_hamiltonian(
        [0.0, 1.0],
        edges,
        [0.4],
        [1.234],
    )
    np.testing.assert_allclose(
        spectral_eigenvalues(h_zero),
        spectral_eigenvalues(h_phase),
        rtol=0.0,
        atol=1e-12,
    )
