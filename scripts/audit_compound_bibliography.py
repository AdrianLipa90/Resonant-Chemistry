"""Fail closed when compound-track DOI provenance is missing from the live bibliography."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BIB_ROOT = ROOT / "monograph" / "bibliography"

# Scope is intentionally the active compound-relation trajectory first.  The
# audit can later be expanded to the entire historical textbook bibliography.
PREFIXES = (
    "COMPOUND_",
    "COORDINATION_",
    "HYPERRELATION_",
    "POSTBLIND_",
    "RELATION_GRAPH_",
    "PARITY_",
    "LIGAND_FAMILY_",
    "ENERGETIC_",
    "CLOSED_SHELL_",
    "ELECTRONIC_TOPOLOGY_",
)
DOC_TOKENS = (
    "compound",
    "coordination",
    "hyperrelation",
    "postblind",
    "relation_graph",
    "parity",
    "heldout",
    "energetic",
    "closed_shell",
    "electronic_topology",
)

DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", re.IGNORECASE)
KEY_RE = re.compile(r"@\w+\{([^,\s]+)")
BIB_DOI_RE = re.compile(r"\bdoi\s*=\s*\{([^}]+)\}", re.IGNORECASE)


def normalize_doi(value: str) -> str:
    return value.strip().rstrip(".,;:)").lower()


def bibliography_files() -> list[Path]:
    if not BIB_ROOT.is_dir():
        raise SystemExit(f"missing bibliography directory: {BIB_ROOT.relative_to(ROOT)}")
    files = sorted(BIB_ROOT.glob("*.bib"))
    if not files:
        raise SystemExit(f"no .bib files under {BIB_ROOT.relative_to(ROOT)}")
    return files


def active_source_files() -> list[Path]:
    files: list[Path] = []
    benchmark_root = ROOT / "benchmarks"
    if benchmark_root.is_dir():
        for path in sorted(benchmark_root.glob("*.json")):
            if path.name.startswith(PREFIXES):
                files.append(path)

    docs_root = ROOT / "docs"
    if docs_root.is_dir():
        for path in sorted(docs_root.glob("*.md")):
            lowered = path.stem.lower()
            if any(token in lowered for token in DOC_TOKENS):
                files.append(path)
    return files


def main() -> int:
    bib_files = bibliography_files()
    combined_bib = "\n".join(path.read_text(encoding="utf-8") for path in bib_files)
    keys = KEY_RE.findall(combined_bib)
    bib_dois = [normalize_doi(x) for x in BIB_DOI_RE.findall(combined_bib)]

    duplicate_keys = sorted({key for key in keys if keys.count(key) > 1})
    duplicate_dois = sorted({doi for doi in bib_dois if bib_dois.count(doi) > 1})

    source_dois: dict[str, set[str]] = defaultdict(set)
    for path in active_source_files():
        text = path.read_text(encoding="utf-8")
        for raw in DOI_RE.findall(text):
            source_dois[normalize_doi(raw)].add(str(path.relative_to(ROOT)))

    bib_set = set(bib_dois)
    missing = {doi: sorted(paths) for doi, paths in source_dois.items() if doi not in bib_set}

    main_tex = (ROOT / "monograph" / "main.tex").read_text(encoding="utf-8")
    expected_stems = [f"bibliography/{path.stem}" for path in bib_files]
    unwired_bibliographies = [stem for stem in expected_stems if stem not in main_tex]

    report = {
        "active_source_files": len(active_source_files()),
        "bibliography_files": [str(path.relative_to(ROOT)) for path in bib_files],
        "bibliography_entries": len(keys),
        "bibliography_dois": len(bib_set),
        "referenced_compound_dois": len(source_dois),
        "missing_dois": missing,
        "duplicate_keys": duplicate_keys,
        "duplicate_dois": duplicate_dois,
        "unwired_bibliographies": unwired_bibliographies,
    }
    print(report)

    if missing or duplicate_keys or duplicate_dois or unwired_bibliographies:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
