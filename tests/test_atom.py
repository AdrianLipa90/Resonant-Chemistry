import math
import unittest

from reschem.atom import Atom, KAPPA, electron_configuration, hydrogenic_energy_ev


class AtomTests(unittest.TestCase):
    def test_kappa(self):
        self.assertAlmostEqual(KAPPA, math.log(2)/(24*math.pi), places=15)

    def test_hydrogen_ground_state(self):
        h = Atom(1, 0)
        self.assertEqual(h.electron_count, 1)
        self.assertEqual(h.configuration, {"1s": 1})
        self.assertAlmostEqual(hydrogenic_energy_ev(1, 1), -13.605693122994, places=12)

    def test_he_plus_scaling(self):
        he_plus = Atom(2, 2, charge=1)
        self.assertTrue(he_plus.is_hydrogenic)
        self.assertAlmostEqual(hydrogenic_energy_ev(2, 1), 4 * hydrogenic_energy_ev(1, 1), places=12)

    def test_carbon(self):
        self.assertEqual(electron_configuration(6), {"1s": 2, "2s": 2, "2p": 2})

    def test_neon(self):
        self.assertEqual(electron_configuration(10), {"1s": 2, "2s": 2, "2p": 6})

    def test_chromium_exception(self):
        c = electron_configuration(24)
        self.assertEqual(c["4s"], 1)
        self.assertEqual(c["3d"], 5)

    def test_copper_exception(self):
        c = electron_configuration(29)
        self.assertEqual(c["4s"], 1)
        self.assertEqual(c["3d"], 10)

    def test_kr_electron_count(self):
        kr = Atom(36, 48)
        self.assertEqual(sum(kr.configuration.values()), 36)

    def test_invalid_neutrons_fail(self):
        with self.assertRaises(ValueError):
            Atom(1, -1)


if __name__ == "__main__":
    unittest.main()
