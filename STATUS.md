# Resonant Chemistry Status

## 2026-08-14 — v0.14A1 + semantic entity registry checkpoint

State: **CONTROL PHYSICS BASELINE PRESERVED / COMPOUND CANDIDATE STACK v0.1–v0.13 IMPLEMENTED / v0.14A1 MOLECULAR SCREEN PARTIALLY EXECUTED / SEMANTIC ENTITY-CARD GRAPH ACTIVE / SOFTWARE+PROVENANCE GATES ACTIVE / PHYSICAL ADMISSION PARTIAL / CANON NOT PROMOTED**

Source of Truth: **GitHub repository `AdrianLipa90/Resonant-Chemistry`, default branch `main`**. Exact canonical identity is the current `main` commit/tree; this file intentionally does not hard-code a commit SHA that would become stale after the next valid merge.

## Operational contract

- observation != hypothesis != candidate != implemented != tested != validated != promoted canon;
- UNKNOWN until probed;
- nuclei remain explicit and integer-`Z`;
- conventional quantum chemistry remains the physical control baseline;
- structural/relational candidates may not silently rewrite control Hamiltonians or energies;
- failures remain visible; no target-specific rescue branch may erase a preregistered failure;
- predictions are not deleted after contradictory evidence appears;
- missing literature is not a negative chemical-existence label;
- missing execution, cancellation, or timeout is not a chemical falsification;
- first-attempt/frozen receipts remain distinguishable from reruns;
- implementation/runtime orchestration may be PhaseNav-native, but conventional electronic-structure backends remain isolated control adapters;
- semantic-card membership or emergence does not imply physical validation;
- provenance holonomy is not physical holonomy;
- interpretive TIR/affective coordinates remain unassigned unless an explicit provenance-bearing mapping is supplied and tested.

## Control-physics baseline

The H–Kr atomic stack remains the control substrate: analytic/numerical hydrogenic checks, He variational/RHF/CI controls, Li open-shell UHF, average-of-configuration atomic HF, global DIIS/quality ladders, H–Kr coverage, shell multiplets, spin-orbit ordering, period-2 spectroscopy/CI, and carbon correlation/orbital-relaxation diagnostics.

No compound-relation or semantic-card correction is inserted into those control Hamiltonians.

The current carbon frontier is multidimensional state-averaged orbital optimization/MCSCF-type relaxation after the already informative one-coordinate active-external radial-p gate, without experimental term-energy fitting.

## Compound trajectory

### v0.1–v0.4 — structural relation grammar

- v0.1: nearest-closed-shell relation skeleton `d(v)=min(v,C-v)` with binary endpoint balance; 231 H–Kr main-group binary candidates; transition metals fail closed in this layer.
- v0.2: post-blind diagnostic preserved explicit falsifier classes; formula hit count is not a chemistry accuracy claim.
- v0.3: connected integer relation graphs with bond-order bookkeeping.
- v0.4: separate three-centre bridge bookkeeping for electron-deficient bridged structures; half-units are bookkeeping, not literal fractional electrons.

### v0.5–v0.8 — coordination, nulls, and energetic admission

- v0.5 coordination/reorganization ladder remains a candidate generator; the `+2` sequence is not promoted as independent new physics.
- v0.6 parity-matched test found no incremental shell information over parity on the chosen SF_n target.
- v0.7 held-out ligand lookup was non-discriminating and remains recorded as such.
- v0.8 defines a conventional pair-loss energetic/Hessian admission contract; it is not a Resonant-Chemistry energy term.

### v0.9–v0.10 — closed-shell activation and topology admission

- v0.9 generates the same nine closed-shell `XY2` structural candidates from centres Ne/Ar/Kr and ligands F/Cl/Br; stoichiometry is not topology.
- v0.10 requires independent diagnostic families before a stable electronic-topology label; insufficient evidence remains UNKNOWN.

### v0.11–v0.12 — atomic explanatory controls

The finite-difference atomic activation-control path remains a useful negative/numerical diagnostic but is **not admitted as a molecular chemistry classifier**. Global scans preserved F-/Br- and Kr convergence counterexamples without post-hoc threshold fitting.

### v0.13 — competing relational-state ensemble

Architecture:

`composition -> unranked ensemble of relational states -> physical admission`

Each of the nine v0.9 compositions receives the same three unranked state candidates:

1. `ACTIVATED_LINEAR_3C4E`;
2. `WEAK_COMPLEX_LINEAR_END_ON`;
3. `WEAK_COMPLEX_T_SHAPED`.

Nine compositions yield 27 states. `prior_rank=None` and `prior_probability=None` are invariant until physical admission.

## v0.14A/A1 — common molecular-state relaxation screen

Frozen conventional screen:

- PySCF 2.14.0 + geomeTRIC 1.1.1;
- B97M-V/VV10;
- def2-TZVPD;
- neutral singlets, gas phase;
- common SCF/optimizer policy;
- common ligand-dimer prepass;
- three activated + two weak starts per formula;
- no target-specific rescue;
- no Hessian in this screen;
- no geometry-only topology verdict.

