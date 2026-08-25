import math
import unittest

from reschem.atomic_subjective_time_v015 import (
    KAPPA,
    LAPSE_MAX,
    LAPSE_MIN,
    AtomicSubjectiveTimeV015Error,
    atomic_subjective_time_candidates,
    candidate_policy_ids,
    hydrodynamic_lapse,
)


class AtomicSubjectiveTimeV015Tests(unittest.TestCase):
    def test_hydrodynamic_lapse_matches_frozen_pncs_expression(self):
        raw, clipped = hydrodynamic_lapse(4.0, 1.0)
        self.assertEqual(raw, 1.0)
        self.assertEqual(clipped, 1.0)

    def test_candidate_set_and_order_are_frozen(self):
        candidates = atomic_subjective_time_candidates(
            symbol="C",
            z=6,
            radial_nuclear_exposure=6.522898358940513,
            semantic_mass=0.09930546,
        )
        self.assertEqual(
            candidate_policy_ids(candidates),
            (
                "NULL_REST_CONTROL",
                "KAPPA_RADIAL_BALANCED",
                "SEMANTIC_MASS_BALANCED",
                "RADIAL_SEMANTIC_GEOMETRIC_COUPLING",
                "RADIAL_SEMANTIC_PRODUCT_COUPLING",
            ),
        )

    def test_dimensionless_coordinates_are_exactly_preregistered(self):
        exposure = 6.522898358940513
        mass = 0.09930546
        candidates = atomic_subjective_time_candidates(
            symbol="C", z=6, radial_nuclear_exposure=exposure, semantic_mass=mass
        )
        for c in candidates:
            self.assertAlmostEqual(c.x_kappa_exposure, KAPPA * exposure, places=15)
            self.assertAlmostEqual(c.y_mass_over_kappa, mass / KAPPA, places=12)

    def test_null_control_is_exactly_one(self):
        null = atomic_subjective_time_candidates(
            symbol="B", z=5, radial_nuclear_exposure=1.6951648879909589, semantic_mass=0.0864968422
        )[0]
        self.assertEqual(null.density, 1.0)
        self.assertEqual(null.effective_viscosity, 0.0)
        self.assertEqual(null.lapse_unclamped, 1.0)
        self.assertEqual(null.lapse, 1.0)

    def test_radial_balanced_closed_form(self):
        exposure = 16.601323277918958
        c = atomic_subjective_time_candidates(
            symbol="N", z=7, radial_nuclear_exposure=exposure, semantic_mass=0.1096379195
        )[1]
        x = KAPPA * exposure
        self.assertAlmostEqual(c.lapse_unclamped, 1.0 / math.sqrt(1.0 + x), places=15)

    def test_geometric_coupling_closed_form(self):
        exposure = 30.21474302486471
        mass = 0.1250368608
        c = atomic_subjective_time_candidates(
            symbol="O", z=8, radial_nuclear_exposure=exposure, semantic_mass=mass
        )[3]
        x = KAPPA * exposure
        y = mass / KAPPA
        expected = math.sqrt(1.0 + x) / (1.0 + math.sqrt(x * y))
        self.assertAlmostEqual(c.lapse_unclamped, expected, places=15)

    def test_payload_forbids_observed_input_and_fit(self):
        c = atomic_subjective_time_candidates(
            symbol="F", z=9, radial_nuclear_exposure=53.0168743677017, semantic_mass=0.14
        )[3].as_dict()
        self.assertEqual(c["fit_parameters"], [])
        self.assertEqual(c["calibration_parameters"], [])
        self.assertFalse(c["stage_c_result_used_as_input"])
        self.assertFalse(c["nist_values_used_as_input"])
        self.assertFalse(c["canon_allowed"])
        self.assertGreaterEqual(c["lapse"], LAPSE_MIN)
        self.assertLessEqual(c["lapse"], LAPSE_MAX)
        self.assertIn("candidate_sha256", c)

    def test_invalid_inputs_fail_closed(self):
        with self.assertRaises(AtomicSubjectiveTimeV015Error):
            atomic_subjective_time_candidates(
                symbol="", z=6, radial_nuclear_exposure=1.0, semantic_mass=0.1
            )
        with self.assertRaises(AtomicSubjectiveTimeV015Error):
            atomic_subjective_time_candidates(
                symbol="C", z=0, radial_nuclear_exposure=1.0, semantic_mass=0.1
            )
        with self.assertRaises(AtomicSubjectiveTimeV015Error):
            atomic_subjective_time_candidates(
                symbol="C", z=6, radial_nuclear_exposure=0.0, semantic_mass=0.1
            )
        with self.assertRaises(AtomicSubjectiveTimeV015Error):
            atomic_subjective_time_candidates(
                symbol="C", z=6, radial_nuclear_exposure=1.0, semantic_mass=0.0
            )


if __name__ == "__main__":
    unittest.main()
