import importlib.util
import json
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "wrap_molecular_relaxation_v0_14a1.py"
SPEC = importlib.util.spec_from_file_location("wrap_molecular_relaxation_v0_14a1", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class MolecularExecutionWrapperTests(unittest.TestCase):
    def _raw(self):
        return {
            "schema": MODULE.RAW_SCHEMA,
            "formula_count": 9,
            "relaxation_start_count": 45,
            "successful_relaxation_count": 40,
            "status_counts": {"RELAXATION_RETURNED_FINAL_SCF_CONVERGED_NO_HESSIAN": 40},
            "formulae": [{"formula": f"X{i}Y2"} for i in range(9)],
        }

    def test_wrapper_preserves_raw_payload_and_adds_amendment(self):
        raw = json.dumps(self._raw(), sort_keys=True).encode("utf-8")
        wrapped = MODULE.wrap_execution(
            raw,
            workflow_run_id=123,
            workflow_head_sha="abcdef0123456789",
        )
        self.assertEqual(wrapped["schema"], MODULE.WRAPPED_SCHEMA)
        self.assertEqual(wrapped["combined_execution"], self._raw())
        self.assertEqual(wrapped["numerical_amendment"], MODULE.AMENDMENT)
        self.assertEqual(wrapped["workflow"]["run_id"], 123)
        self.assertEqual(wrapped["raw_summary"]["relaxation_start_count"], 45)

    def test_wrong_start_count_fails_closed(self):
        raw_payload = self._raw()
        raw_payload["relaxation_start_count"] = 44
        raw = json.dumps(raw_payload).encode("utf-8")
        with self.assertRaises(ValueError):
            MODULE.wrap_execution(
                raw,
                workflow_run_id=123,
                workflow_head_sha="abcdef0123456789",
            )

    def test_duplicate_formulae_fail_closed(self):
        raw_payload = self._raw()
        raw_payload["formulae"][-1] = {"formula": "X0Y2"}
        raw = json.dumps(raw_payload).encode("utf-8")
        with self.assertRaises(ValueError):
            MODULE.wrap_execution(
                raw,
                workflow_run_id=123,
                workflow_head_sha="abcdef0123456789",
            )


if __name__ == "__main__":
    unittest.main()
