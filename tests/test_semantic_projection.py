import json
from pathlib import Path
import unittest

from reschem.entity_registry import CardRegistry
from reschem.molecular_semantic_projection import project_molecular_screen_readout
from reschem.semantic_projection import (
    generate_compound_candidate_cards,
    generate_relational_state_cards,
)


ROOT = Path(__file__).resolve().parents[1]


class SemanticProjectionTests(unittest.TestCase):
    def test_compound_atlas_projects_to_231_emergent_cards(self):
        cards = generate_compound_candidate_cards()
        self.assertEqual(len(cards), 231)
        self.assertEqual(len({card["card_id"] for card in cards}), 231)
        self.assertTrue(all(card["emergence"]["status"] == "MODEL_DEFINED_EMERGENT_CANDIDATE" for card in cards))
        self.assertTrue(all(card["tir"]["semantic_axes"]["values"] == {} for card in cards))

    def test_v013_projects_to_27_unranked_state_cards(self):
        cards = generate_relational_state_cards()
        self.assertEqual(len(cards), 27)
        self.assertEqual(len({card["card_id"] for card in cards}), 27)
        for card in cards:
            self.assertIsNone(card["properties"]["prior_rank"])
            self.assertIsNone(card["properties"]["prior_probability"])
            self.assertEqual(card["physical_holonomy"]["status"], "CANDIDATE_NOT_COMPUTED_FOR_THIS_ENTITY")

    def test_molecular_projection_tracks_partial_execution_exactly(self):
        path = ROOT / "benchmarks" / "MOLECULAR_STATE_RELAXATION_PARTIAL_READOUT_V0_14A1.json"
        readout = json.loads(path.read_text(encoding="utf-8"))
        cards = project_molecular_screen_readout(readout)
        self.assertEqual(len(cards), 10)  # one model card + nine formula cards
        by_id = {card["card_id"]: card for card in cards}
        self.assertEqual(
            by_id["MOLECULE:ArBr2:SCREEN:v0.14A1"]["properties"]["execution_status"],
            "MISSING_EXECUTION_NOT_CHEMICAL_FAIL",
        )
        self.assertEqual(
            by_id["MOLECULE:KrF2:SCREEN:v0.14A1"]["epistemic_status"]["ground_state_ranking"],
            "NOT_VALIDATED",
        )
        self.assertEqual(
            by_id["MODEL:MOLECULAR_STATE_RELAXATION:v0.14A1"]["properties"]["completed_starts"],
            40,
        )

    def test_registry_can_supply_calculation_context_across_emergent_cards(self):
        cards = list(generate_relational_state_cards())
        registry = CardRegistry(cards)
        selected = [
            "RELATIONAL_STATE:KrF2:ACTIVATED_LINEAR_3C4E:v0.13",
            "RELATIONAL_STATE:KrF2:WEAK_COMPLEX_LINEAR_END_ON:v0.13",
        ]
        context = registry.calculation_context(selected)
        self.assertEqual(context["card_ids"], selected)
        self.assertEqual(context["status"], "DERIVED_CALCULATION_CONTEXT_NOT_SCIENTIFIC_PROMOTION")


if __name__ == "__main__":
    unittest.main()
