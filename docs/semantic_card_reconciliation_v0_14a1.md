# Semantic-card reconciliation through v0.14A1

## Why this reconciliation exists

The repository established semantic atom cards early in the atomic programme, but later compound and molecular work advanced faster than the semantic projection layer. This created a documentation/model-to-card drift: atomic cards and overlays existed, while the compound v0.1–v0.13 trajectory and v0.14A1 molecular screen were not represented as current semantic objects.

This change repairs that drift without adding scientific claims.

## Reconciled semantic surfaces

- `reschem/semantic_cards.py` supports repository-derived semantic overlays while preserving the original atom-card API.
- `reschem/entity_registry.py`, `reschem/semantic_projection.py`, `reschem/molecular_semantic_projection.py`, and `reschem/repository_cards.py` provide calculation-addressable entities, relations, deterministic lineage and registry loading.
- `semantic_cards/SEMANTIC_CARD_COVERAGE_V0_14A1.json` is the machine-readable stage ledger.
- `semantic_cards/COMPOUND_MODEL_OVERLAYS_V0_14A1.jsonl` projects v0.1–v0.13 model/gate state.
- `semantic_cards/MOLECULAR_STATE_RELAXATION_V0_14A1.jsonl` projects the v0.14A1 model and nine formula screens.
- `scripts/audit_semantic_card_coverage.py` enforces semantic coverage and epistemic separation in maintained CI.

## THEORY and web reconciliation

Semantic reconciliation is incomplete if only the Python registry is current while the formal and interactive surfaces remain stale. The current cross-surface contract is persisted in `semantic_cards/SURFACE_SYNC_CURRENT.json`.

The current THEORY layer includes:

- `THEORY/02_ATOM_FORMALISM.md` — atomic foundation plus current v0.14A1 repository checkpoint;
- `THEORY/03_SHELL_NBODY_TOPOLOGY.md` — shell/topology boundary carried through the v0.13 competing-state and v0.14A1 admission boundary;
- `THEORY/04_COMPOUND_RELATIONAL_ARCHITECTURE.md` — compound trajectory and molecular-screen admission order;
- `THEORY/05_SEMANTIC_ENTITY_GRAPH.md` — cards, relations, provenance holonomy, physical-holonomy separation and anti-drift rules.

The current web layer includes `web/semantic_card_atlas.html` and `web/semantic_cards.js`. It reads persisted repository JSON/JSONL directly instead of keeping an independent JavaScript copy of semantic truth. The atlas exposes current entity populations, model/gate coverage, the 3×3 noble-gas molecular screen, and the current epistemic boundary.

`scripts/audit_semantic_surface_sync.py` fails if semantic registry, THEORY or web no longer present the same v0.14A1 execution boundary. `compound-relations-ci` runs both semantic audits; `web-ci` also triggers when current semantic/molecular source surfaces change.

## Epistemic rules

Semantic projection is downstream of repository evidence. It may summarize or index a model/benchmark state, but may not strengthen it.

Therefore:

- TIR semantic axes remain unassigned unless an explicit, provenance-bearing mapping is supplied;
- affective labels/coordinates remain unassigned unless an explicit, provenance-bearing mapping is supplied;
- `ArBr2` remains `MISSING_EXECUTION_NOT_CHEMICAL_FAIL`;
- v0.14A1 remains a relaxation screen, not a Hessian/local-minimum admission;
- no ground-state ranking is validated by the semantic layer;
- no geometry-only 3c4e/VDW topology label is promoted by the semantic layer;
- provenance holonomy is deterministic model lineage and is not evidence of physical holonomy;
- THEORY prose and browser visualization may not promote a status beyond their named repository sources.

## Coverage gates

The semantic-card audit fails when:

1. a stage listed in the semantic coverage ledger loses its implementation, benchmark, documentation, or card;
2. H–Kr atomic semantic coverage is incomplete;
3. the molecular formula-card set differs from the frozen benchmark `expected_formulae`;
4. completed and missing molecular execution states disagree with the benchmark;
5. a semantic card silently populates TIR or affective values without provenance;
6. the v0.14A1 model card claims Hessian, ground-state, or topology promotion.

The cross-surface audit additionally fails when:

1. a semantic/THEORY/web surface named by `SURFACE_SYNC_CURRENT.json` is missing;
2. registry entity populations drift from the current deterministic counts;
3. THEORY no longer states the current v0.13/v0.14A1 boundary;
4. web no longer loads the current semantic coverage/registry/molecular records directly;
5. the current `ArBr2`, Hessian, ground-state, topology or descriptive-only survival status diverges between these surfaces.

## Nonclaim

This reconciliation is semantic/provenance/formal/visual infrastructure. It does not alter Hamiltonians, energies, relaxation seeds, benchmark values, chemical classifications, or the current scientific frontier.
