import unittest

from reschem.multiplet_spin_orbit import (
    d_shell_ground_J_sequence,
    p_shell_ground_J_sequence,
    solve_spin_orbit_ground,
)


class SpinOrbitMultipletTests(unittest.TestCase):
    def test_p_shell_ground_J_sequence(self):
        self.assertEqual(
            p_shell_ground_J_sequence(),
            (0.5, 0.0, 1.5, 2.0, 1.5, 0.0),
        )

    def test_d_shell_ground_J_sequence(self):
        self.assertEqual(
            d_shell_ground_J_sequence(),
            (1.5, 2.0, 1.5, 0.0, 2.5, 4.0, 4.5, 4.0, 2.5, 0.0),
        )

    def test_p2_ground_is_triplet_P_J0(self):
        result = solve_spin_orbit_ground(1, 2)
        self.assertEqual(result.LS_ground_term, "^3P")
        self.assertEqual(result.J, 0.0)
        self.assertEqual(result.degeneracy, 1)

    def test_d7_ground_is_quartet_F_J9_over_2(self):
        result = solve_spin_orbit_ground(2, 7)
        self.assertEqual(result.LS_ground_term, "^4F")
        self.assertEqual(result.J, 4.5)
        self.assertEqual(result.degeneracy, 10)


if __name__ == "__main__":
    unittest.main()
