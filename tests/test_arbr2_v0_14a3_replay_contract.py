import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG_PATH = ROOT / "benchmarks" / "MOLECULAR_STATE_RELAXATION_REPLAY_PREREG_V0_14A3.json"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "molecular-state-relaxation-v0.14a3-weak-linear-replay.yml"
PARENT_RECEIPT_PATH = ROOT / "benchmarks" / "v0_14a2_seed_receipts" / "ArBr2_weak_linear.json"
FROZEN_INPUT_PATH = ROOT / "benchmarks" / "v0_14a2_frozen_input" / "Br2.json"

EXPECTED_INPUT_SHA256 = "6c322bbc7ea31cfb51e4d195fcaeea32747e09447cd1dd56a8aab4771af19602"
EXPECTED_PARENT_BLOB_SHA1 = "b4476a0b7896950010987d7aed640b6495052a9f"
EXPECTED_SEED_SHA256 = "05c956d722e890dc3f0a5845c3e058681bf602c77560ace58a575d2df6c06101"
EXPECTED_METHOD_SHA256 = "9b58d32d361bd2c2248c10859b12785aa9aa0244e18b5504f6cbb79d2abe366d"


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


class ArBr2V014A3ReplayContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prereg = json.loads(PREREG_PATH.read_text(encoding="utf-8"))
        cls.workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    def test_preregistration_freezes_target_and_timeout_only_delta(self):
        row = self.prereg
        self.assertEqual(
            row["schema"],
            "RESCHEM_MOLECULAR_STATE_RELAXATION_REPLAY_PREREG_V0_14A3",
        )
        self.assertEqual(row["status"], "PREREGISTERED_NOT_EXECUTED")
        self.assertEqual(row["formula"], "ArBr2")
        self.assertEqual(row["target_seed"]["seed_id"], "ArBr2_weak_linear")
        self.assertEqual(
            row["target_seed"]["seed_identity_sha256"], EXPECTED_SEED_SHA256
        )
        self.assertEqual(
            row["frozen_method"]["method_policy_sha256"], EXPECTED_METHOD_SHA256
        )
        self.assertEqual(row["execution_envelope"]["first_attempt_timeout_seconds"], 2400)
        self.assertEqual(row["execution_envelope"]["replay_timeout_seconds"], 7200)
        self.assertEqual(row["execution_envelope"]["delta"], "TIME_BUDGET_ONLY")
        self.assertEqual(row["execution_envelope"]["timeout_multiplier"], 3.0)

        forbidden = (
            "method_change_allowed",
            "seed_change_allowed",
            "geometry_change_allowed",
            "basis_change_allowed",
            "grid_change_allowed",
            "scf_policy_change_allowed",
            "optimizer_policy_change_allowed",
            "rescue_allowed",
        )
        self.assertTrue(all(row["frozen_method"][key] is False for key in forbidden))

    def test_parent_and_frozen_input_bytes_are_pinned(self):
        parent_raw = PARENT_RECEIPT_PATH.read_bytes()
        self.assertEqual(git_blob_sha1(parent_raw), EXPECTED_PARENT_BLOB_SHA1)
        parent = json.loads(parent_raw)
        self.assertEqual(parent["seed_id"], "ArBr2_weak_linear")
        self.assertEqual(parent["seed_identity_sha256"], EXPECTED_SEED_SHA256)
        self.assertEqual(parent["method_policy_sha256"], EXPECTED_METHOD_SHA256)
        self.assertEqual(parent["execution_status"], "EXECUTION_TIMEOUT_UNKNOWN")
        self.assertEqual(
            parent["epistemic_status"]["execution"],
            "UNKNOWN_EXECUTION_NOT_CHEMICAL_FAIL",
        )

        frozen_raw = FROZEN_INPUT_PATH.read_bytes()
        self.assertEqual(hashlib.sha256(frozen_raw).hexdigest(), EXPECTED_INPUT_SHA256)
        self.assertEqual(
            self.prereg["frozen_input"]["raw_json_sha256"], EXPECTED_INPUT_SHA256
        )

    def test_workflow_is_manual_only_and_executes_exact_preregistered_replay(self):
        text = self.workflow
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("\n  push:\n", text)
        self.assertIn("timeout-minutes: 140", text)
        self.assertIn("--seed ArBr2_weak_linear", text)
        self.assertIn(
            "--dimer-json benchmarks/v0_14a2_frozen_input/Br2.json", text
        )
        self.assertIn("--timeout-seconds 7200", text)
        self.assertIn("--output-dir benchmarks/v0_14a3_replay_receipts", text)
        self.assertNotIn("--output-dir benchmarks/v0_14a2_seed_receipts", text)

    def test_replay_cannot_replace_first_attempt_or_auto_promote(self):
        admission = self.prereg["admission"]
        self.assertTrue(admission["preserve_first_attempt_receipt"])
        self.assertFalse(admission["overwrite_parent_receipt"])
        self.assertFalse(admission["replay_result_may_replace_parent_evidence"])
        self.assertFalse(
            admission["replay_result_automatically_promotes_formula_checkpoint"]
        )
        self.assertTrue(admission["promotion_requires_explicit_lineage_audit"])
        self.assertTrue(admission["promotion_requires_no_unresolved_execution_unit"])

        boundary = self.prereg["epistemic_boundary"]
        self.assertFalse(boundary["timeout_is_chemical_failure"])
        self.assertEqual(boundary["hessian_admission"], "NOT_RUN")
        self.assertEqual(boundary["ground_state_ranking"], "NOT_VALIDATED")
        self.assertEqual(
            boundary["geometry_only_topology_assignment"], "NOT_PROMOTED"
        )


if __name__ == "__main__":
    unittest.main()
