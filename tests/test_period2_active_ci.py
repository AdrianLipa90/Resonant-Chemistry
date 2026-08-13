import math
import unittest

from reschem.period2_active_ci import solve_period2_active_p_ci


class Period2ActiveCITests(unittest.TestCase):
    def test_determinant_dimensions_and_ground_terms(self):
        expected = {
            5: (1, "^2P"),
            6: (2, "^3P"),
            7: (3, "^4S"),
            8: (4, "^3P"),
            9: (5, "^2P"),
        }
        for z, (p_count, ground) in expected.items():
            result = solve_period2_active_p_ci(
                z,
                basis_size=16,
                grid_points=600,
                tolerance_hartree=2.0e-8,
            )
            self.assertEqual(result.p_electron_count, p_count)
            self.assertEqual(result.determinant_count, math.comb(12, p_count))
            self.assertEqual(result.ground_term, ground)

    def test_carbon_and_oxygen_problem_terms_move_down(self):
        # Frozen v0.1 equivalent-shell outputs from the previous internal
        # control benchmark.  These are not experimental reference values.
        old = {
            6: {"^1D": 11883.53007264199, "^1S": 29651.44620052055},
            8: {"^1D": 16731.343173153906, "^1S": 41693.71267306029},
        }
        for z in (6, 8):
            result = solve_period2_active_p_ci(
                z,
                basis_size=16,
                grid_points=600,
                tolerance_hartree=2.0e-8,
            )
            for term in ("^1D", "^1S"):
                self.assertLess(result.term_energy_cm1(term), old[z][term])

    def test_nitrogen_ground_and_excited_term_order(self):
        result = solve_period2_active_p_ci(
            7,
            basis_size=16,
            grid_points=600,
            tolerance_hartree=2.0e-8,
        )
        self.assertEqual(result.ground_term, "^4S")
        self.assertGreater(result.term_energy_cm1("^2D"), 0.0)
        self.assertGreater(result.term_energy_cm1("^2P"), result.term_energy_cm1("^2D"))

    def test_resolution_stability_for_carbon(self):
        coarse = solve_period2_active_p_ci(
            6,
            basis_size=16,
            grid_points=600,
            tolerance_hartree=2.0e-8,
        )
        fine = solve_period2_active_p_ci(
            6,
            basis_size=18,
            grid_points=800,
            tolerance_hartree=1.0e-8,
        )
        self.assertLess(abs(coarse.term_energy_cm1("^1D") - fine.term_energy_cm1("^1D")), 20.0)
        self.assertLess(abs(coarse.term_energy_cm1("^1S") - fine.term_energy_cm1("^1S")), 20.0)


if __name__ == "__main__":
    unittest.main()
