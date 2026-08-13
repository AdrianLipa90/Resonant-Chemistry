import unittest

from reschem.carbon_balanced_valence_ci_v2 import solve_carbon_balanced_valence_ci_v2


class CarbonBalancedValenceCITests(unittest.TestCase):
    def test_balanced_space_is_even_and_physical(self):
        result = solve_carbon_balanced_valence_ci_v2(
            basis_size=16,
            grid_points=600,
            tolerance_hartree=2.0e-9,
        )
        self.assertEqual(result.p_radial_orbitals, 2)
        self.assertEqual(result.spin_orbitals, 14)
        self.assertEqual(result.even_determinants, 561)
        self.assertEqual(result.ground_term, "^3P")
        self.assertGreater(result.term_energy_cm1("^1D"), 0.0)
        self.assertGreater(result.term_energy_cm1("^1S"), result.term_energy_cm1("^1D"))

    def test_balanced_space_resolution_is_stable(self):
        coarse = solve_carbon_balanced_valence_ci_v2(
            basis_size=16,
            grid_points=600,
            tolerance_hartree=2.0e-9,
        )
        fine = solve_carbon_balanced_valence_ci_v2(
            basis_size=18,
            grid_points=800,
            tolerance_hartree=1.0e-9,
        )
        self.assertLess(abs(coarse.term_energy_cm1("^1D") - fine.term_energy_cm1("^1D")), 200.0)
        self.assertLess(abs(coarse.term_energy_cm1("^1S") - fine.term_energy_cm1("^1S")), 200.0)


if __name__ == "__main__":
    unittest.main()
