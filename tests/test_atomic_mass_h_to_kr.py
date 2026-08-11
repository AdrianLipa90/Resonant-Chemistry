import os
import unittest

from reschem.atom import electron_configuration
from reschem.atomic_mass_h_to_kr import H_TO_KR_Z, K_TO_KR_Z, solve_k_to_kr_robust


class AtomicMassHToKrTests(unittest.TestCase):
    def test_ranges_are_complete_and_ordered(self):
        self.assertEqual(H_TO_KR_Z, tuple(range(1, 37)))
        self.assertEqual(K_TO_KR_Z, tuple(range(19, 37)))

    def test_transition_configuration_exceptions_are_preserved(self):
        self.assertEqual(electron_configuration(24)["4s"], 1)
        self.assertEqual(electron_configuration(24)["3d"], 5)
        self.assertEqual(electron_configuration(29)["4s"], 1)
        self.assertEqual(electron_configuration(29)["3d"], 10)

    def test_kr_closes_4p_shell(self):
        configuration = electron_configuration(36)
        self.assertEqual(configuration["3d"], 10)
        self.assertEqual(configuration["4p"], 6)
        self.assertEqual(sum(configuration.values()), 36)

    @unittest.skipUnless(
        os.environ.get("RESCHEM_SLOW_ATOM_TESTS") == "1",
        "set RESCHEM_SLOW_ATOM_TESTS=1 for the full numerical K-to-Kr gate",
    )
    def test_full_k_to_kr_quality_gate(self):
        batch = solve_k_to_kr_robust()
        self.assertEqual(len(batch.results), 18)
        self.assertEqual(batch.quality_pass_count, 18)
        self.assertTrue(batch.all_quality_pass)
        self.assertLess(batch.worst_abs_virial_hartree, 2.0)


if __name__ == "__main__":
    unittest.main()
