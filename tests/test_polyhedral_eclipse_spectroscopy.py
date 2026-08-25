import math
import unittest

import numpy as np

from reschem.polyhedral_eclipse_spectroscopy import (
    KAPPA_INFORMATION,
    PolyhedralConePartition,
    blind_transition_prediction,
    build_orbital_eclipse_probe,
    cone_probabilities,
    dominant_harmonic,
    eclipse_frequency_hz,
    eclipse_phase_trace,
    fibonacci_sphere,
    m_state_coefficients,
    orbital_angular_density,
    polyhedral_information_nats,
    regular_polyhedral_axes,
    semantic_mass_from_card,
)


class PolyhedralEclipseSpectroscopyTests(unittest.TestCase):
    def test_regular_polyhedral_axes_are_unit_and_balanced(self):
        for kind, count in (("tetrahedron", 4), ("octahedron", 6), ("cube", 8), ("icosahedron", 12)):
            axes = regular_polyhedral_axes(kind)
            self.assertEqual(axes.shape, (count, 3))
            self.assertTrue(np.allclose(np.linalg.norm(axes, axis=1), 1.0, atol=1.0e-12))
            self.assertTrue(np.allclose(np.sum(axes, axis=0), 0.0, atol=1.0e-12))

    def test_s_orbital_matches_polyhedral_solid_angle_baseline(self):
        partition = PolyhedralConePartition.regular("octahedron")
        directions = fibonacci_sphere(4096)
        density = orbital_angular_density(0, m_state_coefficients(0, 0), directions)
        probs = cone_probabilities(partition, directions, density)
        reference = partition.solid_angle_fractions(4096)
        self.assertTrue(np.allclose(probs, reference, atol=1.0e-12))
        self.assertAlmostEqual(polyhedral_information_nats(probs, reference), 0.0, places=12)

    def test_pz_has_nonzero_polyhedral_information(self):
        partition = PolyhedralConePartition.regular("octahedron")
        directions = fibonacci_sphere(8192)
        density = orbital_angular_density(1, m_state_coefficients(1, 0), directions)
        probs = cone_probabilities(partition, directions, density)
        reference = partition.solid_angle_fractions(8192)
        info = polyhedral_information_nats(probs, reference)
        self.assertGreater(info, 0.05)
        self.assertGreater(probs[4], reference[4])
        self.assertGreater(probs[5], reference[5])

    def test_real_px_rotation_has_second_harmonic(self):
        partition = PolyhedralConePartition.regular("octahedron")
        coefficients = np.asarray([1.0 / math.sqrt(2.0), 0.0, -1.0 / math.sqrt(2.0)], dtype=complex)
        trace = eclipse_phase_trace(
            partition,
            1,
            coefficients,
            rotation_axis=(0.0, 0.0, 1.0),
            observer_direction=(1.0, 0.0, 0.0),
            sample_count=4096,
            phase_samples=96,
        )
        order, strength = dominant_harmonic(trace)
        self.assertEqual(order, 2)
        self.assertGreater(strength, 0.05)

    def test_kappa_is_canonical_ln2_over_24pi(self):
        self.assertAlmostEqual(KAPPA_INFORMATION, math.log(2.0) / (24.0 * math.pi), places=15)

    def test_semantic_mass_binding_is_fail_closed_and_provenance_bound(self):
        unresolved = {"tir": {"semantic_axes": {"values": {}}}}
        with self.assertRaises(ValueError):
            semantic_mass_from_card(unresolved)

        resolved = {
            "tir": {
                "semantic_axes": {
                    "values": {
                        "semantic_mass": {
                            "value": 3.5,
                            "provenance": "benchmarks/SEMANTIC_MASS_BINDING_V0_15.json",
                        }
                    }
                }
            }
        }
        value, provenance = semantic_mass_from_card(resolved)
        self.assertEqual(value, 3.5)
        self.assertEqual(provenance, "benchmarks/SEMANTIC_MASS_BINDING_V0_15.json")

    def test_probe_tracks_per_nucleon_scaling_and_blind_status(self):
        partition = PolyhedralConePartition.regular("octahedron")
        coefficients = m_state_coefficients(1, 0)
        common = dict(
            partition=partition,
            l=1,
            coefficients=coefficients,
            semantic_mass=12.0,
            semantic_mass_provenance="unit-test-binding",
            radial_nuclear_exposure=7.0,
            sample_count=2048,
            phase_samples=48,
        )
        a12 = build_orbital_eclipse_probe(nucleon_count=12, **common)
        a24 = build_orbital_eclipse_probe(nucleon_count=24, **common)
        self.assertAlmostEqual(a12.semantic_mass_per_nucleon, 2.0 * a24.semantic_mass_per_nucleon)
        self.assertAlmostEqual(
            a12.orbital_information_ratio_to_nucleons,
            2.0 * a24.orbital_information_ratio_to_nucleons,
            places=10,
        )
        self.assertAlmostEqual(a12.eclipse_coupling, 4.0 * a24.eclipse_coupling, places=10)
        payload = a12.as_dict()
        self.assertEqual(payload["epistemic_status"]["spectral_validation"], "BLIND_COMPARISON_PENDING")
        self.assertEqual(payload["phase"]["frequency_mapping_status"], "REQUIRES_INDEPENDENT_PHASE_RATE")

    def test_phase_rate_to_frequency_is_explicit(self):
        rate = 2.0 * math.pi * 100.0
        self.assertAlmostEqual(eclipse_frequency_hz(rate, 2), 200.0)

    def test_blind_transition_keeps_observed_spectrum_withheld(self):
        partition = PolyhedralConePartition.regular("octahedron")
        pz = build_orbital_eclipse_probe(
            partition=partition,
            l=1,
            coefficients=m_state_coefficients(1, 0),
            nucleon_count=12,
            semantic_mass=2.0,
            semantic_mass_provenance="unit-test-binding",
            radial_nuclear_exposure=5.0,
            sample_count=2048,
            phase_samples=48,
        )
        px_coefficients = np.asarray([1.0 / math.sqrt(2.0), 0.0, -1.0 / math.sqrt(2.0)], dtype=complex)
        px = build_orbital_eclipse_probe(
            partition=partition,
            l=1,
            coefficients=px_coefficients,
            nucleon_count=12,
            semantic_mass=2.0,
            semantic_mass_provenance="unit-test-binding",
            radial_nuclear_exposure=5.0,
            sample_count=2048,
            phase_samples=48,
        )
        record = blind_transition_prediction("2p_z", pz, "2p_x", px)
        self.assertEqual(record["observed_spectrum"], "WITHHELD_FOR_BLIND_COMPARISON")
        self.assertEqual(record["validation_status"], "PREDICTION_FEATURES_FROZEN")


if __name__ == "__main__":
    unittest.main()
