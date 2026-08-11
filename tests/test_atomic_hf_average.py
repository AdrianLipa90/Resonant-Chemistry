import unittest

from reschem.atomic_hf_average import solve_atom_average_hf, solve_h_to_ne_blind, subshells_for_atom


class AtomicAverageHFTests(unittest.TestCase):
    def test_hydrogen_self_interaction_cancels(self):
        result = solve_atom_average_hf(1, basis_size=16, grid_points=800, tolerance_hartree=1e-6)
        self.assertTrue(result.converged)
        self.assertLess(abs(result.energy_hartree + 0.5), 2e-5)
        self.assertLess(abs(result.direct_hartree + result.exchange_hartree), 2e-5)

    def test_boron_activates_p_channel_from_atom_configuration(self):
        shells = subshells_for_atom(5)
        p_shell = [shell for shell in shells if shell.label == "2p"][0]
        self.assertEqual(p_shell.l, 1)
        self.assertEqual(p_shell.alpha_occupancy, 1)
        result = solve_atom_average_hf(5, basis_size=16, grid_points=800, tolerance_hartree=2e-6)
        self.assertTrue(result.converged)
        self.assertIn("2p^1", result.configuration)

    def test_neon_is_closed_shell_singlet_control(self):
        result = solve_atom_average_hf(10, basis_size=16, grid_points=800, tolerance_hartree=2e-6)
        self.assertTrue(result.converged)
        self.assertEqual(result.electron_count, 10)
        self.assertAlmostEqual(result.target_s2, 0.0, places=12)

    def test_first_multi_l_batch_h_to_ne_converges(self):
        results = solve_h_to_ne_blind(
            basis_size=16,
            grid_points=800,
            tolerance_hartree=3e-6,
            max_iterations=90,
        )
        self.assertEqual(len(results), 10)
        self.assertTrue(all(result.converged for result in results))
        self.assertTrue(all(b.energy_hartree < a.energy_hartree for a, b in zip(results, results[1:])))


if __name__ == "__main__":
    unittest.main()
