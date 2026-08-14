import unittest

from reschem.coordination_ladder import (
    coordination_degrees,
    coordination_ladder,
    monovalent_ligand_candidates,
)


Z = {
    "N": 7,
    "O": 8,
    "F": 9,
    "P": 15,
    "S": 16,
    "Cl": 17,
    "As": 33,
    "Se": 34,
    "Br": 35,
    "Kr": 36,
}


class CoordinationLadderTests(unittest.TestCase):
    def test_second_period_does_not_expand(self):
        self.assertEqual(coordination_degrees(Z["N"]), (3,))
        self.assertEqual(coordination_degrees(Z["O"]), (2,))
        self.assertEqual(coordination_degrees(Z["F"]), (1,))

    def test_period_three_above_half_ladders(self):
        self.assertEqual(coordination_degrees(Z["P"]), (3, 5))
        self.assertEqual(coordination_degrees(Z["S"]), (2, 4, 6))
        self.assertEqual(coordination_degrees(Z["Cl"]), (1, 3, 5, 7))

    def test_period_four_above_half_ladders(self):
        self.assertEqual(coordination_degrees(Z["As"]), (3, 5))
        self.assertEqual(coordination_degrees(Z["Se"]), (2, 4, 6))
        self.assertEqual(coordination_degrees(Z["Br"]), (1, 3, 5, 7))

    def test_closed_shell_remains_fail_closed(self):
        states = coordination_ladder(Z["Kr"])
        self.assertEqual(len(states), 1)
        self.assertEqual(states[0].relation_degree, 0)
        self.assertEqual(states[0].branch, "CLOSED_UNACTIVATED")

    def test_phosphorus_chloride_candidates(self):
        candidates = monovalent_ligand_candidates(Z["P"], Z["Cl"])
        self.assertEqual(
            tuple(candidate.empirical_formula for candidate in candidates),
            ("PCl3", "PCl5"),
        )
        self.assertEqual(tuple(candidate.q for candidate in candidates), (0, 1))

    def test_sulfur_fluoride_candidates(self):
        candidates = monovalent_ligand_candidates(Z["S"], Z["F"])
        self.assertEqual(
            tuple(candidate.empirical_formula for candidate in candidates),
            ("SF2", "SF4", "SF6"),
        )
        self.assertEqual(tuple(candidate.q for candidate in candidates), (0, 1, 2))

    def test_bromine_fluoride_candidates_include_unvalidated_top_rung(self):
        candidates = monovalent_ligand_candidates(Z["Br"], Z["F"])
        self.assertEqual(
            tuple(candidate.empirical_formula for candidate in candidates),
            ("BrF", "BrF3", "BrF5", "BrF7"),
        )
        self.assertEqual(tuple(candidate.q for candidate in candidates), (0, 1, 2, 3))

    def test_non_monovalent_ligand_fails_closed(self):
        with self.assertRaises(ValueError):
            monovalent_ligand_candidates(Z["P"], Z["O"])


if __name__ == "__main__":
    unittest.main()
