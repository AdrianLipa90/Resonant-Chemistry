import unittest

from reschem.atomic_hf_diis import (
    _GLOBAL_STAGES,
    solve_atom_average_hf_diis,
    solve_atom_average_hf_robust,
)


class AtomicHFDIISTests(unittest.TestCase):
    def test_na_to_ar_all_converge_without_element_specific_parameters(self):
        for z in range(11, 19):
            result = solve_atom_average_hf_diis(
                z,
                basis_size=15,
                grid_points=600,
                damping=0.25,
                diis_start=3,
                diis_size=7,
                max_iterations=220,
                tolerance_hartree=1e-7,
            )
            self.assertTrue(result.converged, f"Z={z}")
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
