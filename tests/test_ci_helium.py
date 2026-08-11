import unittest

from reschem.ci_helium import (
    HELIUM_HF_LIMIT_HARTREE,
    solve_helium_radial_ci,
    solve_helium_radial_ci_richardson,
)


class HeliumRadialCITests(unittest.TestCase):
    def test_ci_lowers_same_grid_rhf_energy(self):
        result = solve_helium_radial_ci(points=199, spatial_orbitals=5)
        self.assertTrue(result.converged)
        self.assertLess(result.ci_energy_hartree, result.rhf_energy_hartree)
        self.assertGreater(result.correlation_lowering_hartree, 1.0e-4)

    def test_larger_s_basis_is_variationally_lower(self):
        small = solve_helium_radial_ci(points=199, spatial_orbitals=2)
        larger = solve_helium_radial_ci(points=199, spatial_orbitals=5)
        self.assertLess(larger.ci_energy_hartree, small.ci_energy_hartree)

    def test_richardson_ci_crosses_below_hf_limit(self):
        result = solve_helium_radial_ci_richardson(coarse_points=199, spatial_orbitals=5)
        self.assertLess(result.extrapolated_ci_energy_hartree, HELIUM_HF_LIMIT_HARTREE)
        self.assertGreater(result.recovered_fraction_of_exact_correlation, 0.01)
        self.assertLess(result.recovered_fraction_of_exact_correlation, 0.10)


if __name__ == "__main__":
    unittest.main()
