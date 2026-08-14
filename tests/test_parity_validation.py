import unittest

from reschem.parity_validation import (
    parity_only_degrees,
    retrospective_period_gate_panel,
    sf_parity_benchmark,
    shell_gated_degrees,
)


class ParityValidationTests(unittest.TestCase):
    def test_second_period_null_expands_but_shell_gate_does_not(self):
        self.assertEqual(parity_only_degrees(7), (3, 5))   # N
        self.assertEqual(shell_gated_degrees(7), (3,))
        self.assertEqual(parity_only_degrees(8), (2, 4, 6))  # O
        self.assertEqual(shell_gated_degrees(8), (2,))

    def test_third_period_shell_gate_matches_parity_ladder(self):
        self.assertEqual(parity_only_degrees(15), (3, 5))
        self.assertEqual(shell_gated_degrees(15), (3, 5))
        self.assertEqual(parity_only_degrees(16), (2, 4, 6))
        self.assertEqual(shell_gated_degrees(16), (2, 4, 6))

    def test_sf_energy_sequence_gives_no_incremental_auc(self):
        result = sf_parity_benchmark(
            {2: 89.5, 3: 54.5, 4: 96.2, 5: 39.2, 6: 105.6}
        )
        self.assertTrue(result["identical_labels"])
        self.assertAlmostEqual(result["M0"]["auc"], 1.0)
        self.assertAlmostEqual(result["M1"]["auc"], 1.0)
        self.assertAlmostEqual(result["delta_auc_M1_minus_M0"], 0.0)

    def test_retrospective_period_gate_sanity(self):
        panel = retrospective_period_gate_panel()
        self.assertEqual(panel["M0_correct"], 2)
        self.assertEqual(panel["M1_correct"], 4)
        self.assertEqual(panel["count"], 4)
        self.assertEqual(panel["status"], "RETROSPECTIVE_SANITY_NOT_BLIND_VALIDATION")


if __name__ == "__main__":
    unittest.main()
