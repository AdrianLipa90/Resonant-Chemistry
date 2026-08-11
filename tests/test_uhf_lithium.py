import unittest

from reschem.uhf_lithium import solve_lithium_radial_uhf, solve_lithium_radial_uhf_richardson


class LithiumUHFTests(unittest.TestCase):
    def test_open_shell_solution_converges(self):
        result = solve_lithium_radial_uhf(points=120)
        self.assertTrue(result.converged)
        self.assertLess(result.energy_hartree, 0.0)
        self.assertLess(abs(result.spin_contamination), 1.0e-3)

    def test_finer_grid_lowers_energy(self):
        coarse = solve_lithium_radial_uhf(points=120)
        fine = solve_lithium_radial_uhf(points=240)
        self.assertLess(fine.energy_hartree, coarse.energy_hartree)

    def test_richardson_moves_toward_atomic_hf_reference(self):
        result = solve_lithium_radial_uhf_richardson(coarse_points=200)
        self.assertTrue(result.coarse.converged)
        self.assertTrue(result.fine.converged)
        self.assertLess(result.relative_error_vs_hf_reference, 0.01)


if __name__ == "__main__":
    unittest.main()
