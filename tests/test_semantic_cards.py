import unittest

from reschem.atom import Atom
from reschem.semantic_cards import make_atom_semantic_card


class SemanticCardTests(unittest.TestCase):
    def test_hydrogen_card(self):
        card = make_atom_semantic_card(Atom(1, 0))
        self.assertEqual(card["card_id"], "ATOM:H:1:q+0")
        self.assertEqual(card["physical_control"]["electron_configuration"], "1s^1")
        self.assertEqual(card["affective_mapping"]["status"], "RESERVED_UNASSIGNED")

    def test_helium_closed_shell(self):
        card = make_atom_semantic_card(Atom(2, 2))
        self.assertTrue(card["physical_control"]["closed_shell_control"])
        self.assertEqual(card["physical_control"]["outer_shell_electrons"], 2)

    def test_interpretive_layers_are_not_silent_defaults(self):
        card = make_atom_semantic_card(Atom(6, 6))
        self.assertEqual(card["tir"]["semantic_axes"]["values"], {})
        self.assertEqual(card["affective_mapping"]["labels"], [])
        self.assertEqual(card["epistemic_status"]["affective_semantics"], "OPEN")


if __name__ == "__main__":
    unittest.main()
