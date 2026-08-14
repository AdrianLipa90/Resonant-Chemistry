import unittest

from reschem.atom import electron_configuration


class ClosedShellIonBookkeepingTests(unittest.TestCase):
    def test_f_minus_is_neon_like_occupancy(self):
        self.assertEqual(electron_configuration(9, -1), electron_configuration(10, 0))

    def test_cl_minus_is_argon_like_occupancy(self):
        self.assertEqual(electron_configuration(17, -1), electron_configuration(18, 0))

    def test_br_minus_is_krypton_like_occupancy(self):
        self.assertEqual(electron_configuration(35, -1), electron_configuration(36, 0))

    def test_closed_shell_anions_have_expected_electron_counts(self):
        for z in (9, 17, 35):
            self.assertEqual(sum(electron_configuration(z, -1).values()), z + 1)


if __name__ == "__main__":
    unittest.main()
