# Resonant Chemistry Status

## 2026-08-14 — repository reconciliation checkpoint

State: **CONTROL PHYSICS BASELINE PRESERVED / COMPOUND CANDIDATE STACK v0.1–v0.13 IMPLEMENTED / v0.14A1 MOLECULAR SCREEN PARTIALLY EXECUTED / SOFTWARE+PROVENANCE GATES ACTIVE / PHYSICAL ADMISSION PARTIAL / CANON NOT PROMOTED**

Source of Truth: **GitHub repository `AdrianLipa90/Resonant-Chemistry`, default branch `main`**.

This status describes the state that has already been merged to `main` through merge commit `346fd8790846d776cbb826a540e6a27e20b653aa`. Research/reconciliation branches may contain newer unmerged documentation, but they do not replace `main` as project SoT.

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
- any technical source used by an active gate is added to the live bibliography in the same development iteration;
- implementation/runtime orchestration may be PhaseNav-native, but an external conventional electronic-structure backend remains an isolated control adapter and does not define Resonant-Chemistry semantics.

## Control-physics baseline

The pre-existing H–Kr atomic stack remains the control substrate: analytic/numerical hydrogenic checks, He variational/RHF/CI controls, Li open-shell UHF, average-of-configuration atomic HF, global DIIS/quality ladders, H–Kr coverage, shell multiplets, spin-orbit ordering, period-2 spectroscopy/CI, and carbon correlation/orbital-relaxation diagnostics.

No compound-relation correction is inserted into those control Hamiltonians.

The first state-averaged active–external carbon relaxation gate has already demonstrated a variationally informative radial-p direction under a frozen equal-weight `3P/1D/1S` objective. The next carbon control frontier is multidimensional state-averaged orbital optimization/MCSCF-type relaxation without experimental term-energy fitting.

## Compound trajectory v0.1–v0.8

### v0.1 — nearest-closed-shell relation skeleton

`d(v)=min(v,C-v)` with binary endpoint balance `n_A d_A = n_B d_B`.

- 231 H–Kr main-group binary skeleton candidates;
- Sc–Zn fail closed;
- particle-hole complementarity is representation metadata, not bond energy.

### v0.2 — post-blind diagnostic screen

Useful falsifier classes:

- B2H6 -> ordinary 2c graph insufficient;
- PCl5/SF6 -> coordination/reorganization required;
- KrF2 -> closed-shell `d=0` is not chemical impossibility.

The formula hit count is not a general chemistry accuracy claim.

### v0.3 — connected integer relation graphs

`sum_j b_ij=d_i`, `b_ij in {0,1,2,3}`, connected.

Coarse controls recover H2/F2/O2/N2/H2O/NH3/CH4/CO2/HCN/C2H2/C2H4/C2H6 patterns. B2H6/PCl5/SF6/KrF2 remain explicit failures of that frozen layer.

### v0.4 — three-centre bridge candidate

A separate `1:2:1` half-unit hyperrelation closes B2H6 with two bridges plus four terminal relations and transfers structurally to bridged Al/Ga halides. Half-units are bookkeeping, not literal fractional electrons.

### v0.5 — coordination/reorganization ladder

For heavier above-half centres: `d0=min(v,C-v)`, `d*=max(v,C-v)`, `d_q=d0+2q`.

The `+2` sequence was later reduced largely to ordinary parity information and is **not promoted as independent new physics**. ClF7/BrF7 remain generated but are recorded as energetically unstable against F2 loss rather than deleted.

### v0.6 — parity-matched null

On sequential SF_n dissociation, M0 parity and M1 shell ladder are identical. Verdict: **no incremental shell information over parity on that target**.

### v0.7 — held-out ligand-family lookup

Existence lookup proved non-discriminating: resolved positives were predicted by both M0 and M1, while missing reports could not supply valid negatives. The target was therefore changed to a common computable physical observable.

### v0.8 — energetic admission contract

Preregistered pair-loss control:

`XY_n -> XY_(n-2) + Y2`,

`DeltaE_pair = E(XY_(n-2)) + E(Y2) - E(XY_n)`.

Frozen high-level conventional policy: r2SCAN-3c geometry/Hessian/ZPE screen followed by DLPNO-CCSD(T1)/TightPNO confirmation under one common method/basis/environment policy. This is a conventional control gate, not a Resonant-Chemistry energy term. It remains distinct from the lower-cost v0.14 relaxation screen.

## Closed-shell topology trajectory v0.9–v0.10

### v0.9 — generic closed-shell activation branch

KrF2 motivated the gate but krypton is not special-cased. Eligibility inside H–Kr gives centres Ne/Ar/Kr and ligands F/Cl/Br, producing nine `XY2` structural candidates with a linear 3c4e branch.

Post-freeze evidence showed immediately that **stoichiometry is not topology**: KrF2 has established activated/three-centre bonding descriptions, while several rare-gas halogen systems have van-der-Waals reference classes.

### v0.10 — electronic-topology admission

