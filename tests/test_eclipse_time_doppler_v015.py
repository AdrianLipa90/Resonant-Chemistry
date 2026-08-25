import math
import unittest

from reschem.eclipse_time_doppler_v015 import (
    C_M_PER_S,
    CONTRACT_ID,
    coordinate_frequency_hz,
    longitudinal_doppler_factor,
    proper_eclipse_frequency_hz,
    transform_eclipse_observation,
)


class EclipseTimeDopplerV015Tests(unittest.TestCase):
    def test_identity_transform(self):
        out = transform_eclipse_observation(
            harmonic_order=2,
            omega_proper_rad_s=2.0 * math.pi,
            subjective_time_scale=1.0,
            beta_radial=0.0,
        )
        self.assertAlmostEqual(out.proper_frequency_hz, 2.0)
        self.assertAlmostEqual(out.coordinate_frequency_hz, 2.0)
        self.assertAlmostEqual(out.doppler_factor, 1.0)
        self.assertAlmostEqual(out.observed_frequency_hz, 2.0)
        self.assertAlmostEqual(out.observed_wavelength_m, C_M_PER_S / 2.0)
        self.assertEqual(out.payload["schema"], CONTRACT_ID)
        self.assertEqual(out.payload["observed_spectrum_input"], "WITHHELD")

    def test_subjective_time_scale_multiplies_coordinate_frequency(self):
        self.assertAlmostEqual(coordinate_frequency_hz(8.0, 0.25), 2.0)
        self.assertAlmostEqual(coordinate_frequency_hz(8.0, 2.0), 16.0)

    def test_receding_relativistic_doppler_redshifts(self):
        factor = longitudinal_doppler_factor(0.6)
        self.assertAlmostEqual(factor, 0.5)
        out = transform_eclipse_observation(
            harmonic_order=1,
            omega_proper_rad_s=2.0 * math.pi,
            subjective_time_scale=1.0,
            beta_radial=0.6,
        )
        self.assertAlmostEqual(out.observed_frequency_hz, 0.5)
        self.assertAlmostEqual(out.observed_wavelength_m, 2.0 * C_M_PER_S)

    def test_approaching_relativistic_doppler_blueshifts(self):
        factor = longitudinal_doppler_factor(-0.6)
        self.assertAlmostEqual(factor, 2.0)
        out = transform_eclipse_observation(
            harmonic_order=1,
            omega_proper_rad_s=2.0 * math.pi,
            subjective_time_scale=1.0,
            beta_radial=-0.6,
        )
        self.assertAlmostEqual(out.observed_frequency_hz, 2.0)
        self.assertAlmostEqual(out.observed_wavelength_m, C_M_PER_S / 2.0)

    def test_doppler_reciprocity(self):
        for beta in (0.1, 0.25, 0.6, 0.9):
            self.assertAlmostEqual(
                longitudinal_doppler_factor(beta) * longitudinal_doppler_factor(-beta),
                1.0,
                places=12,
            )

    def test_zero_harmonic_is_static_and_has_no_wavelength(self):
        out = transform_eclipse_observation(
            harmonic_order=0,
            omega_proper_rad_s=123.0,
            subjective_time_scale=0.5,
            beta_radial=-0.2,
        )
        self.assertEqual(out.observed_frequency_hz, 0.0)
        self.assertIsNone(out.observed_wavelength_m)
        self.assertEqual(out.status, "STATIC_ZERO_FREQUENCY")

    def test_proper_frequency_formula(self):
        self.assertAlmostEqual(proper_eclipse_frequency_hz(2, 5.0 * math.pi), 5.0)

    def test_invalid_beta_fails_closed(self):
        for beta in (-1.0, 1.0, 2.0, float("inf")):
            with self.assertRaises(ValueError):
                longitudinal_doppler_factor(beta)

    def test_invalid_subjective_scale_fails_closed(self):
        for scale in (0.0, -0.1, float("nan")):
            with self.assertRaises(ValueError):
                coordinate_frequency_hz(1.0, scale)

    def test_invalid_harmonic_or_phase_rate_fails_closed(self):
        with self.assertRaises(ValueError):
            proper_eclipse_frequency_hz(-1, 1.0)
        with self.assertRaises(ValueError):
            proper_eclipse_frequency_hz(1, -1.0)
        with self.assertRaises(ValueError):
            proper_eclipse_frequency_hz(True, 1.0)

    def test_transform_order_is_receipt_bound(self):
        out = transform_eclipse_observation(
            harmonic_order=2,
            omega_proper_rad_s=4.0 * math.pi,
            subjective_time_scale=0.5,
            beta_radial=0.6,
        )
        self.assertAlmostEqual(out.proper_frequency_hz, 4.0)
        self.assertAlmostEqual(out.coordinate_frequency_hz, 2.0)
        self.assertAlmostEqual(out.observed_frequency_hz, 1.0)
        self.assertEqual(
            out.payload["transform_order"],
            [
                "harmonic_and_proper_phase_rate",
                "subjective_time_scale",
                "longitudinal_relativistic_doppler",
                "observer_frequency_and_wavelength",
            ],
        )


if __name__ == "__main__":
    unittest.main()
