import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECOVERY_PATH = (
    ROOT
    / "benchmarks"
    / "v0_14a2_seed_receipts"
    / "ARBR2_CANONICAL_RUN_RECOVERY.json"
)
SEED_DIR = ROOT / "benchmarks" / "v0_14a2_seed_receipts"

EXPECTED_METHOD_SHA256 = (
    "9b58d32d361bd2c2248c10859b12785aa9aa0244e18b5504f6cbb79d2abe366d"
)
EXPECTED_SEEDS = {
    "ArBr2_activated_s1p0": {
        "identity": "f4a3399a565ac2688ed568edb839c036d981006ef3a1d5ee57c9ce99edaca629",
        "status": "RELAXATION_RETURNED_FINAL_SCF_CONVERGED_NO_HESSIAN",
    },
    "ArBr2_activated_s1p3": {
        "identity": "be90ec4a53bff85348b0ebfc45515e3e25a3ec96d5e52169720c0d46a8873127",
        "status": "RELAXATION_EXCEPTION",
    },
    "ArBr2_activated_s1p6": {
        "identity": "bd5478a6059cdabe85c1732853177473bd2b3d78bb516a318ff416f958a0a30b",
        "status": "INITIAL_SCF_FAILED_NO_RESCUE",
    },
    "ArBr2_weak_linear": {
        "identity": "05c956d722e890dc3f0a5845c3e058681bf602c77560ace58a575d2df6c06101",
        "status": "EXECUTION_TIMEOUT_UNKNOWN",
    },
    "ArBr2_weak_t": {
        "identity": "866f804d66d2c865c1275b4d0c6f71e90d783b85cb9e831562fb668a244f1cfa",
        "status": "RELAXATION_RETURNED_FINAL_SCF_CONVERGED_NO_HESSIAN",
    },
}
EXPECTED_GATES = {
    "method_frozen": "PASS",
    "seed_identity": "PASS",
    "no_rescue": "PASS",
    "phase36_dimension": "PASS",
}


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


class ArBr2CanonicalRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.recovery = json.loads(RECOVERY_PATH.read_text(encoding="utf-8"))

    def test_recovery_manifest_pins_canonical_execution_source(self):
        row = self.recovery
        self.assertEqual(
            row["schema"], "RESCHEM_ARBR2_V0_14A2_CANONICAL_RUN_RECOVERY_V1"
        )
        self.assertEqual(row["formula"], "ArBr2")
        self.assertEqual(row["execution_partition"], "v0.14A2_PER_SEED")
        self.assertEqual(row["canonical_workflow_run_id"], 31887655166)
        self.assertEqual(
            row["canonical_source_head"],
            "506b6631fa36fadea32210cd884b5481250f8a08",
        )
        self.assertEqual(row["workflow_conclusion"], "success")
        self.assertEqual(row["method_policy_sha256"], EXPECTED_METHOD_SHA256)
        self.assertTrue(row["seed_receipts_persisted_in_repository"])

    def test_all_five_seed_receipts_are_byte_pinned_and_identity_gated(self):
        manifest_seeds = self.recovery["seed_receipts"]
        self.assertEqual(set(manifest_seeds), set(EXPECTED_SEEDS))

        for seed_id, expected in EXPECTED_SEEDS.items():
            with self.subTest(seed_id=seed_id):
                path = SEED_DIR / f"{seed_id}.json"
                self.assertTrue(path.is_file(), seed_id)
                raw = path.read_bytes()
                payload = json.loads(raw.decode("utf-8"))
                provenance = manifest_seeds[seed_id]

                self.assertEqual(
                    git_blob_sha1(raw), provenance["repository_blob_sha1"]
                )
                self.assertEqual(payload["seed_id"], seed_id)
                self.assertEqual(
                    payload["seed_identity_sha256"], expected["identity"]
                )
                self.assertEqual(
                    payload["method_policy_sha256"], EXPECTED_METHOD_SHA256
                )
                self.assertEqual(payload["gates"], EXPECTED_GATES)
                self.assertEqual(payload["phase36"]["dimension"], 36)
                self.assertEqual(payload["execution_status"], expected["status"])
                self.assertEqual(
                    provenance["execution_status"], expected["status"]
                )

    def test_timeout_remains_unknown_and_cannot_promote_checkpoint(self):
        payload = json.loads(
            (SEED_DIR / "ArBr2_weak_linear.json").read_text(encoding="utf-8")
        )
        self.assertEqual(payload["execution_status"], "EXECUTION_TIMEOUT_UNKNOWN")
        self.assertEqual(
            payload["epistemic_status"]["execution"],
            "UNKNOWN_EXECUTION_NOT_CHEMICAL_FAIL",
        )
        self.assertEqual(
            payload["backend_result"]["scientific_interpretation"],
            "UNKNOWN_EXECUTION_NOT_CHEMICAL_FAIL",
        )

        checkpoint = self.recovery["scientific_checkpoint"]
        self.assertEqual(checkpoint["formulae_complete"], "8/9")
        self.assertEqual(checkpoint["starts_complete"], "40/45")
        self.assertFalse(checkpoint["promotion_condition_met"])
        self.assertIn("ArBr2_weak_linear", checkpoint["blocker"])

    def test_aggregate_provenance_records_unknown_without_repository_substitution(self):
        aggregate = self.recovery["aggregate"]
        self.assertEqual(
            aggregate["status"],
            "FORMULA_EXECUTION_PARTITION_COMPLETE_WITH_UNKNOWN_SEEDS",
        )
        self.assertEqual(aggregate["start_count"], 5)
        self.assertEqual(aggregate["attempted_start_count"], 5)
        self.assertEqual(aggregate["successful_relaxation_count"], 2)
        self.assertEqual(
            aggregate["unknown_execution_seed_ids"], ["ArBr2_weak_linear"]
        )
        self.assertFalse(aggregate["repository_copy_persisted"])
        self.assertEqual(
            aggregate["artifact_zip_sha256"],
            "51adeadd4e12ac970f6bbfcf70655312aad7c97c6509afa62d7c7133699d4764",
        )
        self.assertEqual(
            aggregate["raw_json_sha256"],
            "76eaf92fb81a0cf140a2b8b75ae0b511cdca15a281acf2b05987545c1e4649c8",
        )
        self.assertEqual(
            aggregate["raw_json_git_blob_sha1"],
            "9eb889789ff5204ecd61d5e9f855aa02f18e8cd7",
        )


if __name__ == "__main__":
    unittest.main()
