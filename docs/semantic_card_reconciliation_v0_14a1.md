# Semantic-card reconciliation through v0.14A1

## Why this reconciliation exists

The repository established semantic atom cards early in the atomic programme, but later compound and molecular work advanced faster than the semantic projection layer. This created a documentation/model-to-card drift: atomic cards and overlays existed, while the compound v0.1–v0.13 trajectory and v0.14A1 molecular screen were not represented as current semantic objects.

This change repairs that drift without adding scientific claims.

## Reconciled surfaces

- `reschem/semantic_cards.py` now supports repository-derived semantic overlays while preserving the original atom-card API.
- `semantic_cards/SEMANTIC_CARD_COVERAGE_V0_14A1.json` is the machine-readable stage ledger.
- `semantic_cards/COMPOUND_MODEL_OVERLAYS_V0_14A1.jsonl` projects v0.1–v0.13 model/gate state.
- `semantic_cards/MOLECULAR_STATE_RELAXATION_V0_14A1.jsonl` projects the v0.14A1 model and nine formula screens.
- `scripts/audit_semantic_card_coverage.py` enforces coverage and epistemic separation in maintained CI.

## Epistemic rules

Semantic projection is downstream of repository evidence. It may summarize or index a model/benchmark state, but may not strengthen it.

Therefore:

- TIR semantic axes remain unassigned unless an explicit, provenance-bearing mapping is supplied;
- affective labels/coordinates remain unassigned unless an explicit, provenance-bearing mapping is supplied;
- `ArBr2` remains `MISSING_EXECUTION_NOT_CHEMICAL_FAIL`;
- v0.14A1 remains a relaxation screen, not a Hessian/local-minimum admission;
- no ground-state ranking is validated by the semantic layer;
- no geometry-only 3c4e/VDW topology label is promoted by the semantic layer.

## Coverage gate

The audit fails when:

1. a stage listed in the semantic coverage ledger loses its implementation, benchmark, documentation, or card;
2. H–Kr atomic semantic coverage is incomplete;
3. the molecular formula-card set differs from the frozen benchmark `expected_formulae`;
4. completed and missing molecular execution states disagree with the benchmark;
5. a semantic card silently populates TIR or affective values without provenance;
6. the v0.14A1 model card claims Hessian, ground-state, or topology promotion.

The maintained `compound-relations-ci` runs this audit for every pull request targeting `main` and every push to `main`.

## Nonclaim

This reconciliation is semantic/provenance infrastructure. It does not alter Hamiltonians, energies, relaxation seeds, benchmark values, chemical classifications, or the current scientific frontier.
