import json
import math
import unittest

import numpy as np

from reschem.atomic_hf_average import _trap_weights
from reschem.atomic_kepler_phase_v015 import (
    ATOMIC_TIME_SECOND,
    SPEED_OF_LIGHT_CM_PER_SECOND,
    Period2KeplerPhaseRate,
    harmonic_frequency_candidate,
    radial_kepler_observables,
)


class AtomicKeplerPhaseV015Tests(unittest.TestCase):
    def test_radial_kepler_observables_follow_frozen_formula(self):
        r = np.linspace(0.1, 4.0, 128)
        weights = _trap_weights(r)
        one_p = np.exp(-r)
        one_p /= float(np.sum(weights * one_p))
        other = 2.0 * np.exp(-2.0 * r)
        total = one_p + other
        result = radial_kepler_observables(
            5,
            r=r,
            weights=weights,
            total_radial_density=total,
            one_p_density=one_p,
        )
        r_bar = float(np.sum(weights * one_p * r))
        self.assertAlmostEqual(result["mean_radius_bohr"], r_bar, places=14)
        z_eff = result["effective_charge_at_mean_radius"]
        expected_omega_au = math.sqrt(z_eff / r_bar**3)
        self.assertAlmostEqual(result["kepler_angular_rate_atomic_units"], expected_omega_au, places=14)
        self.assertAlmostEqual(
            result["kepler_angular_rate_rad_per_second"], expected_omega_au / ATOMIC_TIME_SECOND, places=3
        )
        self.assertAlmostEqual(
            result["kepler_frequency_hz"],
            result["kepler_angular_rate_rad_per_second"] / (2.0 * math.pi),
            places=3,
        )
        self.assertAlmostEqual(
            result["kepler_wavenumber_cm_inverse"],
            result["kepler_frequency_hz"] / SPEED_OF_LIGHT_CM_PER_SECOND,
            places=8,
        )

    def test_harmonic_frequency_candidate_scales_frozen_phase_rate_only_by_integer_order(self):
        phase = Period2KeplerPhaseRate(
            z=5,
            mean_radius_bohr=1.0,
            enclosed_other_charge_at_mean_radius=1.0,
            effective_charge_at_mean_radius=4.0,
            kepler_angular_rate_atomic_units=2.0,
            kepler_angular_rate_rad_per_second=20.0,
            kepler_frequency_hz=10.0,
            kepler_wavenumber_cm_inverse=5.0,
            zeta_2p_hartree=0.01,
            zeta_2p_control_wavenumber_cm_inverse=2.0,
            hf_energy_hartree=-10.0,
            virial_residual_hartree=1.0e-8,
            scf_iterations=20,
        )
        self.assertEqual(harmonic_frequency_candidate(phase, 0), {"harmonic_order": 0, "frequency_hz": 0.0, "wavenumber_cm_inverse": 0.0})
        self.assertEqual(harmonic_frequency_candidate(phase, 2), {"harmonic_order": 2, "frequency_hz": 20.0, "wavenumber_cm_inverse": 10.0})

    def test_phase_record_carries_zero_fit_and_blind_boundaries(self):
        phase = Period2KeplerPhaseRate(
            z=6,
            mean_radius_bohr=1.2,
            enclosed_other_charge_at_mean_radius=2.0,
            effective_charge_at_mean_radius=4.0,
            kepler_angular_rate_atomic_units=1.5,
            kepler_angular_rate_rad_per_second=1.5 / ATOMIC_TIME_SECOND,
            kepler_frequency_hz=1.5 / ATOMIC_TIME_SECOND / (2.0 * math.pi),
            kepler_wavenumber_cm_inverse=1.5 / ATOMIC_TIME_SECOND / (2.0 * math.pi) / SPEED_OF_LIGHT_CM_PER_SECOND,
            zeta_2p_hartree=0.02,
            zeta_2p_control_wavenumber_cm_inverse=4.0,
            hf_energy_hartree=-20.0,
            virial_residual_hartree=2.0e-8,
            scf_iterations=22,
        )
        payload = phase.as_dict()
        self.assertEqual(payload["fit_parameters"], [])
        self.assertEqual(payload["observed_spectrum"], "WITHHELD_FOR_BLIND_COMPARISON")
        self.assertEqual(payload["epistemic_operator"], "CHYBA")
        self.assertFalse(payload["canon_allowed"])
        text = json.dumps(payload).lower()
        for forbidden in ("observed_wavelength", "observed_wavenumber", "oscillator_strength", "line_intensity"):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
