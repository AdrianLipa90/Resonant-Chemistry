import math
import unittest

from reschem.atomic_radial_spectroscopy import solve_period2_atom_specific_spectroscopy


class Period2AtomSpecificSpectroscopyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = {
            z: solve_period2_atom_specific_spectroscopy(
                z,
                basis_size=16,
                grid_points=800,
                tolerance_hartree=1e-6,
                max_iterations=100,
            )
            for z in range(5, 11)
        }

    def test_all_period2_p_atoms_converge_to_finite_control_state(self):
        for z, result in self.results.items():
            self.assertTrue(math.isfinite(result.hf_energy_hartree), z)
            self.assertTrue(math.isfinite(result.virial_residual_hartree), z)
            self.assertGreater(result.slater_f2_hartree, 0.0, z)
            self.assertGreater(result.zeta_2p_hartree, 0.0, z)

    def test_radial_F2_and_zeta_increase_from_boron_to_fluorine(self):
        f2 = [self.results[z].slater_f2_hartree for z in range(5, 10)]
        zeta = [self.results[z].zeta_2p_hartree for z in range(5, 10)]
        self.assertTrue(all(b > a for a, b in zip(f2, f2[1:])))
        self.assertTrue(all(b > a for a, b in zip(zeta, zeta[1:])))

    def test_ground_LS_sequence_is_computed_for_p_shell(self):
        expected = ("^2P", "^3P", "^4S", "^3P", "^2P", "^1S")
        actual = tuple(self.results[z].ground_LS_term for z in range(5, 11))
        self.assertEqual(actual, expected)

    def test_ground_J_sequence_has_particle_hole_reversal(self):
        expected = (0.5, 0.0, 1.5, 2.0, 1.5, 0.0)
        actual = tuple(self.results[z].ground_J for z in range(5, 11))
        self.assertEqual(actual, expected)

    def test_fine_structure_level_degeneracies_span_full_microstate_space(self):
        for z, result in self.results.items():
            expected_microstates = math.comb(6, result.p_electron_count)
            actual_microstates = sum(level.degeneracy for level in result.levels)
            self.assertEqual(actual_microstates, expected_microstates, z)


if __name__ == "__main__":
    unittest.main()