The A1 amendment changed only common grid pruning after a backend smoke exposed a Kr SG-1 implementation boundary before molecular screening output existed.

Current durable execution evidence:

- **8/9 formulae**;
- **40/45 frozen starts**;
- `ArBr2 = MISSING_EXECUTION_NOT_CHEMICAL_FAIL`;
- first-attempt receipts for the eight completed formulae remain authoritative for this checkpoint;
- rerun scope is recorded separately and may not silently replace them.

Threshold-free screening observations remain descriptive only. The lowest successful screening energy for each completed composition comes from a weak-complex seed family; activated-start survival varies across Ne/Ar/Kr and F/Cl/Br. These observations do not establish harmonic minima, ground states, dissociation stability, or electronic topology.

## Semantic entity-card graph

Semantic cards are now a **required calculation-state layer**.

Canonical entry point:

`reschem.repository_cards.load_current_card_registry()`

Hash-stable downstream context:

`reschem.repository_cards.calculation_context([...])`

Current registry contract includes:

- 36 explicitly indexed neutral atomic base cards H–Kr;
- later atomic evidence attached nondestructively as overlays rather than silently overwriting base cards;
- persisted model/gate cards through v0.13;
- deterministic **231** v0.1 compound-relation candidate cards;
- deterministic **27** v0.13 relational-state candidate cards;
- a dynamic v0.14A1 model card plus **9** molecular formula-screen cards derived from the machine-readable readout.

Every generated entity carries:

- identity;
- physical/model properties;
- state invariants;
- named source artifacts;
- explicit relations to exact cards or deterministic selectors;
- provenance holonomy: parents + generating operation + lineage hash;
- physical-holonomy field, defaulting to `NOT_COMPUTED`;
- emergence status;
- epistemic status;
- unassigned TIR/affective layers unless separately admitted.

Model-derived new entities are marked `MODEL_DEFINED_EMERGENT_CANDIDATE`. This makes them addressable for further calculations without promoting them to physical existence, local minima, ground states, topology labels, or canon.

### Holonomy boundary

`provenance_holonomy` answers how a card arose in the model/state graph.

`physical_holonomy` may contain winding/phase/connection/topology observables only when they were explicitly computed and their source artifacts are named.

Therefore:

`provenance holonomy != physical holonomy`

and a semantic relation cycle cannot itself establish a physical topological effect.

## Semantic-card anti-drift gate

Maintained `compound-relations-ci` now runs `scripts/audit_semantic_card_coverage.py`.

The gate fails if:

- H–Kr canonical atomic-card coverage is incomplete;
- a current model/gate loses its card/overlay or named implementation/benchmark/documentation source;
- deterministic compound/state entity counts drift from frozen generators;
- v0.14A1 molecular cards disagree with expected/completed formulae in the benchmark;
- missing `ArBr2` is converted into chemical failure;
- TIR or affective values appear silently without provenance;
- a non-empty physical-holonomy claim lacks source artifacts;
- semantic cards promote Hessian, ground-state, or topology status beyond current evidence.

## Current open gates

1. Recover only the missing `ArBr2` execution evidence under the same frozen A1 policy.
2. Reach a complete 9/9 formula, 45/45 start screening ledger.
3. Only then freeze a separate v0.14B Hessian/local-minimum admission protocol.
4. After local-minimum evidence exists, apply conventional energetic comparison and v0.10 multi-diagnostic electronic-topology admission.
5. Continue carbon multidimensional state-averaged orbital optimization on its independent control track.
6. Any new atom/compound/state/emergent entity introduced by these steps must receive or deterministically generate a semantic card in the same development cycle.

## Documentation, bibliography, and CI

The formal scientific surface is `monograph/main.tex`; supplemental operational detail lives in `docs/`. A successful PDF build proves buildability, not currency. Changes to model state, evidence, open gates, or semantic-card coverage require reconciliation across README/status/docs/manuscript as appropriate.

The modular bibliography under `monograph/bibliography/` remains provenance-only and does not promote scientific claims.

Maintained gates validate `main` and pull requests targeting `main`. Frozen experiment workflows remain manual replay/provenance surfaces rather than current repository-wide CI.

## Not claimed

- a validated knot-shell law or new topological force term;
- a validated Resonant-Chemistry molecular-energy solver;
- a complete v0.14A1 molecular screen before `ArBr2` is recovered;
- harmonic local-minimum status for v0.14A1 relaxed geometries;
- a validated ground-state ranking from v0.14A1 screening energies;
- 3c4e/VDW topology from stoichiometry, seed label, geometry, one QTAIM point, or one orbital picture alone;
- literal fractional-electron meaning of v0.4 bookkeeping;
- independent physical novelty of the v0.5 `+2` sequence;
- general chemical accuracy from v0.2 formula screening;
- quantitative molecular prediction from the non-admitted v0.11 atomic finite-difference path;
- completeness of the v0.13 state ensemble;
- physical validation of an entity merely because it emerged from a model or exists in the card registry;
- physical holonomy merely because a provenance path or semantic loop exists;
- canonical promotion of the compound candidate stack.
