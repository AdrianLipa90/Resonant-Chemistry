from __future__ import annotations

import argparse
import csv
from decimal import Decimal, InvalidOperation
import hashlib
import io
import json
import math
from pathlib import Path

SCHEMA = "RESCHEM_NIST_GROUND_ORIGIN_STAGE_E_SELECTED_OBSERVED_LEDGER_V0_15"
PREREG_PATH = Path("benchmarks/ATOMIC_SUBJECTIVE_TIME_STAGE_E_GROUND_RESONANCE_HOLDOUT_PREREG_V0_15.json")
ACQ_ROOT = Path("benchmarks/stage_e_nist_ground_origin")
MANIFEST_PATH = ACQ_ROOT / "NIST_GROUND_ORIGIN_STAGE_E_ACQUISITION_MANIFEST_V0_15.json"
SPECIES = (("B", "b_i_nist_asd.tsv"), ("C", "c_i_nist_asd.tsv"), ("N", "n_i_nist_asd.tsv"), ("O", "o_i_nist_asd.tsv"), ("F", "f_i_nist_asd.tsv"), ("Ne", "ne_i_nist_asd.tsv"))


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_json(value: object) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def decimal_field(row: dict[str, str], field: str) -> Decimal:
    raw = row.get(field)
    if raw is None:
        raise ValueError(f"missing required NIST field: {field}")
    value = raw.strip().strip('"')
    if not value:
        raise ValueError(f"empty required NIST field: {field}")
    try:
        out = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"non-decimal NIST field {field}: {raw!r}") from exc
    if not out.is_finite():
        raise ValueError(f"non-finite NIST field {field}: {raw!r}")
    return out


def select_from_tsv(raw: bytes) -> tuple[dict[str, str], int, int]:
    text = raw.decode("utf-8", errors="strict")
    reader = csv.DictReader(io.StringIO(text), delimiter="\t")
    required = {"wn(cm-1)", "Ei(cm-1)", "Ek(cm-1)"}
    if reader.fieldnames is None or not required.issubset(set(reader.fieldnames)):
        raise SystemExit(f"required NIST fields missing: {reader.fieldnames}")
    candidates: list[tuple[Decimal, str, dict[str, str]]] = []
    parsed_rows = 0
    for row in reader:
        parsed_rows += 1
        try:
            ei = decimal_field(row, "Ei(cm-1)")
            ek = decimal_field(row, "Ek(cm-1)")
            wn = decimal_field(row, "wn(cm-1)")
        except ValueError:
            continue
        if ei != Decimal("0"):
            continue
        if ek <= 0 or wn <= 0:
            continue
        canonical = canonical_json(row)
        candidates.append((wn, canonical, row))
    if not candidates:
        raise SystemExit("no NIST row satisfies frozen Stage-E ground-origin rule")
    candidates.sort(key=lambda item: (item[0], item[1]))
    return candidates[0][2], parsed_rows, len(candidates)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="out/NIST_GROUND_ORIGIN_STAGE_E_SELECTED_OBSERVED_LEDGER_V0_15.json")
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    prereg_raw = PREREG_PATH.read_bytes()
    prereg = json.loads(prereg_raw)
    manifest_raw = MANIFEST_PATH.read_bytes()
    manifest = json.loads(manifest_raw)
    if prereg.get("status") != "INDEPENDENT_NIST_GROUND_ORIGIN_LINE_HOLDOUT_PREREGISTERED_BEFORE_DATA_JOIN":
        raise SystemExit("Stage-E prereg status drift")
    if manifest.get("status") != "NIST_STAGE_E_RAW_GROUND_ORIGIN_RESPONSES_ARCHIVED_BEFORE_JOIN":
        raise SystemExit("Stage-E acquisition manifest status drift")
    if manifest.get("selection_performed") is not False or manifest.get("model_data_join_performed") is not False:
        raise SystemExit("acquisition boundary drift")

    manifest_by_symbol = {r["symbol"]: r for r in manifest["records"]}
    rows: list[dict[str, object]] = []
    for symbol, filename in SPECIES:
        path = ACQ_ROOT / "normalized" / filename
        raw = path.read_bytes()
        rec = manifest_by_symbol[symbol]
        if sha256_bytes(raw) != rec["normalized_sha256"]:
            raise SystemExit(f"normalized NIST SHA drift before selection: {symbol}")
        selected, parsed_count, candidate_count = select_from_tsv(raw)
        wn = decimal_field(selected, "wn(cm-1)")
        ei = decimal_field(selected, "Ei(cm-1)")
        ek = decimal_field(selected, "Ek(cm-1)")
        row_body: dict[str, object] = {
            "symbol": symbol,
            "selection_rule": "MIN_POSITIVE_WAVENUMBER_AMONG_EXACT_EI_ZERO_FINITE_POSITIVE_EK_AND_WN",
            "source_normalized_path": str(path),
            "source_normalized_sha256": sha256_bytes(raw),
            "parsed_row_count": parsed_count,
            "eligible_candidate_count": candidate_count,
            "selected_wavenumber_cm_inverse": float(wn),
            "selected_lower_energy_cm_inverse": float(ei),
            "selected_upper_energy_cm_inverse": float(ek),
            "selected_record": selected,
            "selected_record_canonical_json": canonical_json(selected),
            "tie_break": "LEXICOGRAPHIC_CANONICAL_JSON_AFTER_MIN_WAVENUMBER",
            "manual_selection": False,
        }
        rows.append({**row_body, "row_sha256": sha256_json(row_body)})

    body: dict[str, object] = {
        "schema": SCHEMA,
        "version": "0.15.0",
        "status": "STAGE_E_OBSERVED_GROUND_ORIGIN_LINES_SELECTED_BY_PREREGISTERED_RULE",
        "sources": {
            str(PREREG_PATH): sha256_bytes(prereg_raw),
            str(MANIFEST_PATH): sha256_bytes(manifest_raw),
        },
        "acquisition_manifest_sha256": manifest["manifest_sha256"],
        "species_count": len(rows),
        "selection_performed": True,
        "selection_automatic": True,
        "model_data_join_performed": False,
        "model_parameters_changed": False,
        "fit_parameters_added": [],
        "calibration_parameters_added": [],
        "rows": rows,
        "interpretation": "NONE_IN_OBSERVED_SELECTION_LEDGER",
        "canon_allowed": False,
    }
    ledger = {**body, "ledger_sha256": sha256_json(body)}
    output.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", "utf-8")
    print(json.dumps({
        "status": ledger["status"],
        "ledger_sha256": ledger["ledger_sha256"],
        "selected": {r["symbol"]: r["selected_wavenumber_cm_inverse"] for r in rows},
        "output": str(output),
    }, indent=2))


if __name__ == "__main__":
    main()
