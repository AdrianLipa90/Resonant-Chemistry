# Resonant Chemistry Status

## 2026-08-14 — compound relation / molecular-state checkpoint

State: **CONTROL PHYSICS BASELINE PRESERVED / COMPOUND CANDIDATE STACK v0.1–v0.13 IMPLEMENTED / SOFTWARE+PROVENANCE CI ACTIVE / PHYSICAL ADMISSION PARTIAL / CANON NOT PROMOTED**

Integration branch: `compound-relations-v0.3`.

`main` is not modified by this working checkpoint.

## Operational contract

- observation != hypothesis != candidate != implemented != tested != validated != promoted canon;
- UNKNOWN until probed;
- nuclei remain explicit and integer-`Z`;
- conventional quantum chemistry remains the physical control baseline;
- structural/relational candidates may not silently rewrite control Hamiltonians or energies;
- failures remain visible; no target-specific rescue branch may erase a preregistered failure;
- predictions are not deleted after contradictory evidence appears;
- missing literature is not a negative chemical-existence label;
- any technical source used by an active gate is added to the live bibliography in the same development iteration.

## Control-physics baseline

The pre-existing H–Kr atomic stack remains the control substrate: analytic/numerical hydrogenic checks, He variational/RHF/CI controls, Li open-shell UHF, average-of-configuration atomic HF, global DIIS/quality ladders, H–Kr coverage, shell multiplets, spin-orbit ordering, period-2 spectroscopy/CI, and carbon correlation/orbital-relaxation diagnostics.

No compound-relation correction is inserted into those control Hamiltonians.

## Compound trajectory v0.1–v0.8

### v0.1 — nearest-closed-shell relation skeleton

`d(v)=min(v,C-v)` and binary endpoint balance `n_A d_A = n_B d_B`.

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

Coarse controls recover H2/F2/O2/N2/H2O/NH3/CH4/CO2/HCN/C2H2/C2H4/C2H6 patterns. B2H6/PCl5/SF6/KrF2 remain explicit failures.

### v0.4 — three-centre bridge candidate

A separate `1:2:1` half-unit hyperrelation closes B2H6 with two bridges plus four terminal relations and transfers structurally to Al2Cl6/Al2Br6/Ga2Cl6. Half-units are bookkeeping, not literal fractional electrons.

### v0.5 — coordination/reorganization ladder

For heavier above-half centres: `d0=min(v,C-v)`, `d*=max(v,C-v)`, `d_q=d0+2q`.

The `+2` sequence was later reduced largely to ordinary parity information and is **not promoted as independent new physics**. ClF7/BrF7 remain generated but are recorded as energetically unstable against F2 loss rather than deleted.

### v0.6 — parity-matched null

On sequential SF_n dissociation, M0 parity and M1 shell ladder are identical. Verdict: **no incremental shell information over parity on that target**.

### v0.7 — held-out ligand-family lookup

Existence lookup proved non-discriminating: resolved positives were predicted by both M0 and M1, while missing reports could not supply valid negatives. The primary target was therefore changed to a common computable physical observable.

### v0.8 — energetic admission contract

Preregistered pair-loss control:

`XY_n -> XY_(n-2) + Y2`,

`DeltaE_pair = E(XY_(n-2)) + E(Y2) - E(XY_n)`.

Frozen conventional policy: r2SCAN-3c geometry/Hessian/ZPE screen followed by DLPNO-CCSD(T1)/TightPNO high-level confirmation under one common method/basis/environment policy. This is a conventional control gate, not a Resonant-Chemistry energy term.

## Closed-shell topology trajectory v0.9–v0.10

### v0.9 — generic closed-shell activation branch

KrF2 motivated the gate but krypton is not special-cased.

Eligibility inside H–Kr gives centres Ne/Ar/Kr and ligands F/Cl/Br, producing nine `XY2` structural candidates with a linear 3c4e branch.

Post-freeze evidence showed immediately that **stoichiometry is not topology**: KrF2 has established three-centre bonding descriptions, while KrCl2 and several rare-gas halogen systems have van der Waals reference classes.

