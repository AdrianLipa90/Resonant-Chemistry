import math
import unittest

import numpy as np

from reschem.chemical_berry_loop_control_v01 import (
    ChemicalBerryLoopError,
    discrete_berry_phase,
    discrete_wilson_loop,
    linear_conical_intersection_hamiltonian,
    normalized_eigenstate,
    normalized_overlap_transport,
    rephase_states,
    sampled_lower_state_loop,
)


class ChemicalBerryLoopControlV01Tests(unittest.TestCase):
    def test_linear_conical_intersection_hamiltonian_is_hermitian(self):
        h = linear_conical_intersection_hamiltonian(0.4, -0.7)
        np.testing.assert_allclose(h, h.conjugate().T, rtol=0.0, atol=1e-15)

    def test_encircling_loop_has_pi_berry_phase(self):
        states = sampled_lower_state_loop(samples=32)
        wilson = discrete_wilson_loop(states)
        self.assertAlmostEqual(wilson.real, -1.0, places=12)
        self.assertAlmostEqual(wilson.imag, 0.0, places=12)
        self.assertAlmostEqual(abs(discrete_berry_phase(states)), math.pi, places=12)

    def test_contractible_loop_has_zero_berry_phase(self):
        states = sampled_lower_state_loop(center_x=2.0, radius=0.4, samples=32)
        wilson = discrete_wilson_loop(states)
        self.assertAlmostEqual(wilson.real, 1.0, places=12)
        self.assertAlmostEqual(wilson.imag, 0.0, places=12)
        self.assertAlmostEqual(discrete_berry_phase(states), 0.0, places=12)

    def test_wilson_loop_is_invariant_under_pointwise_rephasing(self):
        states = sampled_lower_state_loop(samples=24)
        phases = tuple(0.37 * k * k - 0.11 * k for k in range(len(states)))
        transformed = rephase_states(states, phases)
        self.assertLess(
            abs(discrete_wilson_loop(states) - discrete_wilson_loop(transformed)),
            1e-12,
        )

    def test_normalized_overlap_transport_rejects_orthogonal_states(self):
        with self.assertRaises(ChemicalBerryLoopError):
            normalized_overlap_transport([1.0, 0.0], [0.0, 1.0])

    def test_invalid_inputs_fail_closed(self):
        with self.assertRaises(ChemicalBerryLoopError):
            linear_conical_intersection_hamiltonian(float("nan"), 0.0)
        with self.assertRaises(ChemicalBerryLoopError):
            normalized_eigenstate(np.array([[0.0, 1.0], [0.0, 0.0]]))
        with self.assertRaises(ChemicalBerryLoopError):
            sampled_lower_state_loop(radius=0.0)
        with self.assertRaises(ChemicalBerryLoopError):
            sampled_lower_state_loop(samples=2)


if __name__ == "__main__":
    unittest.main()
