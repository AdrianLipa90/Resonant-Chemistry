import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "benchmarks" / "MOLECULAR_STATE_RELAXATION_ACTIVATED_SURVIVAL_MATRIX_V0_14A1_PARTIAL.json"
OVERLAY = ROOT / "semantic_cards" / "MOLECULAR_ACTIVATED_SURVIVAL_V0_14A1.jsonl"


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class SemanticSurvivalOverlayTests(unittest.TestCase):
    def test_overlay_matches_benchmark_exactly(self):
        source = json.loads(BENCHMARK.read_text(encoding="utf-8"))
        cards = load_jsonl(OVERLAY)
        by_formula = {card["identity"]["formula"]: card for card in cards}
        self.assertEqual(set(by_formula), set(source["cells"]))

        keys = (
            "activated_successful",
            "activated_starts",
            "activated_to_lowest_weak_gap_kcal_mol",
            "mean_XY_angstrom_lowest_successful_activated",
        )
        for formula, expected in source["cells"].items():
            card = by_formula[formula]
            control = card["physical_control"]
            for key in keys:
                self.assertEqual(control.get(key), expected.get(key), (formula, key))
            if formula == "ArBr2":
                self.assertEqual(control.get("status"), "MISSING_EXECUTION")
            self.assertEqual(control["readout_status"], "DESCRIPTIVE_ONLY_NO_FIT_NO_THRESHOLD")
            self.assertEqual(card["tir"]["semantic_axes"]["values"], {})
            self.assertEqual(card["affective_mapping"]["labels"], [])
            self.assertEqual(card["affective_mapping"]["coordinates"], {})
            self.assertEqual(card["epistemic_status"]["hessian_admission"], "NOT_RUN")
            self.assertEqual(card["epistemic_status"]["ground_state_ranking"], "NOT_VALIDATED")
            self.assertEqual(card["epistemic_status"]["topology_assignment"], "NOT_PROMOTED")

    def test_f_ligand_sequence_is_descriptive_not_fitted(self):
        source = json.loads(BENCHMARK.read_text(encoding="utf-8"))
        gaps = [source["cells"][formula]["activated_to_lowest_weak_gap_kcal_mol"] for formula in ("NeF2", "ArF2", "KrF2")]
        self.assertGreater(gaps[0], gaps[1])
        self.assertGreater(gaps[1], gaps[2])
        self.assertIn("no activation law is fitted", source["forbidden_inference"])


if __name__ == "__main__":
    unittest.main()
