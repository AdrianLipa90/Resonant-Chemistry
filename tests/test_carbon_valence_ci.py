import unittest

from reschem.carbon_valence_ci import (
    _mixed_angular_coulomb_coefficient,
    solve_carbon_valence_sp_ci,
)
from reschem.multiplet_angular import _angular_coulomb_coefficient


class CarbonValenceCITests(unittest.TestCase):
    def test_mixed_angular_kernel_reduces_to_existing_p_shell_kernel(self):
        for m1 in (-1, 0, 1):
            for m2 in (-1, 0, 1):
                for m3 in (-1, 0, 1):
                    for m4 in (-1, 0, 1):
                        for k in (0, 2):
                            old = _angular_coulomb_coefficient(1, m1, m2, m3, m4, k)
                            new = _mixed_angular_coulomb_coefficient(
                                1, m1, 1, m2, 1, m3, 1, m4, k
                            )
                            self.assertAlmostEqual(old, new, places=12)

    def test_carbon_physical_sp_space(self):
        result = solve_carbon_valence_sp_ci(
            basis_size=16,
            grid_points=600,
            tolerance_hartree=2.0e-9,
        )
        self.assertEqual(result.determinant_count, 70)
        self.assertEqual(result.ground_term, "^3P")
        self.assertGreater(result.term_energy_cm1("^1D"), 0.0)
        self.assertGreater(result.term_energy_cm1("^1S"), result.term_energy_cm1("^1D"))

    def test_carbon_sp_resolution_stability(self):
        coarse = solve_carbon_valence_sp_ci(
            basis_size=16,
            grid_points=600,
            tolerance_hartree=2.0e-9,
        )
        fine = solve_carbon_valence_sp_ci(
            basis_size=18,
            grid_points=800,
            tolerance_hartree=1.0e-9,
        )
        self.assertLess(abs(coarse.term_energy_cm1("^1D") - fine.term_energy_cm1("^1D")), 100.0)
        self.assertLess(abs(coarse.term_energy_cm1("^1S") - fine.term_energy_cm1("^1S")), 100.0)


if __name__ == "__main__":
    unittest.main()
