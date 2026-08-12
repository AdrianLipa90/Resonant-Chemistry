import unittest

from reschem.carbon_valence_ci_consistent import solve_carbon_valence_sp_ci_consistent


class CarbonValenceCIConsistentTests(unittest.TestCase):
    def test_consistent_open_2s_space_remains_physical(self):
        result = solve_carbon_valence_sp_ci_consistent(
            basis_size=16,
            grid_points=600,
            tolerance_hartree=2.0e-9,
        )
        self.assertEqual(result.determinant_count, 70)
        self.assertEqual(result.ground_term, "^3P")
        self.assertGreater(result.term_energy_cm1("^1D"), 0.0)
        self.assertGreater(result.term_energy_cm1("^1S"), result.term_energy_cm1("^1D"))

    def test_consistent_open_2s_resolution_stability(self):
        coarse = solve_carbon_valence_sp_ci_consistent(
            basis_size=16,
            grid_points=600,
            tolerance_hartree=2.0e-9,
        )
        fine = solve_carbon_valence_sp_ci_consistent(
            basis_size=18,
            grid_points=800,
            tolerance_hartree=1.0e-9,
        )
        self.assertLess(abs(coarse.term_energy_cm1("^1D") - fine.term_energy_cm1("^1D")), 150.0)
        self.assertLess(abs(coarse.term_energy_cm1("^1S") - fine.term_energy_cm1("^1S")), 150.0)


if __name__ == "__main__":
    unittest.main()
