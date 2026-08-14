import unittest

from reschem.atom import Atom
from reschem.semantic_cards import make_atom_semantic_card, make_repository_semantic_overlay


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

    def test_repository_overlay_preserves_epistemic_separation(self):
        card = make_repository_semantic_overlay(
            card_id="MODEL:EXAMPLE:vX",
            entity_level="test_model",
            model_version="vX",
            identity={"model": "EXAMPLE"},
            source_artifacts={"benchmarks": ["benchmarks/example.json"]},
            physical_control={"status": "TEST_ONLY"},
            epistemic_status={"model": "TEST_ONLY"},
        )
        self.assertEqual(card["tir"]["semantic_axes"]["values"], {})
        self.assertEqual(card["affective_mapping"]["status"], "RESERVED_UNASSIGNED")
        self.assertEqual(card["source_artifacts"]["benchmarks"], ["benchmarks/example.json"])

    def test_repository_overlay_requires_provenance_source(self):
        with self.assertRaises(ValueError):
            make_repository_semantic_overlay(
                card_id="MODEL:BAD:vX",
                entity_level="test_model",
                model_version="vX",
                identity={},
                source_artifacts={},
                physical_control={},
                epistemic_status={},
            )


if __name__ == "__main__":
    unittest.main()
