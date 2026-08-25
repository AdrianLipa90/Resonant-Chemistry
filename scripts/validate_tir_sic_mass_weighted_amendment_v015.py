#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_SCHEMA = "RESCHEM_TIR_SIC_MASS_WEIGHTED_LEDGER_V0_15"
EXPECTED_STATUS = "PRIMARY_TIR_SIC_MASS_WEIGHTED_FEATURES_FROZEN_BEFORE_SPECTRAL_JOIN"
EXPECTED_CARDS = (
    "ATOM:B:11:q+0",
    "ATOM:C:12:q+0",
    "ATOM:N:14:q+0",
    "ATOM:O:16:q+0",
    "ATOM:F:19:q+0",
    "ATOM:Ne:20:q+0",
)


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _sha256_json(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _verify_hash(record: dict, field: str) -> None:
    expected = record.get(field)
    if not isinstance(expected, str) or len(expected) != 64:
        raise ValueError(f"missing or malformed {field}")
    body = dict(record)
    body.pop(field)
    observed = _sha256_json(body)
    if observed != expected:
        raise ValueError(f"{field} mismatch: {observed} != {expected}")


def validate(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != EXPECTED_SCHEMA:
        raise ValueError("TIR-SIC mass-weighted schema mismatch")
    if payload.get("status") != EXPECTED_STATUS:
        raise ValueError("TIR-SIC mass-weighted status mismatch")
    if payload.get("row_count") != 6:
        raise ValueError("TIR-SIC mass-weighted row count mismatch")
    if payload.get("spectral_join") != {"status": "WITHHELD_FOR_BLIND_COMPARISON", "accepted_observed_fields": []}:
        raise ValueError("TIR-SIC mass-weighted spectral boundary drift")
    if payload.get("epistemic_operator") != "CHYBA" or payload.get("canon_allowed") is not False:
        raise ValueError("TIR-SIC mass-weighted epistemic boundary drift")

    rows = payload.get("rows")
    if not isinstance(rows, list) or tuple(row.get("atom_card_id") for row in rows) != EXPECTED_CARDS:
        raise ValueError("TIR-SIC mass-weighted cohort/order drift")

    coupling = {}
    for row in rows:
        _verify_hash(row, "row_sha256")
        card_id = row["atom_card_id"]
        if row.get("spectral_join") != "WITHHELD_FOR_BLIND_COMPARISON":
            raise ValueError(f"row spectral boundary drift: {card_id}")
        if row.get("epistemic_operator") != "CHYBA" or row.get("canon_allowed") is not False:
            raise ValueError(f"row epistemic boundary drift: {card_id}")
        a = row.get("A")
        mass = row.get("semantic_mass")
        mu = row.get("semantic_mass_per_nucleon")
        i_sic = row.get("sic_information_nats")
        eta = row.get("sic_information_ratio_to_nucleons")
        chi = row.get("radial_nuclear_exposure")
        e_sic = row.get("primary_tir_sic_eclipse_coupling")
        for name, value in (("A", a), ("semantic_mass", mass), ("mu", mu), ("I_SIC", i_sic), ("eta", eta), ("chi", chi), ("E_SIC", e_sic)):
            if not isinstance(value, (int, float)):
                raise ValueError(f"{name} missing/non-numeric: {card_id}")
        if a <= 0 or mass < 0.0 or i_sic < 0.0 or chi < 0.0 or e_sic < 0.0:
            raise ValueError(f"negative/nonpositive component drift: {card_id}")
        if abs(float(mu) - float(mass) / float(a)) > 1.0e-15:
            raise ValueError(f"semantic mass per nucleon parity drift: {card_id}")
        if abs(float(e_sic) - float(mu) * float(eta) * float(chi)) > 1.0e-15:
            raise ValueError(f"TIR-SIC coupling parity drift: {card_id}")

        phase = row.get("axis_resolved_phase")
        if not isinstance(phase, dict) or phase.get("selection_status") != "ALL_PREREGISTERED_AXES_PRESERVED":
            raise ValueError(f"axis selection drift: {card_id}")
        if set(phase) != {"x", "y", "z", "selection_status"}:
            raise ValueError(f"axis set drift: {card_id}")
        for axis in ("x", "y", "z"):
            axis_row = phase[axis]
            order = axis_row.get("dominant_harmonic_order")
            strength = axis_row.get("dominant_harmonic_strength")
            if isinstance(order, bool) or not isinstance(order, int) or order < 0:
                raise ValueError(f"invalid harmonic order {axis}: {card_id}")
            if not isinstance(strength, (int, float)) or strength < 0.0:
                raise ValueError(f"invalid harmonic strength {axis}: {card_id}")
        coupling[card_id] = float(e_sic)

    _verify_hash(payload, "ledger_sha256")
    text = path.read_text(encoding="utf-8").lower()
    for forbidden in ("observed_wavelength", "observed_wavenumber", "oscillator_strength", "line_intensity"):
        if forbidden in text:
            raise ValueError(f"forbidden spectral field present: {forbidden}")

    return {
        "status": "PASS_PRIMARY_TIR_SIC_MASS_WEIGHTED_LEDGER",
        "row_count": 6,
        "ledger_sha256": payload["ledger_sha256"],
        "raw_file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "coupling_by_card": coupling,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate post-A1 primary TIR-SIC mass-weighted v0.15 ledger")
    parser.add_argument("ledger", type=Path)
    args = parser.parse_args()
    print(json.dumps(validate(args.ledger), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
