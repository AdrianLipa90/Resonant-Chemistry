import unittest

from reschem.helium import (
    HELIUM_EXACT_NONREL_HARTREE,
    HELIUM_HF_LIMIT_HARTREE,
    optimal_zeta,
    solve_two_electron_variational,
    variational_energy_hartree,
)


class TwoElectronVariationalTests(unittest.TestCase):
    def test_helium_optimum(self):
        self.assertEqual(optimal_zeta(2), 27.0 / 16.0)

    def test_helium_energy_closed_form(self):
        result = solve_two_electron_variational(2)
        self.assertAlmostEqual(result.energy_hartree, -2.84765625, places=12)

    def test_screening_lowers_energy(self):
        screened = solve_two_electron_variational(2).energy_hartree
        unscreened = variational_energy_hartree(2, 2.0)
        self.assertLess(screened, unscreened)

    def test_variational_bound(self):
        result = solve_two_electron_variational(2)
        self.assertGreaterEqual(result.energy_hartree, HELIUM_EXACT_NONREL_HARTREE)

    def test_hf_gap_is_visible(self):
        result = solve_two_electron_variational(2)
        rel = abs(result.energy_hartree - HELIUM_HF_LIMIT_HARTREE) / abs(HELIUM_HF_LIMIT_HARTREE)
        self.assertLess(rel, 0.005)

    def test_virial_at_optimum(self):
        result = solve_two_electron_variational(2)
        self.assertAlmostEqual(result.virial_residual_hartree, 0.0, places=12)


if __name__ == "__main__":
    unittest.main()
