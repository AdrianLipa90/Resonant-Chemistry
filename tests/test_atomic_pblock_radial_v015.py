import math
import unittest

import numpy as np

from reschem.atomic_kepler_phase_v015 import radial_kepler_observables
from reschem.atomic_pblock_radial_v015 import (
    AtomicPBlockRadialV015Error,
    pblock_radial_control_exposure,
    solve_neutral_pblock_radial_state,
)
from reschem.atomic_radial_spectroscopy import _solve_period2_radial_state


class AtomicPBlockRadialV015Tests(unittest.TestCase):
    COMMON = dict(
        basis_size=16,
        grid_points=700,
        mixing=0.32,
        tolerance_hartree=2.0e-7,
        max_iterations=120,
    )

    def _assert_period2_parity(self, z: int) -> None:
        legacy = _solve_period2_radial_state(z, **self.COMMON)
        generic = solve_neutral_pblock_radial_state(z, "2p", **self.COMMON)
        self.assertEqual(generic["active_p_shell"], "2p")
        self.assertEqual(generic["p_electron_count"], legacy["p_electron_count"])
        self.assertEqual(generic["iterations"], legacy["iterations"])
        self.assertAlmostEqual(generic["energy_hartree"], legacy["energy_hartree"], places=12)
        self.assertAlmostEqual(
            generic["virial_residual_hartree"], legacy["virial_residual_hartree"], places=12
        )
        np.testing.assert_allclose(generic["r"], legacy["r"], rtol=0.0, atol=0.0)
        np.testing.assert_allclose(generic["weights"], legacy["weights"], rtol=0.0, atol=0.0)
        np.testing.assert_allclose(generic["density"], legacy["density"], rtol=1e-12, atol=1e-13)
        np.testing.assert_allclose(
            generic["one_p_density"], legacy["one_p_density"], rtol=1e-12, atol=1e-13
        )

    def test_boron_replays_legacy_period2_solver(self):
        self._assert_period2_parity(5)

    def test_neon_replays_legacy_period2_solver(self):
        self._assert_period2_parity(10)

    def test_aluminium_3p_state_converges_and_normalizes(self):
        state = solve_neutral_pblock_radial_state(13, "3p", **self.COMMON)
        normalization = float(np.sum(state["weights"] * state["one_p_density"]))
        self.assertAlmostEqual(normalization, 1.0, places=10)
        self.assertTrue(np.all(np.isfinite(state["density"])))
        self.assertTrue(np.all(state["density"] >= -1e-12))
        obs = radial_kepler_observables(
            13,
            r=state["r"],
            weights=state["weights"],
            total_radial_density=state["density"],
            one_p_density=state["one_p_density"],
        )
        self.assertGreater(obs["effective_charge_at_mean_radius"], 0.0)
        self.assertGreater(obs["kepler_wavenumber_cm_inverse"], 0.0)

    def test_argon_3p_state_converges_and_normalizes(self):
        state = solve_neutral_pblock_radial_state(18, "3p", **self.COMMON)
        normalization = float(np.sum(state["weights"] * state["one_p_density"]))
        self.assertAlmostEqual(normalization, 1.0, places=10)
        self.assertTrue(np.all(np.isfinite(state["density"])))
        obs = radial_kepler_observables(
            18,
            r=state["r"],
            weights=state["weights"],
            total_radial_density=state["density"],
            one_p_density=state["one_p_density"],
        )
        self.assertGreater(obs["effective_charge_at_mean_radius"], 0.0)

    def test_exposure_uses_same_pauli_central_field_definition(self):
        control = pblock_radial_control_exposure(13, "3p", **self.COMMON)
        self.assertGreater(control["radial_nuclear_exposure"], 0.0)
        self.assertGreater(control["zeta_p_hartree"], 0.0)
        self.assertEqual(control["spectral_input"], "NONE")
        self.assertEqual(control["fit_parameters"], [])
        self.assertEqual(control["calibration_parameters"], [])
        self.assertFalse(control["canon_allowed"])

    def test_invalid_or_absent_active_shell_fails_closed(self):
        with self.assertRaises(AtomicPBlockRadialV015Error):
            solve_neutral_pblock_radial_state(13, "2p", **self.COMMON)
        with self.assertRaises(AtomicPBlockRadialV015Error):
            solve_neutral_pblock_radial_state(13, "3d", **self.COMMON)
        with self.assertRaises(AtomicPBlockRadialV015Error):
            solve_neutral_pblock_radial_state(12, "3p", **self.COMMON)


if __name__ == "__main__":
    unittest.main()
