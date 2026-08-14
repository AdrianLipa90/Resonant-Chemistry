import unittest

from reschem.energetic_admission import (
    HARTREE_TO_KCAL_MOL,
    EnergyDatum,
    MethodPolicy,
    PairLossChannel,
    evaluate_pair_loss,
    score_boolean_model,
)


class EnergeticAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.policy = MethodPolicy("TEST_METHOD", "TEST_BASIS")
        self.channel = PairLossChannel("XF4", "XF2", "F2")

    def datum(self, formula, energy, **kw):
        return EnergyDatum(formula, energy, self.policy, **kw)

    def test_positive_pair_loss_admission(self):
        records = {
            "XF4": self.datum("XF4", -10.0),
            "XF2": self.datum("XF2", -7.0),
            "F2": self.datum("F2", -2.5),
        }
        result = evaluate_pair_loss(self.channel, records)
        self.assertEqual(result.status, "ADMITTED_BOUND_AGAINST_PAIR_LOSS")
        self.assertAlmostEqual(result.delta_e_hartree, 0.5)
        self.assertAlmostEqual(result.delta_e_kcal_mol, 0.5 * HARTREE_TO_KCAL_MOL)

    def test_negative_pair_loss_keeps_metastable_separate(self):
        records = {
            "XF4": self.datum("XF4", -8.0),
            "XF2": self.datum("XF2", -7.0),
            "F2": self.datum("F2", -1.5),
        }
        result = evaluate_pair_loss(self.channel, records)
        self.assertEqual(result.status, "METASTABLE_OR_UNBOUND_TO_PAIR_LOSS")
        self.assertLess(result.delta_e_hartree, 0.0)

    def test_imaginary_frequency_rejects_parent_local_minimum(self):
        records = {
            "XF4": self.datum("XF4", -10.0, imaginary_frequencies=1),
            "XF2": self.datum("XF2", -7.0),
            "F2": self.datum("F2", -2.5),
        }
        result = evaluate_pair_loss(self.channel, records)
        self.assertEqual(result.status, "REJECTED_PARENT_NO_LOCAL_MINIMUM")

    def test_missing_parent_hessian_stays_unknown(self):
        records = {
            "XF4": self.datum("XF4", -10.0, imaginary_frequencies=None),
            "XF2": self.datum("XF2", -7.0),
            "F2": self.datum("F2", -2.5),
        }
        result = evaluate_pair_loss(self.channel, records)
        self.assertEqual(result.status, "UNKNOWN_PARENT_HESSIAN_NOT_AVAILABLE")

    def test_missing_energy_stays_unknown(self):
        records = {
            "XF4": self.datum("XF4", -10.0),
            "XF2": self.datum("XF2", -7.0),
        }
        result = evaluate_pair_loss(self.channel, records)
        self.assertEqual(result.status, "UNKNOWN_MISSING_ENERGY_DATA")

    def test_policy_mismatch_is_incomparable(self):
        other = MethodPolicy("OTHER_METHOD", "TEST_BASIS")
        records = {
            "XF4": self.datum("XF4", -10.0),
            "XF2": self.datum("XF2", -7.0),
            "F2": EnergyDatum("F2", -2.5, other),
        }
        result = evaluate_pair_loss(self.channel, records)
        self.assertEqual(result.status, "INCOMPARABLE_METHOD_POLICY")

    def test_tolerance_gate(self):
        records = {
            "XF4": self.datum("XF4", -10.0),
            "XF2": self.datum("XF2", -7.0),
            "F2": self.datum("F2", -3.0 + 5e-7),
        }
        result = evaluate_pair_loss(self.channel, records, tolerance_hartree=1e-6)
        self.assertEqual(result.status, "ENERGETICALLY_DEGENERATE_WITHIN_TOLERANCE")

    def test_product_hessian_unknown_keeps_channel_unresolved(self):
        records = {
            "XF4": self.datum("XF4", -10.0),
            "XF2": self.datum("XF2", -7.0, imaginary_frequencies=None),
            "F2": self.datum("F2", -2.5),
        }
        result = evaluate_pair_loss(self.channel, records)
        self.assertEqual(result.status, "UNKNOWN_PRODUCT_HESSIAN_NOT_AVAILABLE")

    def test_product_not_minimum_invalidates_specific_channel(self):
        records = {
            "XF4": self.datum("XF4", -10.0),
            "XF2": self.datum("XF2", -7.0, imaginary_frequencies=1),
            "F2": self.datum("F2", -2.5),
        }
        result = evaluate_pair_loss(self.channel, records)
        self.assertEqual(
            result.status,
            "INVALID_PAIR_LOSS_CHANNEL_PRODUCT_NOT_LOCAL_MINIMUM",
        )

    def test_score_excludes_unknown(self):
        admissions = [
            evaluate_pair_loss(
                PairLossChannel("XF4", "XF2", "F2"),
                {
                    "XF4": self.datum("XF4", -10.0),
                    "XF2": self.datum("XF2", -7.0),
                    "F2": self.datum("F2", -2.5),
                },
            ),
            evaluate_pair_loss(
                PairLossChannel("YF4", "YF2", "F2"),
                {
                    "YF4": self.datum("YF4", -8.0),
                    "F2": self.datum("F2", -2.5),
                },
            ),
        ]
        score = score_boolean_model({"XF4": True, "YF4": False}, admissions)
        self.assertEqual(score["resolved_count"], 1)
        self.assertEqual(score["correct_count"], 1)
        self.assertEqual(len(score["unresolved"]), 1)

    def test_balanced_accuracy_requires_both_classes(self):
        pos = evaluate_pair_loss(
            PairLossChannel("XF4", "XF2", "F2"),
            {
                "XF4": self.datum("XF4", -10.0),
                "XF2": self.datum("XF2", -7.0),
                "F2": self.datum("F2", -2.5),
            },
        )
        neg = evaluate_pair_loss(
            PairLossChannel("YF4", "YF2", "F2"),
            {
                "YF4": self.datum("YF4", -8.0),
                "YF2": self.datum("YF2", -7.0),
                "F2": self.datum("F2", -1.5),
            },
        )
        score = score_boolean_model({"XF4": True, "YF4": False}, [pos, neg])
        self.assertEqual(score["balanced_accuracy"], 1.0)


if __name__ == "__main__":
    unittest.main()
