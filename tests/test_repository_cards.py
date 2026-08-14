import unittest

from reschem.repository_cards import calculation_context, load_current_card_registry


class RepositoryCardRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = load_current_card_registry()

    def test_registry_contains_current_calculation_population(self):
        # 36 canonical neutral atoms + 13 persisted model cards +
        # 231 v0.1 compound candidates + 27 v0.13 states +
        # 10 v0.14A1 model/formula cards. Additional evidence overlays may add more.
        self.assertGreaterEqual(len(self.registry.cards), 317)

    def test_atom_selector_resolves_kr(self):
        matched = self.registry.match_selector({"identity.symbol": "Kr", "identity.charge": 0})
        self.assertTrue(matched)
        self.assertTrue(any(card.get("identity", {}).get("symbol") == "Kr" for card in matched))

    def test_relational_state_resolves_centre_and_ligand_cards(self):
        card_id = "RELATIONAL_STATE:KrF2:ACTIVATED_LINEAR_3C4E:v0.13"
        centres = self.registry.relation_targets(card_id, "HAS_CENTRE")
        ligands = self.registry.relation_targets(card_id, "HAS_LIGAND")
        self.assertTrue(any(card.get("identity", {}).get("symbol") == "Kr" for card in centres))
        self.assertTrue(any(card.get("identity", {}).get("symbol") == "F" for card in ligands))

    def test_provenance_lineage_reaches_parent_models(self):
        lineage = self.registry.provenance_lineage(
            "RELATIONAL_STATE:KrF2:ACTIVATED_LINEAR_3C4E:v0.13"
        )
        self.assertIn("MODEL:CLOSED_SHELL_ACTIVATION:v0.9", lineage)
        self.assertIn("MODEL:COMPOUND_STATE_ENSEMBLE:v0.13", lineage)

    def test_molecular_context_can_pull_parent_state_cards(self):
        context = calculation_context(["MOLECULE:KrF2:SCREEN:v0.14A1"])
        self.assertIn("MOLECULE:KrF2:SCREEN:v0.14A1", context["card_ids"])
        self.assertIn("RELATIONAL_STATE:KrF2:ACTIVATED_LINEAR_3C4E:v0.13", context["card_ids"])
        self.assertIn("RELATIONAL_STATE:KrF2:WEAK_COMPLEX_LINEAR_END_ON:v0.13", context["card_ids"])
        self.assertIn("RELATIONAL_STATE:KrF2:WEAK_COMPLEX_T_SHAPED:v0.13", context["card_ids"])
        self.assertEqual(context["status"], "DERIVED_CALCULATION_CONTEXT_NOT_SCIENTIFIC_PROMOTION")


if __name__ == "__main__":
    unittest.main()
