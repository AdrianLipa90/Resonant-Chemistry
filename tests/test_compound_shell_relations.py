import unittest

from reschem.compound_shell_relations import (
    binary_saturation_skeleton,
    stoichiometric_balance_residual,
    valence_shell_profile,
)

Z = {
    "H": 1, "Li": 3, "Be": 4, "B": 5, "C": 6, "N": 7,
    "O": 8, "F": 9, "Ne": 10, "Na": 11, "Mg": 12,
    "Al": 13, "Si": 14, "P": 15, "S": 16, "Cl": 17,
    "Fe": 26,
}


class CompoundShellRelationTests(unittest.TestCase):
    def test_second_period_relation_degree_sequence(self):
        got = [
            valence_shell_profile(Z[symbol]).relation_degree
            for symbol in ("Li", "Be", "B", "C", "N", "O", "F", "Ne")
        ]
        self.assertEqual(got, [1, 2, 3, 4, 3, 2, 1, 0])

    def test_hydride_series(self):
        expected = {
            "Li": "LiH", "Be": "BeH2", "B": "BH3", "C": "CH4",
            "N": "NH3", "O": "OH2", "F": "FH",
        }
        for symbol, formula in expected.items():
            relation = binary_saturation_skeleton(Z[symbol], Z["H"])
            self.assertIsNotNone(relation)
            self.assertEqual(relation.empirical_formula, formula)

    def test_oxide_skeletons(self):
        expected = {
            "B": "B2O3", "C": "CO2", "Al": "Al2O3",
            "Si": "SiO2", "Na": "Na2O", "Mg": "MgO",
        }
        for symbol, formula in expected.items():
            relation = binary_saturation_skeleton(Z[symbol], Z["O"])
            self.assertIsNotNone(relation)
            self.assertEqual(relation.empirical_formula, formula)

    def test_chloride_skeletons(self):
        expected = {
            "Na": "NaCl", "Mg": "MgCl2", "Al": "AlCl3",
            "Si": "SiCl4", "P": "PCl3", "S": "SCl2",
        }
        for symbol, formula in expected.items():
            relation = binary_saturation_skeleton(Z[symbol], Z["Cl"])
            self.assertIsNotNone(relation)
            self.assertEqual(relation.empirical_formula, formula)

    def test_noble_gas_is_blocked(self):
        self.assertIsNone(binary_saturation_skeleton(Z["Ne"], Z["H"]))

    def test_transition_metal_fails_closed(self):
        with self.assertRaises(ValueError):
            valence_shell_profile(Z["Fe"])

    def test_endpoint_balance(self):
        self.assertTrue(stoichiometric_balance_residual({Z["C"]: 1, Z["H"]: 4})["balanced"])
        self.assertFalse(stoichiometric_balance_residual({Z["C"]: 1, Z["H"]: 3})["balanced"])

    def test_particle_hole_complementarity_na_cl(self):
        relation = binary_saturation_skeleton(Z["Na"], Z["Cl"])
        self.assertIsNotNone(relation)
        self.assertAlmostEqual(relation.particle_hole_complementarity, 1.0, places=12)


if __name__ == "__main__":
    unittest.main()
