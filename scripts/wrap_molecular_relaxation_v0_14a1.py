"""Wrap the raw v0.14A Actions aggregate with durable v0.14A1 provenance.

This script does not recompute, filter, rank, cluster, or relabel molecular
results. It only validates the raw aggregate schema and attaches immutable
execution/provenance metadata plus a SHA-256 digest of the raw artifact bytes.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

RAW_SCHEMA = "RESCHEM_MOLECULAR_STATE_RELAXATION_V0_14A"
WRAPPED_SCHEMA = "RESCHEM_MOLECULAR_STATE_RELAXATION_EXECUTION_V0_14A1"
PARENT_PREREG = "benchmarks/MOLECULAR_STATE_RELAXATION_PREREG_V0_14A.json"
AMENDMENT = "benchmarks/MOLECULAR_STATE_RELAXATION_AMENDMENT_V0_14A1.json"


def wrap_execution(
    raw_bytes: bytes,
    *,
    workflow_run_id: int,
    workflow_head_sha: str,
) -> dict:
    raw = json.loads(raw_bytes.decode("utf-8"))
    if raw.get("schema") != RAW_SCHEMA:
        raise ValueError(f"unexpected raw schema: {raw.get('schema')!r}")
    if raw.get("formula_count") != 9:
        raise ValueError(f"expected 9 formulae, got {raw.get('formula_count')!r}")
    if raw.get("relaxation_start_count") != 45:
        raise ValueError(
            f"expected 45 relaxation starts, got {raw.get('relaxation_start_count')!r}"
        )
    formulae = raw.get("formulae")
    if not isinstance(formulae, list) or len(formulae) != 9:
        raise ValueError("raw aggregate must contain exactly nine formula receipts")
    if len({item.get("formula") for item in formulae}) != 9:
        raise ValueError("raw aggregate contains duplicate or missing formula identities")
    if not workflow_head_sha or len(workflow_head_sha) < 7:
        raise ValueError("workflow_head_sha is required")

    return {
        "schema": WRAPPED_SCHEMA,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "RAW_EXECUTION_WRAPPED_WITH_AMENDMENT_PROVENANCE_NO_REINTERPRETATION",
        "parent_preregistration": PARENT_PREREG,
        "numerical_amendment": AMENDMENT,
        "workflow": {
            "run_id": int(workflow_run_id),
            "head_sha": workflow_head_sha,
            "raw_artifact_schema": RAW_SCHEMA,
        },
        "raw_artifact_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "raw_summary": {
            "formula_count": raw.get("formula_count"),
            "relaxation_start_count": raw.get("relaxation_start_count"),
            "successful_relaxation_count": raw.get("successful_relaxation_count"),
            "status_counts": raw.get("status_counts"),
        },
        "combined_execution": raw,
        "nonclaim": "wrapper preserves raw v0.14A execution and provenance only; it performs no Hessian admission, topology assignment, clustering, chemical ranking rewrite, or candidate rescue",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--combined", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--workflow-run-id", required=True, type=int)
    parser.add_argument("--workflow-head-sha", required=True)
    args = parser.parse_args()

    raw_bytes = args.combined.read_bytes()
    wrapped = wrap_execution(
        raw_bytes,
        workflow_run_id=args.workflow_run_id,
        workflow_head_sha=args.workflow_head_sha,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(wrapped, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "status": wrapped["status"],
        "raw_artifact_sha256": wrapped["raw_artifact_sha256"],
        "raw_summary": wrapped["raw_summary"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
