# Semantic cards

`semantic_cards/` is a first-class derived projection of the repository Source of Truth.

## Invariant

Every newly introduced atomic species, compound relation model, coordination/activation/topology model, compound state ensemble, or molecular-state screening gate must receive a semantic card or overlay in the same development cycle.

Cards preserve epistemic separation:

- physical/control fields derive only from named repository models, benchmarks, receipts, or preregistrations;
- TIR semantic axes remain `CANDIDATE_UNASSIGNED` unless an explicit mapping with provenance is supplied;
- affective mappings remain `RESERVED_UNASSIGNED` unless an explicit mapping with provenance is supplied;
- missing execution is never converted to chemical failure;
- screening results are never promoted to harmonic minima, ground-state rankings, or topology assignments without their own gates.

## Current coverage

`SEMANTIC_CARD_COVERAGE_V0_14A1.json` reconciles the model/gate trajectory from compound v0.1 through molecular v0.14A1. `MOLECULAR_STATE_RELAXATION_V0_14A1.jsonl` projects the current nine-formula molecular screen, preserving eight completed formulae and `ArBr2` as `MISSING_EXECUTION_NOT_CHEMICAL_FAIL`.

`scripts/audit_semantic_card_coverage.py` is the CI enforcement surface. New model/benchmark surfaces must be added to coverage before the maintained compound/molecular CI can pass.
