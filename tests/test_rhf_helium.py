import unittest

from reschem.rhf_helium import (
    HELIUM_HF_LIMIT_HARTREE,
    solve_two_electron_rhf,
    solve_two_electron_rhf_richardson,
)


class RHFHeliumTests(unittest.TestCase):
    def test_single_grid_converges(self):
        result = solve_two_electron_rhf(points=149, tolerance_hartree=1e-8)
        self.assertTrue(result.converged)
        self.assertLess(result.energy_hartree, -2.79)

    def test_richardson_reaches_hf_control(self):
        result = solve_two_electron_rhf_richardson(coarse_points=149, tolerance_hartree=1e-8)
        rel = abs(result.extrapolated_energy_hartree - HELIUM_HF_LIMIT_HARTREE) / abs(HELIUM_HF_LIMIT_HARTREE)
        self.assertLess(rel, 3e-4)

    def test_variational_direction(self):
        result = solve_two_electron_rhf_richardson(coarse_points=149, tolerance_hartree=1e-8)
        self.assertGreaterEqual(result.extrapolated_energy_hartree, HELIUM_HF_LIMIT_HARTREE)


if __name__ == "__main__":
    unittest.main()
