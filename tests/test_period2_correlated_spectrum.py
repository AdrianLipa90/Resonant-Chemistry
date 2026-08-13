import unittest

from reschem.atomic_radial_spectroscopy import solve_period2_atom_specific_spectroscopy
from reschem.period2_correlated_spectrum import solve_period2_correlated_spectrum


def level_energy(result, term, J):
    for level in result.levels:
        if level.approximate_term == term and level.J == J:
            return level.relative_energy_cm1
    raise AssertionError(f"missing {term}_{J}")


class Period2CorrelatedSpectrumTests(unittest.TestCase):
    def test_ground_J_sequence_for_selected_atoms(self):
        expected = {5: 0.5, 6: 0.0, 8: 2.0, 9: 1.5}
        for z, J in expected.items():
            result = solve_period2_correlated_spectrum(
                z,
                basis_size=16,
                grid_points=600,
                spectroscopy_basis_size=18,
                spectroscopy_grid_points=800,
            )
            self.assertEqual(result.ground_level.J, J)

    def test_boron_one_electron_split_is_preserved(self):
        previous = solve_period2_atom_specific_spectroscopy(
            5,
            basis_size=18,
            grid_points=800,
        )
        correlated = solve_period2_correlated_spectrum(
            5,
            basis_size=16,
            grid_points=600,
            spectroscopy_basis_size=18,
            spectroscopy_grid_points=800,
        )
        old_split = previous.levels[1].relative_energy_cm1
        new_split = level_energy(correlated, "^2P", 1.5)
        self.assertAlmostEqual(old_split, new_split, places=4)

    def test_correlated_regression_targets(self):
        # Internal numerical regression values from the reference-isolated
        # implementation-equivalent prototype. They are not experimental data.
        targets = {
            (6, "^3P", 1.0): 18.22,
            (6, "^3P", 2.0): 54.41,
            (8, "^3P", 1.0): 144.91,
            (8, "^3P", 0.0): 215.75,
            (9, "^2P", 0.5): 383.48,
        }
        cache = {}
        for (z, term, J), expected in targets.items():
            if z not in cache:
                cache[z] = solve_period2_correlated_spectrum(
                    z,
                    basis_size=18,
                    grid_points=800,
                    spectroscopy_basis_size=24,
                    spectroscopy_grid_points=1500,
                )
            value = level_energy(cache[z], term, J)
            self.assertLess(abs(value - expected), 1.0)


if __name__ == "__main__":
    unittest.main()
