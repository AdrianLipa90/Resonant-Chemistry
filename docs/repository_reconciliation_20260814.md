# Repository reconciliation — 2026-08-14

Status: **DOCUMENTATION / CI / MANUSCRIPT / PACKAGING RECONCILIATION; NO SCIENTIFIC MODEL OR NUMERICAL RESULT CHANGED**

## Scope

This reconciliation started from repository `main` commit:

`346fd8790846d776cbb826a540e6a27e20b653aa`

Working branch:

`docs/reconcile-v0.14a1`

Draft validation PR: `#7`.

The purpose is to remove drift between already-merged repository evidence and the surfaces that describe, package, or validate it. The reconciliation does not alter the physical Hamiltonians, compound relation algorithms, v0.13 state generator, v0.14A/A1 molecular method, frozen seed geometries, benchmark numerical values, or scientific promotion state.

## Drift detected

The pre-reconciliation `main` state contained several stale surfaces:

1. `README.md` still presented an older shell-N-body working branch and pre-v0.14 frontier.
2. `STATUS.md` still described `compound-relations-v0.3` as the working checkpoint and stated that `main` was not modified, despite v0.14A1 evidence already being merged.
3. `docs/molecular_state_relaxation_v0_14a.md` still ended at backend-receipt-pending state even though the A1 smoke, dimer prepass, and partial 8/9 formula execution receipts existed.
4. The manuscript molecular chapter still described H2+ as the first admissible molecular implementation target and did not contain the v0.13 competing-state ensemble or v0.14A/A1 relaxation evidence.
5. Manuscript appendices A-D did not index the v0.13/v0.14 code, receipts, partial-result semantics, rerun provenance, or current open molecular gate.
6. Chapter 21 did not state the current repository-authority contract (`main` = SoT; Library/NOEMA = mirror/recovery/provenance) or the PhaseNav command/gate/backend-adapter boundary.
7. `monograph/main.tex` compiled correctly but its title/status paragraph predated the v0.14A1 merged evidence.
8. Maintained CI workflows were attached to historical research branches instead of `main`/pull requests targeting `main`.
9. Versioned experiment workflows v0.11/v0.12/v0.14 still had automatic push triggers on completed historical branches even though their correct role is frozen/manual replay.
10. The `docs/` directory had no current index distinguishing active trajectory notes from historical/candidate notes and maintained CI from replay workflows.
11. `pyproject.toml` disagreed with the runtime/CI dependency contract: it declared only `numpy>=2.0` while the repository requirements and code also require SciPy. The frozen v0.14 molecular backend was not represented as an explicit optional package extra.

## Reconciled scientific state

The documentation now records the already-merged v0.14A1 state without promotion:

- v0.13: nine closed-shell XY2 compositions expanded to 27 unranked competing relational-state candidates;
- v0.14A: common conventional B97M-V/VV10/def2-TZVPD relaxation screen;
- v0.14A1: globally recorded NWChem-pruning amendment after SG-1 heavy-atom smoke failure and before screening output;
- amended backend smoke: recorded PASS;
- F2/Cl2/Br2 dimer prepass: recorded;
- durable first-attempt molecular evidence: 8/9 formulae, 40/45 starts;
- ArBr2: `MISSING_EXECUTION`, not a chemical negative;
- no Hessian/local-minimum admission;
- no validated ground-state ranking;
- no geometry-only 3c4e/VDW topology label;
- no PhaseNav/TIR/affective correction to conventional atomic or molecular energies.

The next molecular gate remains completion of the missing ArBr2 execution under the unchanged A1 policy. v0.14B Hessian/local-minimum admission remains blocked until a complete 9/9, 45/45 relaxation ledger exists.

## Reconciled repository authority

The repository default branch `main` is explicitly documented as the project Source of Truth for canonical code, manuscript, benchmarks, gates, and current project state.

Library/NOEMA may retain mirrors, recovery artifacts, cards, receipts, indexes, and continuity state, but must not be required to checkout/build/test/recover the canonical repository. Normal canonical persistence direction is repository -> mirror. Recovery from a mirror is exceptional and requires identity/provenance verification.

## Reconciled PhaseNav boundary

PhaseNav may provide native commands, concepts, gates, 36D state records, orchestration, and receipts. External quantum-chemistry packages remain isolated conventional numerical backend adapters.

Operational representation is not physical authority: PhaseNav may preserve and route conventional energies, gradients, Hessians, convergence failures, and exceptions, but may not rewrite them to obtain a desired relational result.

## Packaging reconciliation

Package semver remains `0.1.0`; this is deliberately independent of research-gate labels such as v0.13 or v0.14A1.

Core install metadata is now aligned with the repository runtime contract:

- `numpy>=1.26`;
- `scipy>=1.11`.

The frozen molecular control backend is exposed only as the optional extra `molecular-v014`:

- `pyscf==2.14.0`;
- `geometric==1.1.1`.

This keeps conventional molecular backends out of the core semantic/runtime dependency set while making the exact v0.14 environment explicit and reproducible. The full textbook/repository gate now performs `pip install .` followed by `pip check` so package metadata cannot drift silently from CI requirements.

## CI reconciliation

Maintained current gates now target `main` and pull requests targeting `main`:

- `compound-relations-ci.yml`;
- `bibliography-ci.yml`;
- `monograph-ci.yml`;
- `period2-active-ci.yml`;
- `web-ci.yml`.

The compound/molecular gate now includes `MOLECULAR_*.json` and verifies v0.13/v0.14 current surfaces. The textbook gate additionally validates package installation metadata before the full Python regression and manuscript build.

Frozen versioned experiment workflows are retained as manual `workflow_dispatch` replay surfaces with their computational jobs unchanged:

- closed-shell v0.11/v0.11C controls;
- atomic-ion convergence v0.12A/v0.12B;
- v0.14 molecular backend smoke/status and full relaxation replay.

This prevents accidental automatic recreation of historical experiments from pushes to obsolete branches while preserving reproducibility.

## Files intentionally not rewritten

Historical numerical receipts, frozen preregistrations, raw evidence ZIPs, scientific source modules, and old standalone historical formalism artifacts were not rewritten merely to make dates/narrative look current. Their history is part of provenance.

The v0.14A1 amendment note received only an appended subsequent-execution section; the original amendment status and chronology remain intact.

## Acceptance criteria for this reconciliation

Before merge to `main`:

1. branch must remain based on the exact current `main` without unrelated scientific-code changes;
2. package metadata install plus `pip check` must pass;
3. full Python regression must pass;
4. compound/molecular JSON + current-surface checks must pass;
5. bibliography DOI/key/wiring audit must pass;
6. LaTeX/BibTeX textbook build must pass with no unresolved references/citations;
7. subsystem period-2 and web gates must remain green where triggered;
8. final diff must contain no unintended scientific model/benchmark mutation;
9. merge itself remains a separate user decision.

Epistemic status of this reconciliation: **REPOSITORY_STATE_ALIGNMENT / NOT_SCIENTIFIC_PROMOTION**.
