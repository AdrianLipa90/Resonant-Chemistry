import unittest
from types import SimpleNamespace

from reschem.atomic_ion_convergence_continuation import L3, run_l3_state


def fake_solver(z, charge, **kwargs):
    return SimpleNamespace(
        configuration=f"Z{z} q{charge}",
        energy_hartree=-float(z * z) - 0.1 * charge,
        converged=True,
        iterations=23,
        virial_residual_hartree=0.0123,
        basis_size=kwargs["basis_size"],
        grid_points=kwargs["grid_points"],
    )


class AtomicIonConvergenceContinuationTests(unittest.TestCase):
    def test_l3_matches_preregistered_continuation(self):
        self.assertEqual(L3.name, "L3")
        self.assertEqual(L3.basis_size, 32)
        self.assertEqual(L3.grid_points, 2200)
        self.assertEqual(L3.zeta_min, 0.0025)
        self.assertEqual(L3.radial_grid_max_bohr, 300.0)
        self.assertEqual(L3.max_iterations, 1500)

    def test_run_preserves_raw_result_without_threshold(self):
        out = run_l3_state(35, -1, solver=fake_solver)
        self.assertEqual(out["level"], "L3")
        self.assertTrue(out["converged"])
        self.assertAlmostEqual(out["virial_abs_hartree"], 0.0123)
        self.assertIn("NO_CONVERGENCE_THRESHOLD", out["status"])
        self.assertNotIn("quality_pass", out)
        self.assertNotIn("convergence_pass", out)

    def test_same_l3_parameters_apply_to_neutral_and_anion(self):
        a = run_l3_state(9, 0, solver=fake_solver)
        b = run_l3_state(9, -1, solver=fake_solver)
        self.assertEqual(a["parameters"], b["parameters"])


if __name__ == "__main__":
    unittest.main()
