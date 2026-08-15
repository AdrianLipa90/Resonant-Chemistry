import unittest

from reschem.molecular_state_relaxation import xy2_seed_geometries
from reschem.phasenav_chem import (
    FROZEN_METHOD_POLICY_SHA256,
    SEED_RECEIPT_SCHEMA,
    aggregate_seed_receipts,
    assert_frozen_method_gate,
    frozen_seed_manifest,
    phase36_encode,
    seed_identity_sha256,
    select_frozen_seed,
)


class PhaseNavChemV014A2Tests(unittest.TestCase):
    RYY = 2.30

    def test_frozen_method_policy_hash(self):
        self.assertEqual(assert_frozen_method_gate(), FROZEN_METHOD_POLICY_SHA256)

    def test_manifest_has_exact_five_frozen_arbr2_seeds(self):
        manifest = frozen_seed_manifest("Ar", "Br", self.RYY)
        self.assertEqual(manifest["seed_count"], 5)
        self.assertEqual(
            [item["seed_id"] for item in manifest["seeds"]],
            [
                "ArBr2_activated_s1p0",
                "ArBr2_activated_s1p3",
                "ArBr2_activated_s1p6",
                "ArBr2_weak_linear",
                "ArBr2_weak_t",
            ],
        )

    def test_phase36_is_deterministic_and_nonphysical_metadata(self):
        seed = select_frozen_seed("Ar", "Br", self.RYY, "ArBr2_activated_s1p0")
        first = phase36_encode(seed)
        second = phase36_encode(seed)
        self.assertEqual(first, second)
        self.assertEqual(first["dimension"], 36)
        self.assertEqual(len(first["vector"]), 36)
        self.assertEqual(
            first["status"],
            "MODEL_DEFINED_EXECUTION_ADDRESS_NOT_PHYSICAL_OBSERVABLE",
        )

    def _receipts(self, unknown_seed=None):
        receipts = []
        for index, seed in enumerate(xy2_seed_geometries("Ar", "Br", self.RYY)):
            if seed.seed_id == unknown_seed:
                backend = {
                    "seed": seed.to_dict(),
                    "status": "EXECUTION_TIMEOUT_UNKNOWN",
                }
            else:
                backend = {
                    "seed": seed.to_dict(),
                    "status": "RELAXATION_RETURNED_FINAL_SCF_CONVERGED_NO_HESSIAN",
                    "final_energy_hartree": -1000.0 + index * 0.001,
                }
            receipts.append(
                {
                    "schema": SEED_RECEIPT_SCHEMA,
                    "formula": "ArBr2",
                    "method_policy_sha256": FROZEN_METHOD_POLICY_SHA256,
                    "seed_id": seed.seed_id,
                    "seed_identity_sha256": seed_identity_sha256(seed),
                    "backend_result": backend,
                }
            )
        return receipts

    def test_aggregate_reconstructs_five_start_formula_receipt(self):
        payload = aggregate_seed_receipts("Ar", "Br", self.RYY, self._receipts())
        self.assertEqual(payload["schema"], "RESCHEM_MOLECULAR_FORMULA_RELAXATION_V0_14A")
        self.assertEqual(payload["execution_partition"], "v0.14A2_PER_SEED")
        self.assertEqual(payload["status"], "FORMULA_RELAXATION_SCREEN_COMPLETE")
        self.assertEqual(payload["start_count"], 5)
        self.assertEqual(payload["successful_relaxation_count"], 5)
        self.assertEqual(payload["unknown_execution_seed_ids"], [])
        self.assertEqual(len(payload["relaxations"]), 5)

    def test_timeout_is_unknown_not_chemical_fail(self):
        missing = "ArBr2_activated_s1p6"
        payload = aggregate_seed_receipts(
            "Ar", "Br", self.RYY, self._receipts(unknown_seed=missing)
        )
        self.assertEqual(
            payload["status"],
            "FORMULA_EXECUTION_PARTITION_COMPLETE_WITH_UNKNOWN_SEEDS",
        )
        self.assertEqual(payload["unknown_execution_seed_ids"], [missing])
        self.assertNotIn("CHEMICAL_FAIL", payload["status"])

    def test_seed_identity_gate_rejects_unknown_seed(self):
        with self.assertRaises(ValueError):
            select_frozen_seed("Ar", "Br", self.RYY, "ArBr2_rescue_custom")


if __name__ == "__main__":
    unittest.main()
