import unittest

from reschem.entity_registry import (
    CardRegistry,
    lineage_sha256,
    make_emergent_candidate_card,
    make_entity_card,
    make_relation,
)


class EntityRegistryTests(unittest.TestCase):
    def test_lineage_hash_is_order_stable_for_parent_set(self):
        a = lineage_sha256(parents=["B", "A"], operation="op", identity={"x": 1})
        b = lineage_sha256(parents=["A", "B"], operation="op", identity={"x": 1})
        self.assertEqual(a, b)

    def test_physical_holonomy_requires_provenance_when_computed(self):
        with self.assertRaises(ValueError):
            make_entity_card(
                card_id="X",
                entity_level="test",
                identity={"x": 1},
                properties={},
                state_invariants={},
                source_artifacts={"implementation": ["reschem/x.py"]},
                epistemic_status={"entity": "TEST"},
                physical_holonomy={"status": "CANDIDATE_COMPUTED", "observables": {}},
            )

    def test_emergence_does_not_imply_validation(self):
        card = make_emergent_candidate_card(
            card_id="EMERGENT:X",
            entity_level="candidate",
            identity={"x": 1},
            properties={},
            state_invariants={},
            source_artifacts={"implementation": ["reschem/x.py"]},
            parent_card_ids=["PARENT:A"],
            generating_operation="derive_x",
        )
        self.assertEqual(card["emergence"]["status"], "MODEL_DEFINED_EMERGENT_CANDIDATE")
        self.assertEqual(card["epistemic_status"]["physical_validation"], "OPEN")
        self.assertEqual(card["tir"]["semantic_axes"]["values"], {})

    def test_relation_requires_exactly_one_target_mode(self):
        with self.assertRaises(ValueError):
            make_relation(source_card_id="A", predicate="R")
        with self.assertRaises(ValueError):
            make_relation(source_card_id="A", predicate="R", target_card_id="B", target_selector={"x": 1})

    def test_registry_context_is_deterministic(self):
        card = make_entity_card(
            card_id="ENTITY:A",
            entity_level="test",
            identity={"x": 1},
            properties={"p": 2},
            state_invariants={},
            source_artifacts={"implementation": ["reschem/x.py"]},
            epistemic_status={"entity": "TEST"},
        )
        registry = CardRegistry([card])
        first = registry.calculation_context(["ENTITY:A"])
        second = registry.calculation_context(["ENTITY:A"])
        self.assertEqual(first["context_sha256"], second["context_sha256"])


if __name__ == "__main__":
    unittest.main()
