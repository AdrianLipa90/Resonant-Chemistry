import math

import numpy as np
import pytest

from reschem.relational_holonomy_spectroscopy import (
    HolonomyGraphError,
    cycle_rank,
    forest_gauge_potential,
    gauge_equivalent_hamiltonian,
    gauge_transform_phases,
    oriented_cycle_phase,
    phase_dressed_hamiltonian,
    spectral_eigenvalues,
    wilson_loop,
)


def test_cycle_rank_tree_and_ring():
    assert cycle_rank(4, [(0, 1), (1, 2), (2, 3)]) == 0
    assert cycle_rank(3, [(0, 1), (1, 2), (2, 0)]) == 1
    assert cycle_rank(6, [(0, 1), (1, 2), (2, 0), (3, 4)]) == 1


def test_forest_phases_are_gauge_removable():
    edges = [(0, 1), (1, 2), (1, 3)]
    phases = [0.3, -0.8, 1.1]
    chi = forest_gauge_potential(4, edges, phases)
    transformed = gauge_transform_phases(phases, edges, chi)
    assert transformed == pytest.approx(np.zeros(3), abs=1e-12)


def test_cycle_phase_is_gauge_invariant():
    edges = [(0, 1), (1, 2), (2, 0)]
    phases = np.array([0.2, -0.4, 0.9])
    cycle = [(0, +1), (1, +1), (2, +1)]
    chi = [0.7, -0.2, 1.3]
    transformed = gauge_transform_phases(phases, edges, chi)
    assert oriented_cycle_phase(transformed, cycle) == pytest.approx(
        oriented_cycle_phase(phases, cycle)
    )
    assert wilson_loop(transformed, cycle) == pytest.approx(
        wilson_loop(phases, cycle)
    )


def test_gauge_related_hamiltonians_are_unitarily_equivalent():
    edges = [(0, 1), (1, 2), (2, 0)]
    diagonal = [0.1, -0.2, 0.3]
    hoppings = [1.0, 0.8 - 0.1j, 1.2]
    phases = np.array([0.2, -0.4, 0.9])
    chi = np.array([0.7, -0.2, 1.3])

    h = phase_dressed_hamiltonian(diagonal, edges, hoppings, phases)
    transformed_phases = gauge_transform_phases(phases, edges, chi)
    h_from_phases = phase_dressed_hamiltonian(
        diagonal, edges, hoppings, transformed_phases
    )
    h_from_basis = gauge_equivalent_hamiltonian(h, chi)

    assert np.allclose(h_from_phases, h_from_basis, rtol=0.0, atol=1e-12)
    assert spectral_eigenvalues(h_from_phases) == pytest.approx(
        spectral_eigenvalues(h), abs=1e-12
    )


def test_ring_spectrum_depends_on_loop_flux():
    edges = [(0, 1), (1, 2), (2, 0)]
    diagonal = [0.0, 0.0, 0.0]
    hoppings = [1.0, 1.0, 1.0]

    h_zero = phase_dressed_hamiltonian(
        diagonal, edges, hoppings, [0.0, 0.0, 0.0]
    )
    h_flux = phase_dressed_hamiltonian(
        diagonal, edges, hoppings, [0.0, 0.0, math.pi / 2.0]
    )

    assert spectral_eigenvalues(h_zero) == pytest.approx([-1.0, -1.0, 2.0])
    assert spectral_eigenvalues(h_flux) == pytest.approx(
        [-math.sqrt(3.0), 0.0, math.sqrt(3.0)], abs=1e-12
    )


def test_forest_rejects_global_phase_removal_on_cycle():
    with pytest.raises(HolonomyGraphError):
        forest_gauge_potential(
            3,
            [(0, 1), (1, 2), (2, 0)],
            [0.1, 0.2, 0.3],
        )


@pytest.mark.parametrize(
    "call",
    [
        lambda: cycle_rank(0, []),
        lambda: cycle_rank(2, [(0, 0)]),
        lambda: gauge_transform_phases([0.1], [(0, 1)], [0.0]),
        lambda: oriented_cycle_phase([0.1], [(0, 0)]),
    ],
)
def test_fail_closed_graph_domains(call):
    with pytest.raises(HolonomyGraphError):
        call()
