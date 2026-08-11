import unittest

from reschem.mass_solver_s_shell import (
    SShellSpecies,
    first_blind_batch,
    solve_s_shell_richardson,
    solve_s_shell_uhf,
)


class BlindMassSolverTests(unittest.TestCase):
    def test_all_first_batch_species_converge(self):
        for species in first_blind_batch():
            result = solve_s_shell_uhf(species, points=159, tolerance_hartree=1e-7)
            self.assertTrue(result.converged, species.label)
            self.assertEqual(result.n_alpha + result.n_beta, species.electron_count)

    def test_one_electron_hydrogenic_scaling(self):
        for z in range(1, 5):
            species = SShellSpecies(f"Z{z}-one-electron", z, 1)
            result = solve_s_shell_richardson(species, coarse_points=159, tolerance_hartree=1e-8)
            exact = -0.5 * z * z
            relative = abs(result.extrapolated_energy_hartree - exact) / abs(exact)
            self.assertLess(relative, 4e-5)

    def test_spin_targets(self):
        singlet = solve_s_shell_uhf(SShellSpecies("He", 2, 2), points=159, tolerance_hartree=1e-7)
        doublet = solve_s_shell_uhf(SShellSpecies("Li", 3, 3), points=159, tolerance_hartree=1e-7)
        self.assertAlmostEqual(singlet.s2_expectation, 0.0, places=8)
        self.assertLess(abs(doublet.spin_contamination), 5e-4)

    def test_neutral_energy_ordering(self):
        neutral = [
            SShellSpecies("H", 1, 1),
            SShellSpecies("He", 2, 2),
            SShellSpecies("Li", 3, 3),
            SShellSpecies("Be", 4, 4),
        ]
        energies = [solve_s_shell_uhf(s, points=159, tolerance_hartree=1e-7).energy_hartree for s in neutral]
        self.assertTrue(all(b < a for a, b in zip(energies, energies[1:])))


if __name__ == "__main__":
    unittest.main()
