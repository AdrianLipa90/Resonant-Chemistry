import unittest

from reschem.atomic_hf_diis import (
    _GLOBAL_STAGES,
    solve_atom_average_hf_diis,
    solve_atom_average_hf_robust,
)


class AtomicHFDIISTests(unittest.TestCase):
    def test_na_to_ar_all_pass_global_non_element_specific_quality_ladder(self):
        """Current release gate: one global fallback policy, no element branches.

        The historical single-stage Na-Ar checkpoint is retained in its frozen
        benchmark, but current CI uses the later robust ladder because numerical
        library updates can move a marginal fixed-point iteration across the
        convergence threshold without changing the physical operator.
        """
        for z in range(11, 19):
            robust = solve_atom_average_hf_robust(
                z,
                virial_gate_hartree=2.0,
                tolerance_hartree=1e-6,
            )
            result = robust.result
            self.assertTrue(robust.quality_pass, f"Z={z}, stage={robust.stage}")
            self.assertTrue(result.converged, f"Z={z}, stage={robust.stage}")
            self.assertTrue(result.energy_hartree < 0.0)
            self.assertEqual(result.electron_count, z)

    def test_argon_is_closed_shell_singlet(self):
        result = solve_atom_average_hf_diis(
            18,
            basis_size=15,
            grid_points=600,
            tolerance_hartree=1e-7,
        )
        self.assertTrue(result.converged)
        self.assertAlmostEqual(result.target_s, 0.0, places=12)
        self.assertAlmostEqual(result.target_s2, 0.0, places=12)
        self.assertIn("3p^6", result.configuration)

    def test_global_fallback_contains_no_element_identity(self):
        self.assertGreaterEqual(len(_GLOBAL_STAGES), 3)
        for stage in _GLOBAL_STAGES:
            self.assertNotIn("z", stage)
            self.assertNotIn("element", stage)
            self.assertIn("basis_size", stage)
            self.assertIn("grid_points", stage)

    def test_robust_quality_gate_requires_virial_and_convergence(self):
        result = solve_atom_average_hf_robust(19, virial_gate_hartree=2.0)
        self.assertTrue(result.quality_pass)
        self.assertTrue(result.result.converged)
        self.assertLess(abs(result.result.virial_residual_hartree), 2.0)


if __name__ == "__main__":
    unittest.main()
