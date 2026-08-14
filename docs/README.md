# Resonant Chemistry documentation index

This directory contains supplemental development and validation notes. The repository default branch `main` is the project Source of Truth, while `monograph/main.tex` is the primary formal scientific surface. A Markdown note may contain operational detail, but it does not supersede the manuscript, benchmark ledger, machine-readable receipts, or semantic-card evidence projections.

## Current frontier

The current merged scientific trajectory through the v0.14A1 checkpoint is:

`atomic controls -> shell/correlation controls -> compound relation gates -> competing v0.13 state ensemble -> conventional v0.14A/A1 molecular relaxation screen -> future Hessian/electronic-topology admission`

Current molecular execution status is **partial**:

- 9 frozen closed-shell `XY2` compositions;
- 5 frozen starts per formula;
- 8/9 formula receipts durably recovered;
- 40/45 starts have first-attempt evidence;
- `ArBr2 = MISSING_EXECUTION`;
- no Hessian/local-minimum admission;
- no validated ground-state ranking;
- no geometry-only 3c4e/VDW topology label.

The semantic projection layer is reconciled through the same v0.14A1 checkpoint. It is downstream of repository evidence and may not strengthen the scientific status of the source benchmark.

The current carbon correlation frontier is multidimensional state-averaged orbital optimization after the already informative one-coordinate active-external radial-p gate.

## Current compound/molecular notes

Read these in trajectory order:

1. `compound_shell_relations_v0_1.md` — nearest-closed-shell structural skeleton.
2. `postblind_compound_validation_v0_2.md` — falsifier classes and scope correction.
3. `relation_graph_gate_v0_3.md` — connected integer relation graph.
4. `hyperrelation_bridge_gate_v0_4.md` — separate three-centre bridge bookkeeping.
5. `coordination_ladder_v0_5.md` — coordination/reorganization candidate and later parity caveat.
6. `parity_matched_validation_v0_6.md` — parity-matched null.
7. `heldout_ligand_lookup_v0_7.md` — non-discriminating literature lookup and missing-negative warning.
8. `energetic_admission_v0_8.md` — conventional high-level energetic/Hessian admission contract.
9. `closed_shell_activation_v0_9.md` — generic closed-shell activation atlas.
10. `electronic_topology_v0_10.md` — independent multi-diagnostic topology admission.
11. `closed_shell_atomic_control_v0_11.md` — non-admitted atomic finite-difference control attempt.
12. `atomic_ion_convergence_v0_12a.md` / `atomic_ion_convergence_v0_12b.md` — global numerical scans and the Kr counterexample to monotonic diffuse extension.
13. `compound_state_ensemble_v0_13.md` — 27 unranked competing states over nine compositions.
14. `molecular_state_relaxation_v0_14a.md` — reconciled common molecular relaxation screen and current execution state.
15. `molecular_state_relaxation_v0_14a1_amendment.md` — historical post-smoke/pre-screening numerical pruning amendment.
16. `molecular_state_relaxation_v0_14a1_partial_readout.md` — constrained interpretation of the durable 8/9, 40/45 partial evidence.
17. `semantic_card_reconciliation_v0_14a1.md` — semantic-card backlog repair, model/gate projection coverage, and CI anti-drift invariant.

The machine-readable benchmark/receipt is authoritative when a Markdown summary and JSON disagree. Semantic cards are derived projections and therefore cannot override their named source artifacts.

## Historical/candidate topology notes

- `knot_conformal_atom_symmetry_v0_1.md` — historical atom-level exploratory comparison; direct spectral association was not promoted.
- `knot_conformal_shell_symmetry_v0_2.md` — corrected shell-level comparison object.
- `shell_nbody_topology_v0_1.md` — shell-level N-body topology primitives and dimensional boundaries.

These remain candidate diagnostics and do not define a new force term.

## Documentation and semantic-card discipline

A merged change that materially alters any of the following requires documentation reconciliation:

- implementation status;
- numerical/physical validation state;
- benchmark or receipt availability;
- current nonclaims;
- Source-of-Truth or reproducibility contract;
- next open scientific gate;
- bibliography/method provenance;
- semantic-card projection coverage.

Minimum reconciliation surface:

- `README.md`;
- `STATUS.md`;
- the relevant `docs/` note;
- the relevant chapter in `monograph/`;
- appendix A benchmark ledger;
- appendix B equation-to-code map;
- appendix C validation/reproducibility contract when methodology changed;
- appendix D open gates;
- bibliography module(s) if new sources were used;
- `semantic_cards/` overlay/coverage ledger for every new atomic, compound, state, or molecular gate.

A PDF may compile successfully while being scientifically stale. Build correctness, repository-state reconciliation, and semantic-card coverage are separate gates.

## CI classes

### Maintained current gates

These validate the repository SoT and pull requests targeting it:

- `compound-relations-ci.yml` — full Python regression, compound/molecular JSON, semantic-card coverage/epistemic audit, bibliography audit, current surfaces;
- `bibliography-ci.yml` — modular bibliography + LaTeX/BibTeX build;
- `monograph-ci.yml` — full tests, repository audit, bibliography audit, textbook build;
- `period2-active-ci.yml` — period-2/carbon subsystem regression;
- `web-ci.yml` — static 36D/web surface smoke.

### Frozen/replay experiment workflows

Versioned v0.11/v0.12/v0.14 experiment workflows encode specific preregistered numerical experiments. They are provenance/replay surfaces, not the current repository-wide CI contract. Their outputs retain the epistemic status declared by the corresponding preregistration and receipts.

Do not reinterpret a replay as a replacement for the original first-attempt receipt, and do not use a historical branch name as evidence of current canon.

## PhaseNav/NOEMA boundary

New orchestration functions may be exposed through PhaseNav-native commands, concepts, gates, 36D state records and receipts. External quantum-chemistry packages remain isolated conventional numerical backends. PhaseNav/NOEMA may preserve execution semantics and provenance but may not rewrite conventional energies, gradients, Hessians, failures, or scientific status.

Library/NOEMA continuity stores are mirrors/recovery/provenance for this project. They are not prerequisites for checking out, building, testing, or reproducing the repository SoT.
