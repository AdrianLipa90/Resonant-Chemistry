import unittest

from reschem.repository_cards import load_current_card_registry


class PolyhedralEclipseSemanticRegistryV015Tests(unittest.TestCase):
    def test_v015_model_card_is_in_current_registry(self):
        registry = load_current_card_registry()
        card = registry.resolve("MODEL:POLYHEDRAL_ECLIPSE_SPECTROSCOPY:v0.15")
        self.assertEqual(card["entity_level"], "spectral_feature_model")
        self.assertEqual(card["model_version"], "v0.15")
        self.assertEqual(card["physical_control"]["source_status"], "IMPLEMENTED_STAGE_A_FEATURE_LAYER")
        self.assertEqual(card["physical_control"]["spectral_validation"], "BLIND_COMPARISON_PENDING")
        self.assertEqual(card["tir"]["semantic_axes"]["values"]["kappa"], 0.009193150006360484)

    def test_v015_model_card_names_all_stage_a_sources(self):
        registry = load_current_card_registry()
        card = registry.resolve("MODEL:POLYHEDRAL_ECLIPSE_SPECTROSCOPY:v0.15")
        sources = card["source_artifacts"]
        self.assertIn("reschem/polyhedral_eclipse_spectroscopy.py", sources["implementation"])
        self.assertIn("reschem/pncs_semantic_mass_bridge_v015.py", sources["implementation"])
        self.assertIn("benchmarks/POLYHEDRAL_ECLIPSE_SPECTROSCOPY_PREREG_V0_15.json", sources["benchmarks"])
        self.assertIn("docs/polyhedral_eclipse_spectroscopy_v0_15.md", sources["documentation"])


if __name__ == "__main__":
    unittest.main()
