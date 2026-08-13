from __future__ import annotations

import math
import unittest

import numpy as np

from reschem.carbon_state_averaged_orbital_relaxation import (
    _active_p_rotation,
    _normalize_weights,
    solve_carbon_state_averaged_p_relaxation,
)


class TestCarbonStateAveragedOrbitalRelaxation(unittest.TestCase):
    def test_weight_normalization(self):
        self.assertEqual(_normalize_weights((1.0, 1.0, 1.0), 3), (1/3, 1/3, 1/3))
        with self.assertRaises(ValueError):
            _normalize_weights((1.0, -1.0, 1.0), 3)
        with self.assertRaises(ValueError):
            _normalize_weights((0.0, 0.0, 0.0), 3)

    def test_active_external_rotation_is_orthonormal(self):
        for theta in (-0.35, -0.1, 0.0, 0.2, 0.35):
            rotation = _active_p_rotation(theta)
            self.assertTrue(np.allclose(rotation.T @ rotation, np.eye(2), atol=1.0e-13))
        baseline = _active_p_rotation(0.0)
        self.assertTrue(np.array_equal(baseline, np.asarray([[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]])))

    def test_small_state_average_scan_is_variational_and_reference_is_sampled(self):
        result = solve_carbon_state_averaged_p_relaxation(
            basis_size=12,
            grid_points=320,
            tolerance_hartree=2.0e-8,
            theta_max_rad=0.12,
            angle_points=3,
        )
        self.assertEqual(result.objective_terms, ("^3P", "^1D", "^1S"))
        self.assertEqual(result.baseline.theta_rad, 0.0)
        self.assertLessEqual(
            result.best.state_average_hartree,
            result.baseline.state_average_hartree + 1.0e-10,
        )
        self.assertGreaterEqual(result.improvement_hartree, -1.0e-10)
        for point in result.points:
            self.assertTrue(math.isfinite(point.state_average_hartree))
            self.assertTrue(math.isfinite(point.ground_energy_hartree))
            for term in result.objective_terms:
                self.assertTrue(math.isfinite(point.absolute(term)))
                self.assertTrue(math.isfinite(point.relative_cm1(term)))
        print("STATE_AVERAGED_P_RELAXATION_SMALL_SCAN", result.as_dict())

    def test_input_gate_requires_odd_scan(self):
        with self.assertRaises(ValueError):
            solve_carbon_state_averaged_p_relaxation(angle_points=4)


if __name__ == "__main__":
    unittest.main()