### v0.10 — electronic-topology admission

Frozen independent diagnostic families:

1. `ORBITAL_SUBSPACE`;
2. `REAL_SPACE_FORCE`;
3. `FRAGMENTATION_ISOMER_ENERGY`.

A stable topology label requires at least two agreeing independent families and no informative opposing family. Conflicts remain mixed; insufficient evidence remains UNKNOWN. The 2-of-3 rule is a validation contract, not a physical constant.

Post-preregistered literature classes NeCl2, NeBr2 and ArBr2 as van der Waals systems, conflicting with the broad v0.9 3c4e branch. Formal v0.10 remains UNKNOWN until a second admitted diagnostic family exists. KrBr2 remains UNKNOWN.

## Atomic explanatory-control trajectory v0.11–v0.12

### v0.11 — first atomic finite-difference control attempt

Raw vector used the existing atomic HF control only:

- `I_X^HF = E(X+) - E(X)`;
- `A_Y^HF = E(Y) - E(Y-)`;
- `Delta_CT^HF = I_X^HF - A_Y^HF`;
- neutral outer-`p` radial descriptors.

No scalar classifier or fitted threshold was defined.

The first physical run failed closed. Targeted v0.11C localized the failures:

- F neutral PASS; F- FAIL because SCF converged to a state with virial residual ~18.09 Ha;
- Br neutral PASS; Br- FAIL after 700 iterations with virial residual ~9.54 Ha;
- both are `anion_only_failure` under the frozen broad quality gate.

A separate canonical-fidelity audit showed that first-passing neutral energies were not numerically identical to the previously frozen neutral checkpoints, especially for Br/Kr. Therefore v0.11 finite-difference energies are **not admitted as a precision chemistry descriptor**.

### v0.12A — global L0/L1/L2 numerical scan

All twelve states Ne/Ne+/Ar/Ar+/Kr/Kr+/F/F-/Cl/Cl-/Br/Br- were run through the same globally enlarged radial spaces without early acceptance and without selecting a numerical convergence threshold.

Verified workflow run: `31783012784`, head `71175b86c98fcec6f775ace798c130ad144ba541`, combined artifact SHA256 `105954c3a8372f956b4f581f99cf25e44505df00222f6df6f257ac0cd64b60ad`.

Important observations:

- F- changes to a low-virial converged branch only at L2;
- Br- changes from nonconverged L0/L1 to converged low-virial L2;
- Ne/Ar/Kr ionization matched differences and Cl attachment show decreasing drift through L2;
- F/Br attachment differences are not stable across v0.12A because the anions change numerical branch at the terminal level.

No L2 value was declared converged.

### v0.12B — common L3 continuation

Because F-/Br- entered their viable branch only at L2, a further identical L3 was frozen for all twelve states before any convergence criterion was proposed:

- basis 32;
- grid 2200;
- `zeta_min=0.0025`;
- `r_max=300 bohr`;
- common late-stage DIIS/damping settings;
- no target-specific rescue.

Verified workflow run: `31783601291`, head `7566987863f0b7a750e5c40fdb1747e3ab9d5b95`, combined artifact SHA256 `1e8e4c44a29dbdb0ca67528688cca56279d4fcbb912125d6967ce3bf91245050`.

Results:

- F- and Br- remain SCF-converged on the L3 branch with small virial residuals;
- attachment drift L2->L3 is small for F (~9.78e-5 Ha), Cl (~1.12e-4 Ha), and Br (~2.57e-4 Ha);
- Ne/Ar ionization drift remains small;
- **neutral Kr is the counterexample to monotonic diffuse extension**: L3 virial rises to ~5.09 Ha and Kr ionization drift jumps to ~0.0465 Ha.

Verdict: **do not fit or promote a chemistry classifier from the v0.11/v0.12 atomic energy-difference path at this stage**. Global diffuse extension improves the anion problem but is not uniformly quality-improving across the full state set.

No post-hoc convergence tolerance is selected and no L4 continuation is launched automatically.

