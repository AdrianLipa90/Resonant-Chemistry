import unittest

from reschem.multiplet_angular import (
    d_shell_ground_terms,
    p_shell_ground_terms,
    solve_equivalent_shell_multiplets,
)


class AngularMultipletTests(unittest.TestCase):
    def test_p_shell_ground_term_sequence(self):
        self.assertEqual(
            p_shell_ground_terms(),
            ("^2P", "^3P", "^4S", "^3P", "^2P", "^1S"),
        )

    def test_p2_full_term_content_and_microstates(self):
        result = solve_equivalent_shell_multiplets(1, 2)
        self.assertEqual(result.microstate_count, 15)
        self.assertEqual(
            [(term.symbol, term.degeneracy) for term in result.terms],
            [("^3P", 9), ("^1D", 5), ("^1S", 1)],
        )
        self.assertAlmostEqual(result.terms[0].energy_units, -0.2, places=10)
        self.assertAlmostEqual(result.terms[1].energy_units, 0.04, places=10)
        self.assertAlmostEqual(result.terms[2].energy_units, 0.4, places=10)

    def test_p3_full_term_content_and_microstates(self):
        result = solve_equivalent_shell_multiplets(1, 3)
        self.assertEqual(result.microstate_count, 20)
        self.assertEqual(
            [(term.symbol, term.degeneracy) for term in result.terms],
            [("^4S", 4), ("^2D", 10), ("^2P", 6)],
        )

    def test_d_shell_ground_term_sequence(self):
        self.assertEqual(
            d_shell_ground_terms(),
            (
                "^2D",
                "^3F",
                "^4F",
                "^5D",
                "^6S",
                "^5D",
                "^4F",
                "^3F",
                "^2D",
                "^1S",
            ),
        )

    def test_d5_microstate_count(self):
        result = solve_equivalent_shell_multiplets(2, 5)
        self.assertEqual(result.microstate_count, 252)
        self.assertEqual(result.ground_term.symbol, "^6S")
        self.assertEqual(result.ground_term.degeneracy, 6)


if __name__ == "__main__":
    unittest.main()
