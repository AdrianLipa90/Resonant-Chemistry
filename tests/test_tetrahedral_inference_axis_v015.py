import unittest

from reschem.tetrahedral_inference_axis_v015 import (
    AXIS_RESOLVED_PHASE_CONTRACT_ID,
    axis_resolved_tetrahedral_harmonics,
)


class TetrahedralInferenceAxisV015Tests(unittest.TestCase):
    def test_z_aligned_bloch_state_resolves_transverse_and_collinear_axes(self):
        payload = axis_resolved_tetrahedral_harmonics((0.0, 0.0, 1.0), phase_samples=96)
        self.assertEqual(payload["schema"], AXIS_RESOLVED_PHASE_CONTRACT_ID)
        self.assertEqual(payload["axes"]["x"]["dominant_harmonic_order"], 1)
        self.assertEqual(payload["axes"]["y"]["dominant_harmonic_order"], 1)
        self.assertEqual(payload["axes"]["z"]["dominant_harmonic_order"], 0)
        self.assertGreater(payload["axes"]["x"]["dominant_harmonic_strength"], 0.05)
        self.assertGreater(payload["axes"]["y"]["dominant_harmonic_strength"], 0.05)
        self.assertEqual(payload["axes"]["z"]["dominant_harmonic_strength"], 0.0)

    def test_mixed_central_bloch_coordinate_has_zero_phase_harmonics(self):
        payload = axis_resolved_tetrahedral_harmonics((0.0, 0.0, 0.0), phase_samples=96)
        for row in payload["axes"].values():
            self.assertEqual(row["dominant_harmonic_order"], 0)
            self.assertEqual(row["dominant_harmonic_strength"], 0.0)

    def test_axis_selection_remains_unselected_before_spectral_join(self):
        payload = axis_resolved_tetrahedral_harmonics((0.0, 0.0, 0.5), phase_samples=96)
        self.assertEqual(payload["selection_status"], "ALL_PREREGISTERED_AXES_PRESERVED")
        self.assertEqual(payload["spectral_join"], "WITHHELD_FOR_BLIND_COMPARISON")


if __name__ == "__main__":
    unittest.main()