## v0.13 — competing relational-state ensemble

The core architectural update is:

`composition -> unranked ensemble of relational states -> physical admission`

instead of

`composition -> one predicted graph`.

For every frozen v0.9 closed-shell `XY2` composition, v0.13 generates the same three competing branches:

1. `ACTIVATED_LINEAR_3C4E`;
2. `WEAK_COMPLEX_LINEAR_END_ON`;
3. `WEAK_COMPLEX_T_SHAPED`.

Nine compositions therefore yield 27 state candidates.

Every state has `prior_rank=None` and `prior_probability=None`; known KrF2/VDW cases are not converted into priors. The implementation rejects prior ranking at this layer.

Physical selection remains delegated to:

- conventional energetic/local-minimum controls;
- v0.10 multi-diagnostic electronic-topology admission.

The physical layer may select one state, multiple metastable states, or reject all enumerated states.

This ensemble architecture also captures the broader lesson of B2H6 and PCl5/SF6: new relation modes should coexist as competing branches rather than silently overwrite the lower-level relation law.

## Live bibliography and provenance

The working textbook uses the modular ledger `monograph/bibliography/*.bib`.

- `references.bib`: active/current sources;
- `compound_legacy.bib`: backfilled older compound-track provenance.

Invariant enforced by CI:

- source DOI used in active compound docs/benchmarks but absent from the ledger -> FAIL;
- duplicate BibTeX key or DOI -> FAIL;
- bibliography module not wired into `monograph/main.tex` -> FAIL.

A dedicated LaTeX/BibTeX build gate has already passed and produced a PDF/hash receipt. New sources are added in the same development iteration; v0.12/v0.13 introduced no new external paper and therefore required no duplicate bibliography entries.

## Current verification state

Verified independent execution gates include:

- complete v0.12A 12-state numerical scan: PASS as an execution/receipt gate;
- complete v0.12B 12-state L3 continuation: PASS as an execution/receipt gate;
- bibliography LaTeX/BibTeX/PDF build: PASS;
- branch software/provenance CI: active on every push; current compound-state ensemble changes are subject to the same full Python-test, JSON, DOI and branch-surface checks.

Scientific nonconvergence and failed physical controls are not converted into CI infrastructure failures unless a preregistered gate explicitly requires physical quality.

## Open physical frontier

The priority is now **state admission for compounds**, not further tuning of the atom-only descriptor:

1. feed v0.13 competing states into a conventional common-method molecular control;
2. preserve all local minima/isomers and compare their energies under one policy;
3. apply v0.10 electronic-topology evidence to distinguish activated 3c4e from weak-complex states;
4. keep UNKNOWN when the second independent topology family is absent.

The conventional multicentre molecular solver remains a separate control frontier; the relational stack is an interface into it, not a substitute for Born–Oppenheimer/electronic-structure physics.

## TIR / PhaseNav admission

- `kappa = ln(2)/(24*pi)` remains model-defined metadata;
- `W_AB` remains reserved/candidate until tied to a no-refit observable;
- 36D PhaseNav remains a representation interface, not proof of 36 physical dimensions;
- semantic/affective mappings may consume immutable controls but may not rewrite physical control outcomes;
- no TIR or affective correction is promoted into atomic or molecular energies.

## Not claimed

- a validated knot-shell law;
- a topological force term in a physical Hamiltonian;
- a validated Resonant-Chemistry molecular-energy solver;
- literal fractional-electron meaning of v0.4 half-units;
- literal expanded-octet/d-orbital mechanism for v0.5;
- independent physical novelty of the v0.5 `+2` sequence;
- general chemical accuracy from v0.2 formula screening;
- 3c4e topology from stoichiometry/linearity/one QTAIM point/one orbital picture alone;
- quantitative molecular prediction from the retired v0.11 atomic finite-difference path;
- numerical convergence of every v0.12 L2/L3 atomic energy;
- completeness of the v0.13 state ensemble;
- complete transition-metal, hypervalent, radical, electron-deficient, or noble-gas chemistry;
- canonical promotion of the compound candidate stack.
