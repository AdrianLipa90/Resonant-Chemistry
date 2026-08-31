#!/usr/bin/env python3
"""Validate the Resonant Chemistry nucleon-boundary structural/provenance contract.

This gate validates typed interface structure, dependency-export identity, and immutable
scientific-source provenance. It emits a structural/provenance receipt; physical
observable validation belongs to the subsequent nucleon-packet and deuteron gates.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = Path("THEORY/01_NUCLEON_BOUNDARY_V0_1.md")
EXPORT = Path("DEPENDENCY_EXPORT.json")
RECEIPT = Path("build/NUCLEON_BOUNDARY_V0_1_VALIDATION.json")

EXPECTED_REPOSITORY = "AdrianLipa90/Resonant-Chemistry"
EXPECTED_CLAIMS = {
    "RC.NUCLEON_BOUNDARY": "SOURCE_BOUND_EFFECTIVE_INPUT_CONTRACT",
    "RC.ATOM_FORMALISM": "CANDIDATE_FOUNDATION",
}
EXPECTED_EDGE = (
    "RC.NUCLEON_BOUNDARY",
    "RC.ATOM_FORMALISM",
    "CANONICAL_FRONTIER",
)
REQUIRED_MARKERS = (
    "SOURCE_BOUND_EFFECTIVE_INPUT_CONTRACT",
    r"\mathfrak N_a",
    r"\mathcal H_N",
    r"H_{NN}=T_{\rm rel}+V_{NN}+H_{\rm corr}",
    r"p+n\rightarrow{}^2\mathrm H",
    r"J^P=1^+",
    "EXTERNAL_EMPIRICAL",
    "ENDOGENOUS_DERIVED",
    r"\mathfrak C_A=(Z,N;M_A,J_A^{P_A},\mu_A,Q_A,\Pi_A)",
    "Every parameter at this boundary belongs to the interaction model",
)


def fail(message: str, checks: list[dict[str, object]]) -> None:
    checks.append({"check": message, "status": "FAIL"})
    emit("FAIL", checks)
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def emit(status: str, checks: list[dict[str, object]]) -> None:
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    receipt = {
        "schema": "RC_NUCLEON_BOUNDARY_VALIDATION_V0_1",
        "gate": "NUCLEON_BOUNDARY_STRUCTURAL_PROVENANCE",
        "status": "STRUCTURAL_PROVENANCE_PASS" if status == "PASS" else "FAIL",
        "physical_validation_status": "PENDING_NUCLEON_PACKET_AND_DEUTERON_GATES",
        "document": str(DOC),
        "dependency_export": str(EXPORT),
        "checks": checks,
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


def git_file_at(commit: str, path: Path) -> str:
    proc = subprocess.run(
        ["git", "show", f"{commit}:{path.as_posix()}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git show failed")
    return proc.stdout


def main() -> int:
    checks: list[dict[str, object]] = []
    doc_path = ROOT / DOC
    export_path = ROOT / EXPORT
    if not doc_path.is_file():
        fail(f"missing {DOC}", checks)
    if not export_path.is_file():
        fail(f"missing {EXPORT}", checks)

    text = doc_path.read_text(encoding="utf-8")
    missing = [marker for marker in REQUIRED_MARKERS if marker not in text]
    if missing:
        fail(f"missing contract markers: {missing}", checks)
    checks.append({"check": "typed_contract_markers", "status": "PASS", "count": len(REQUIRED_MARKERS)})

    try:
        export = json.loads(export_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"dependency export JSON: {exc}", checks)

    if export.get("schema") != "FPDG_DEPENDENCY_EXPORT_V0_1":
        fail("dependency export schema", checks)
    if export.get("repository_id") != "RC" or export.get("repository") != EXPECTED_REPOSITORY:
        fail("dependency export repository identity", checks)

    source_commit = export.get("source_commit")
    if not isinstance(source_commit, str) or len(source_commit) != 40:
        fail("dependency export source_commit", checks)

    claims = export.get("claims")
    if not isinstance(claims, list):
        fail("dependency export claims list", checks)
    claim_map = {
        row.get("claim_id"): row
        for row in claims
        if isinstance(row, dict) and isinstance(row.get("claim_id"), str)
    }
    if set(claim_map) != set(EXPECTED_CLAIMS):
        fail(f"claim identity set: {sorted(claim_map)}", checks)
    for claim_id, expected_status in EXPECTED_CLAIMS.items():
        if claim_map[claim_id].get("status") != expected_status:
            fail(f"claim status {claim_id}", checks)

    nucleon_claim = claim_map["RC.NUCLEON_BOUNDARY"]
    if nucleon_claim.get("source_path") != DOC.as_posix():
        fail("nucleon-boundary source_path", checks)
    if nucleon_claim.get("exact_head") != source_commit:
        fail("nucleon-boundary exact_head/source_commit identity", checks)

    edges = export.get("local_edges", [])
    edge_set = {
        (row.get("from"), row.get("to"), row.get("authority"))
        for row in edges
        if isinstance(row, dict)
    }
    if EXPECTED_EDGE not in edge_set:
        fail("nucleon-boundary -> atom canonical frontier", checks)
    checks.append({"check": "dependency_export_surface", "status": "PASS"})

    try:
        source_text = git_file_at(source_commit, DOC)
    except RuntimeError as exc:
        fail(f"scientific source commit unavailable: {exc}", checks)
    if source_text != text:
        fail("current nucleon contract differs from source_commit snapshot", checks)
    checks.append({
        "check": "immutable_scientific_source_snapshot",
        "status": "PASS",
        "source_commit": source_commit,
    })

    emit("PASS", checks)
    print(
        "PASS: nucleon boundary structural/provenance gate; "
        f"source_commit={source_commit}; physical validation pending"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