Frozen independent diagnostic families:

1. `ORBITAL_SUBSPACE`;
2. `REAL_SPACE_FORCE`;
3. `FRAGMENTATION_ISOMER_ENERGY`.

A stable topology label requires at least two agreeing independent families and no informative opposing family. Conflicts remain mixed; insufficient evidence remains UNKNOWN. The 2-of-3 rule is a validation contract, not a physical constant.

Primary literature classes NeCl2, NeBr2 and ArBr2 as van-der-Waals systems, conflicting with the broad structural v0.9 3c4e branch. Formal v0.10 labels remain conservative until sufficient admitted diagnostic families exist.

## Atomic explanatory-control trajectory v0.11–v0.12

### v0.11 — atomic finite-difference control attempt

Raw vector used the existing atomic HF control only:

- `I_X^HF = E(X+) - E(X)`;
- `A_Y^HF = E(Y) - E(Y-)`;
- `Delta_CT^HF = I_X^HF - A_Y^HF`;
- neutral outer-p radial descriptors.

No scalar classifier or fitted threshold was defined. Targeted diagnostics localized F-/Br- failures, and a canonical-fidelity audit showed that first-passing neutral energies were not precise enough to support the intended finite-difference descriptor. Therefore v0.11 is **not admitted as a precision chemistry classifier**.

### v0.12A/B — common global numerical scans

All twelve Ne/Ne+/Ar/Ar+/Kr/Kr+/F/F-/Cl/Cl-/Br/Br- states were run through common globally enlarged spaces without target-specific rescue.

v0.12A showed that F- and Br- enter a viable low-virial branch only at the largest tested L2 space. v0.12B continued every state to the same L3 and found small attachment drifts for F/Cl/Br but a counterexample in neutral Kr: its L3 virial quality worsened and the Kr ionization difference moved substantially.

Verdict: **do not fit or promote a molecular chemistry classifier from the v0.11/v0.12 atomic finite-difference path at this stage**. No post-hoc convergence tolerance was selected.

## v0.13 — competing relational-state ensemble

Core architecture:

`composition -> unranked ensemble of relational states -> physical admission`

instead of

`composition -> one predicted graph`.

For every frozen v0.9 closed-shell `XY2` composition, v0.13 generates the same three competing branches:

1. `ACTIVATED_LINEAR_3C4E`;
2. `WEAK_COMPLEX_LINEAR_END_ON`;
3. `WEAK_COMPLEX_T_SHAPED`.

Nine compositions yield 27 state candidates. Every state has `prior_rank=None` and `prior_probability=None`; already-known KrF2/VDW examples are not converted into priors. Physical selection remains delegated to conventional energetic/local-minimum controls and v0.10 multi-diagnostic electronic-topology admission.

## v0.14A/A1 — common molecular-state relaxation screen

### Original v0.14A preregistration

v0.14A is a **conventional screening layer**, not a Resonant-Chemistry molecular-energy law. The common method was frozen before molecular relaxation outputs:

- PySCF 2.14.0 + geomeTRIC 1.1.1;
- B97M-V/VV10;
- def2-TZVPD;
- neutral singlets, gas phase;
- common SCF and optimizer policy;
- no candidate-specific rescue;
- no Hessian in this screen;
- no geometry-only topology verdict.

F2/Cl2/Br2 are relaxed first from one common 2.0 Å start. Their optimized `r_YY` values are used only as method-internal seed scales. Each of the nine XY2 compositions then receives the same five starts: three symmetric activated-linear seeds (`1.0`, `1.3`, `1.6` times `r_YY`), one weak end-on seed, and one weak T-shaped seed. Total frozen work: 45 XY2 relaxations.

### v0.14A1 global grid amendment

The original backend smoke exposed a PySCF SG-1 pruning limitation for Kr during VV10/NLC grid construction before a KrF2 energy was produced. The amendment was recorded **post-smoke / pre-screening-output** and changed only numerical pruning: both regular and NLC grids use the common PySCF `nwchem_prune` policy. B97M-V, VV10, def2-TZVPD, grid sizes, SCF policy, optimizer settings, seed geometries, and no-rescue rules remained unchanged.

The amended backend smoke subsequently passed and the common ligand-dimer prepass was durably recorded.

### v0.14A1 partial execution evidence

Original workflow: `31795895258`, frozen execution head `db756f5aa8598a24004f056aeb09b18034a08e5b`.

Durably recovered first-attempt formula receipts:

- NeF2, NeCl2, NeBr2;
- ArF2, ArCl2;
- KrF2, KrCl2, KrBr2.

Current durable matrix: **8/9 formulae, 40/45 frozen starts**.

`ArBr2` remains **`MISSING_EXECUTION`** after cancellation during the five-start job. This is an execution gap, not a negative chemical label. A later GitHub matrix rerun re-executed a broader dependency scope than intended; the original first-attempt receipts remain the canonical v0.14A1 evidence for the eight already-completed formulae. Only a missing ArBr2 receipt may fill the existing gap without replacing those first-attempt records.

