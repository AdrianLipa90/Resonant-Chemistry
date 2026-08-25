import math
import unittest

import numpy as np

from reschem.tetrahedral_inference_v015 import (
    TIR_REFERENCE_COMMIT,
    TETRAHEDRAL_SIC_CONTRACT_ID,
    build_tetrahedral_inference_probe,
    period2_p_spin_bloch_control,
    sic_information_nats,
    tetrahedral_gram_matrix,
    tetrahedral_phase_trace,
    tetrahedral_sic_probabilities,
    tetrahedral_vertices,
)


class TetrahedralInferenceV015Tests(unittest.TestCase):
    def test_tetrahedral_frame_matches_tir_dot_products(self):
        vertices = tetrahedral_vertices()
        dots = vertices @ vertices.T
        self.assertTrue(np.allclose(np.diag(dots), 1.0, atol=1.0e-12))
        off = dots[~np.eye(4, dtype=bool)]
        self.assertTrue(np.allclose(off, -1.0 / 3.0, atol=1.0e-12))

    def test_tir_gram_matrix_is_one_and_one_third(self):
        gram = tetrahedral_gram_matrix()
        self.assertTrue(np.allclose(np.diag(gram), 1.0, atol=1.0e-12))
        off = gram[~np.eye(4, dtype=bool)]
        self.assertTrue(np.allclose(off, 1.0 / 3.0, atol=1.0e-12))

    def test_sic_map_at_vertex_has_half_and_sixths(self):
        vertex = tetrahedral_vertices()[0]
        probs = tetrahedral_sic_probabilities(vertex)
        self.assertAlmostEqual(probs[0], 0.5, places=12)
        for value in probs[1:]:
            self.assertAlmostEqual(value, 1.0 / 6.0, places=12)
        self.assertAlmostEqual(float(np.sum(probs)), 1.0, places=12)

    def test_sic_map_at_antipode_has_zero_and_thirds(self):
        vertex = tetrahedral_vertices()[0]
        probs = tetrahedral_sic_probabilities(-vertex)
        self.assertAlmostEqual(probs[0], 0.0, places=12)
        for value in probs[1:]:
            self.assertAlmostEqual(value, 1.0 / 3.0, places=12)

    def test_maximally_mixed_bloch_coordinate_is_uniform(self):
        probs = tetrahedral_sic_probabilities((0.0, 0.0, 0.0))
        self.assertTrue(np.allclose(probs, 0.25, atol=1.0e-12))
        self.assertAlmostEqual(sic_information_nats(probs), 0.0, places=12)

    def test_period2_spin_reduction_tracks_half_filling_to_closed_shell(self):
        nitrogen = period2_p_spin_bloch_control(7)
        oxygen = period2_p_spin_bloch_control(8)
        fluorine = period2_p_spin_bloch_control(9)
        neon = period2_p_spin_bloch_control(10)
        self.assertEqual(nitrogen["alpha_occupancy"], 3)
        self.assertEqual(nitrogen["beta_occupancy"], 0)
        self.assertAlmostEqual(nitrogen["spin_polarization"], 1.0)
        self.assertAlmostEqual(oxygen["spin_polarization"], 0.5)
        self.assertAlmostEqual(fluorine["spin_polarization"], 0.2)
        self.assertAlmostEqual(neon["spin_polarization"], 0.0)

    def test_tetrahedral_phase_trace_is_periodic_and_finite(self):
        trace = tetrahedral_phase_trace((1.0, 0.0, 0.0), phase_samples=64)
        self.assertEqual(trace.shape, (64,))
        self.assertTrue(np.all(np.isfinite(trace)))
        self.assertGreater(float(np.max(trace) - np.min(trace)), 0.1)

    def test_probe_retains_tir_reference_and_blind_status(self):
        probe = build_tetrahedral_inference_probe((0.0, 0.0, 1.0), phase_samples=64).as_dict()
        self.assertEqual(probe["schema"], TETRAHEDRAL_SIC_CONTRACT_ID)
        self.assertEqual(probe["tir_reference"]["commit"], TIR_REFERENCE_COMMIT)
        self.assertEqual(probe["epistemic_status"]["tetrahedral_frame"], "TIR_MODEL_AXIOM_REFERENCE_BOUND")
        self.assertEqual(probe["epistemic_status"]["spectral_validation"], "BLIND_COMPARISON_PENDING")


if __name__ == "__main__":
    unittest.main()
