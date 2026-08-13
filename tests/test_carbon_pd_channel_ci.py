import unittest

from reschem.carbon_pd_channel_ci import solve_carbon_pd_channel_ci


class CarbonPDChannelCITests(unittest.TestCase):
    def test_pd_space_dimension_and_ground_term(self):
        result = solve_carbon_pd_channel_ci(
            basis_size=16,
            grid_points=600,
            tolerance_hartree=2.0e-9,
        )
        self.assertEqual(result.spin_orbitals, 22)
        self.assertEqual(result.even_determinants, 111)
        self.assertEqual(result.ground_term, "^3P")
        self.assertGreater(result.term_energy_cm1("^1D"), 0.0)
        self.assertGreater(result.term_energy_cm1("^1S"), result.term_energy_cm1("^1D"))

    def test_pd_resolution_stability(self):
        coarse = solve_carbon_pd_channel_ci(
            basis_size=16,
            grid_points=600,
            tolerance_hartree=2.0e-9,
        )
        fine = solve_carbon_pd_channel_ci(
            basis_size=18,
            grid_points=800,
            tolerance_hartree=1.0e-9,
        )
        self.assertLess(abs(coarse.term_energy_cm1("^1D") - fine.term_energy_cm1("^1D")), 200.0)
        self.assertLess(abs(coarse.term_energy_cm1("^1S") - fine.term_energy_cm1("^1S")), 200.0)


if __name__ == "__main__":
    unittest.main()
