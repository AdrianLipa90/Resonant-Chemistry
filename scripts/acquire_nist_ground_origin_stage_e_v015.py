from __future__ import annotations

import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from datetime import datetime, timezone

PREREG_PATH = Path("benchmarks/ATOMIC_SUBJECTIVE_TIME_STAGE_E_GROUND_RESONANCE_HOLDOUT_PREREG_V0_15.json")
NIST_ENDPOINT = "https://physics.nist.gov/cgi-bin/ASD/lines1.pl"
SCHEMA = "RESCHEM_NIST_GROUND_ORIGIN_STAGE_E_ACQUISITION_MANIFEST_V0_15"
SPECIES = (("B", "B I"), ("C", "C I"), ("N", "N I"), ("O", "O I"), ("F", "F I"), ("Ne", "Ne I"))


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def text(self) -> str:
        return "".join(self.parts)


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def sha256_json(value: object) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def query_params(spectrum: str) -> dict[str, str]:
    # `format=3` is NIST ASD tab-delimited output. `show_wn=1` requests
    # wavenumber output explicitly. The frozen Stage-E rule requires the
    # absolute ground lower level only, hence max_low_enrg=0.
    return {
        "spectra": spectrum,
        "limits_type": "0",
        "low_w": "",
        "upp_w": "",
        "unit": "1",
        "submit": "Retrieve Data",
        "de": "0",
        "format": "3",
        "line_out": "0",
        "remove_js": "on",
        "no_spaces": "on",
        "en_unit": "0",
        "output": "0",
        "bibrefs": "1",
        "page_size": "100",
        "show_obs_wl": "1",
        "show_calc_wl": "1",
        "show_wn": "1",
        "unc_out": "1",
        "order_out": "0",
        "max_low_enrg": "0",
        "show_av": "2",
        "max_upp_enrg": "",
        "tsb_value": "0",
        "min_str": "",
        "A_out": "1",
        "intens_out": "on",
        "max_str": "",
        "allowed_out": "1",
        "forbid_out": "1",
        "min_accur": "",
        "min_intens": "",
        "conf_out": "on",
        "term_out": "on",
        "enrg_out": "on",
        "J_out": "on",
    }


def normalize_tab_output(raw: bytes) -> str:
    decoded = raw.decode("utf-8", errors="strict")
    parser = _TextExtractor()
    parser.feed(decoded)
    text = html.unescape(parser.text()).replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.splitlines()]
    # Preserve all NIST textual content, but trim purely blank prefix/suffix.
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="out/stage_e_nist_ground_origin")
    args = parser.parse_args()
    out = Path(args.output_dir)
    raw_dir = out / "raw"
    normalized_dir = out / "normalized"
    raw_dir.mkdir(parents=True, exist_ok=True)
    normalized_dir.mkdir(parents=True, exist_ok=True)

    prereg_raw = PREREG_PATH.read_bytes()
    prereg = json.loads(prereg_raw)
    if prereg.get("status") != "INDEPENDENT_NIST_GROUND_ORIGIN_LINE_HOLDOUT_PREREGISTERED_BEFORE_DATA_JOIN":
        raise SystemExit("Stage-E prereg status drift")
    if prereg.get("fit_parameters") != [] or prereg.get("calibration_parameters") != []:
        raise SystemExit("Stage-E prereg fit/calibration boundary drift")

    retrieved_at = datetime.now(timezone.utc).isoformat()
    records: list[dict[str, object]] = []
    for symbol, spectrum in SPECIES:
        params = query_params(spectrum)
        url = NIST_ENDPOINT + "?" + urlencode(params)
        req = Request(url, headers={"User-Agent": "Resonant-Chemistry-v0.15-stage-e/1.0 (NIST ASD reproducible research)"})
        with urlopen(req, timeout=60) as response:
            status = getattr(response, "status", 200)
            if status != 200:
                raise SystemExit(f"NIST HTTP status for {spectrum}: {status}")
            raw = response.read()
            content_type = response.headers.get("Content-Type", "")
        if not raw:
            raise SystemExit(f"empty NIST response: {spectrum}")
        normalized = normalize_tab_output(raw)
        if "Error Message" in normalized or "Please select" in normalized:
            raise SystemExit(f"NIST returned error output for {spectrum}")
        if "Ei" not in normalized or "Ek" not in normalized:
            raise SystemExit(f"NIST classified-energy columns missing for {spectrum}")

        stem = symbol.lower()
        raw_path = raw_dir / f"{stem}_i_nist_asd_response.bin"
        normalized_path = normalized_dir / f"{stem}_i_nist_asd.tsv"
        raw_path.write_bytes(raw)
        normalized_path.write_text(normalized, "utf-8")
        tab_lines = [line for line in normalized.splitlines() if "\t" in line]
        header_preview = tab_lines[0] if tab_lines else ""
        records.append({
            "symbol": symbol,
            "spectrum": spectrum,
            "endpoint": NIST_ENDPOINT,
            "query_parameters": params,
            "content_type": content_type,
            "raw_path": str(raw_path),
            "raw_sha256": sha256_bytes(raw),
            "raw_size_bytes": len(raw),
            "normalized_path": str(normalized_path),
            "normalized_sha256": sha256_bytes(normalized.encode("utf-8")),
            "normalized_size_bytes": len(normalized.encode("utf-8")),
            "tab_line_count": len(tab_lines),
            "header_preview": header_preview,
        })

    body: dict[str, object] = {
        "schema": SCHEMA,
        "version": "0.15.0",
        "status": "NIST_STAGE_E_RAW_GROUND_ORIGIN_RESPONSES_ARCHIVED_BEFORE_JOIN",
        "retrieved_at_utc": retrieved_at,
        "preregister_source": str(PREREG_PATH),
        "preregister_raw_sha256": sha256_bytes(prereg_raw),
        "nist_authority": "NIST Atomic Spectra Database",
        "nist_endpoint": NIST_ENDPOINT,
        "species_count": len(records),
        "records": records,
        "selection_performed": False,
        "model_data_join_performed": False,
        "fit_parameters_added": [],
        "calibration_parameters_added": [],
        "interpretation": "NONE_IN_ACQUISITION_MANIFEST",
        "canon_allowed": False,
    }
    manifest = {**body, "manifest_sha256": sha256_json(body)}
    manifest_path = out / "NIST_GROUND_ORIGIN_STAGE_E_ACQUISITION_MANIFEST_V0_15.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", "utf-8")
    print(json.dumps({
        "status": manifest["status"],
        "manifest_sha256": manifest["manifest_sha256"],
        "species": [
            {
                "symbol": r["symbol"],
                "raw_sha256": r["raw_sha256"],
                "tab_line_count": r["tab_line_count"],
                "header_preview": r["header_preview"],
            }
            for r in records
        ],
        "output_dir": str(out),
    }, indent=2))


if __name__ == "__main__":
    main()
