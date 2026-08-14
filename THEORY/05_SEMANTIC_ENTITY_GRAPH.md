# 05 — Semantic Entity Graph

**Status:** implemented calculation/provenance layer; downstream of scientific evidence.

## 1. Card meaning

A semantic card is an addressable computational object. It may carry identity, model/control properties, state invariants, source artifacts, relations, provenance lineage and explicit epistemic status.

A card does **not** acquire physical authority merely because it exists in the registry.

The current card surface separates:

1. canonical atomic base cards;
2. nondestructive atomic evidence overlays;
3. persisted model/gate projections;
4. deterministic generated compound candidates;
5. deterministic generated relational-state candidates;
6. molecular-screen cards derived from machine-readable execution evidence.

## 2. Current populations

At checkpoint v0.14A1 the maintained registry includes:

- 36 neutral atomic base cards H→Kr;
- 231 generated v0.1 compound-relation candidate cards;
- 27 generated v0.13 relational-state candidate cards;
- 10 v0.14A1 molecular cards: one screen-model card plus nine formula cards;
- persisted model/gate projections spanning the compound trajectory through v0.14A1.

High-cardinality cards are regenerated deterministically from scientific generators rather than manually copied into hundreds of independent files.

## 3. Relations

A relation is explicit data with a source card, predicate, target and provenance. A target is either an exact card ID or a deterministic selector.

Examples include:

- `HAS_ATOMIC_COMPONENT`;
- `HAS_CENTRE`;
- `HAS_LIGAND`;
- `DERIVED_BY_MODEL`;
- `SCREENED_STATE_CANDIDATE`;
- `LOWEST_SUCCESSFUL_SCREENING_WITHIN_FROZEN_STARTS`.

These are repository/calculation relations. They must not be silently identified with a physical/TIR `W_ij` operator.

## 4. Provenance holonomy vs physical holonomy

Generated entity cards carry deterministic lineage metadata:

```text
parents + generating operation + identity -> lineage SHA-256
```

This is called `provenance_holonomy`: it records the path by which an entity arose in the model graph.

It is **not** evidence of physical holonomy.

`physical_holonomy` remains `NOT_COMPUTED` (or an explicitly candidate state with named source artifacts) unless winding, phase, connection or topology observables have actually been evaluated.

Therefore the invariant is

```text
provenance_holonomy != physical_holonomy
```

## 5. Semantic/affective separation

Control evidence is never rewritten by interpretive semantics.

Unless an explicit provenance-bearing mapping has been introduced and tested:

- `tir.semantic_axes.values = {}`;
- TIR semantics remain `OPEN` / `CANDIDATE_UNASSIGNED`;
- affective labels and coordinates remain empty;
- affective status remains `RESERVED_UNASSIGNED`.

This prevents reverse fitting of physical results into desired semantic meanings.

## 6. Molecular state at v0.14A1

The molecular semantic layer must reproduce the machine-readable execution boundary exactly:

- 8/9 formulae completed;
- 40/45 frozen starts completed;
- `ArBr2 = MISSING_EXECUTION_NOT_CHEMICAL_FAIL`;
- Hessian admission `NOT_RUN`;
- ground-state ranking `NOT_VALIDATED`;
- geometry-only topology assignment `NOT_PROMOTED`.

The v0.13 competing states remain unranked until physical admission. The activated-survival matrix is descriptive only and cannot create a semantic threshold or topology label.

## 7. Anti-drift invariant

A new model, benchmark, addressable entity, or scientific-status transition is incomplete until the semantic projection and visible surfaces are reconciled in the same development cycle.

The maintained anti-drift path is:

```text
model / benchmark / receipt
  -> semantic projection / registry
  -> THEORY
  -> documentation / textbook
  -> web surface
  -> CI coverage audit
```

`scripts/audit_semantic_card_coverage.py` enforces the repository-facing part of this invariant. `semantic_cards/SURFACE_SYNC_CURRENT.json` records the current cross-surface checkpoint.