Threshold-free descriptive observations from the persisted evidence:

- for every completed composition, the lowest successful *screening* electronic energy belongs to a weak-complex seed family;
- KrF2 has 3/3 successful activated starts; the symmetric activated basin is near `r(Kr-F) ~ 1.883 Å` and lies about `9.288 kcal/mol` above the lowest successful weak-linear screening state under this common screen;
- ArF2 activated starts: 3/3; corresponding activated-to-lowest-weak screening gap about `37.99 kcal/mol`;
- NeF2 activated starts: 2/3; corresponding gap about `95.93 kcal/mol`;
- NeCl2 and NeBr2: 0/3 successful activated starts, while both weak seed families complete;
- ArCl2: 2/3 activated starts complete;
- KrCl2: 2/3;
- KrBr2: 1/3;
- successful weak-complex states retain Y-Y distances close to the same-method ligand-dimer prepass values.

These are **basin-screen/convergence observations only**. They do not establish harmonic minima, ground states, dissociation stability, or 3c4e/VDW electronic topology.

## Current molecular gate boundary

The v0.14A1 preregistration/readout contract blocks a Hessian gate until all nine formula receipts / all 45 starts are durably present.

Therefore the immediate molecular frontier is:

1. complete **only the missing ArBr2 execution evidence** under the same frozen A1 policy, preserving timeout/cancellation as UNKNOWN if execution again fails;
2. obtain a complete 9/9, 45/45 screening ledger;
3. only then freeze a separate v0.14B Hessian/local-minimum admission protocol;
4. after local-minimum evidence exists, apply conventional energetic comparison and v0.10 multi-diagnostic electronic-topology admission;
5. retain UNKNOWN whenever required independent evidence is absent.

The older H2+/H2/HeH+/LiH molecular-control ladder remains scientifically useful as a complementary simple-system validation track, but it is no longer accurate to describe H2+ as the repository's first molecular implementation target: v0.14A/A1 molecular relaxation infrastructure now exists and has partial execution evidence.

## Live bibliography and provenance

The working textbook uses the modular ledger `monograph/bibliography/*.bib`:

- `references.bib`: active/current sources;
- `compound_legacy.bib`: backfilled older compound-track provenance;
- `molecular_screening.bib`: B97M-V, PySCF, diffuse def2, geomeTRIC, and grid-pruning technical provenance for v0.14.

Invariant:

- source DOI used in active compound docs/benchmarks but absent from the ledger -> FAIL;
- duplicate BibTeX key or DOI -> FAIL;
- bibliography module not wired into `monograph/main.tex` -> FAIL;
- manuscript build must reject unresolved citations/references.

A bibliography entry establishes provenance, not scientific promotion.

## CI / repository reconciliation requirement

Historical workflow triggers were created on research branches. Because `main` is now the project SoT, the maintained CI contract must validate `main` and pull requests targeting `main`, while retaining explicit manual dispatch where useful. Branch names from completed historical tracks must not be the sole trigger for textbook, bibliography, or compound-regression gates.

The full manuscript and root documentation must be updated whenever a merged change materially changes current implementation status, numerical evidence, open gates, or nonclaims. A PDF can be build-correct yet scientifically stale if the underlying LaTeX has not been reconciled with merged repository evidence.

## TIR / PhaseNav admission

- `kappa = ln(2)/(24*pi)` remains model-defined metadata;
- `W_AB` remains reserved/candidate until tied to a no-refit observable;
- 36D PhaseNav remains a representation/orchestration interface, not proof of 36 physical dimensions;
- new orchestration functions may be PhaseNav-native, but conventional quantum-chemistry backends remain isolated control adapters;
- semantic/affective mappings may consume immutable controls but may not rewrite physical control outcomes;
- no TIR, PhaseNav, or affective correction is promoted into atomic or molecular energies.

## Not claimed

- a validated knot-shell law;
- a topological force term in a physical Hamiltonian;
- a validated Resonant-Chemistry molecular-energy solver;
- a complete v0.14A1 molecular screen before ArBr2 is recovered;
- harmonic local-minimum status for v0.14A1 relaxed geometries;
- a validated ground-state ranking from v0.14A1 screening energies;
- 3c4e/VDW topology from stoichiometry, seed label, geometry, one QTAIM point, or one orbital picture alone;
- literal fractional-electron meaning of v0.4 half-units;
- literal expanded-octet/d-orbital mechanism for v0.5;
- independent physical novelty of the v0.5 `+2` sequence;
- general chemical accuracy from v0.2 formula screening;
- quantitative molecular prediction from the retired/non-admitted v0.11 atomic finite-difference path;
- numerical convergence of every v0.12 absolute atomic energy;
- completeness of the v0.13 state ensemble;
- complete transition-metal, hypervalent, radical, electron-deficient, or noble-gas chemistry;
- canonical promotion of the compound candidate stack.
