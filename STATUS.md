# Resonant Chemistry Status

## 2026-08-14 — compound relation / molecular-structure checkpoint

State: **CONTROL STACK IMPLEMENTED / COMPOUND-RELATION CANDIDATE STACK v0.1–v0.11 / SOFTWARE+PROVENANCE CI ACTIVE / PHYSICAL ADMISSION PARTIAL / CANON NOT PROMOTED**

Integration branch: `compound-relations-v0.3`.

`main` is not the integration target of this working checkpoint.

## Operational contract

The compound track follows these standing rules:

- observation != hypothesis != candidate != implemented != tested != validated != promoted canon;
- UNKNOWN until probed;
- nuclear identity remains explicit and integer-`Z`;
- conventional quantum chemistry is the physical control baseline;
- representation candidates may not silently rewrite control energies or Hamiltonians;
- failed controls remain visible and are not repaired with candidate-specific rescue branches;
- preregistered candidates are not deleted after contradictory evidence appears;
- missing literature is not converted into a negative existence label;
- every technical paper used to motivate, constrain, validate, or falsify an active gate is added to the live bibliography in the same development iteration.

## Atomic/control physics

The pre-existing control stack remains the physical baseline:

- atomic identity and electronic configurations through Kr;
- hydrogenic analytic/numerical radial controls;
- He variational, RHF, finite-CI, natural-occupation and entropy controls;
- Li open-shell UHF;
- average-of-configuration atomic HF;
- global non-element-specific DIIS/quality ladder;
- H–Kr atomic control coverage with explicit convergence/virial gates;
- equivalent-shell multiplets, spin-orbit ordering, period-2 spectroscopy/CI;
- carbon correlation and state-averaged orbital-relaxation diagnostics.

No compound-relation term is inserted into these atomic Hamiltonians.

## v0.1 — shell-relation stoichiometric skeleton

Frozen rule for an outer main-group `s/p` shell:

`d(v) = min(v, C-v)`

with `C=2` for the first shell and `C=8` thereafter.

Binary endpoint balance:

`n_A d_A = n_B d_B`.

Current consequences:

- 231 H–Kr main-group binary skeleton candidates;
- Sc–Zn intentionally fail closed;
- nuclei remain discrete;
- particle-hole complementarity is representation metadata, not bond energy.

## v0.2 — post-blind diagnostic screen

The first 18-pair screen exposed three useful falsifier classes:

- B2H6: ordinary two-centre endpoint graph is insufficient;
- PCl5 / SF6: higher coordination/reorganization is required;
- KrF2: frozen closed-shell `d=0` is not equivalent to chemical impossibility.

The observed primary-formula hit count is not treated as a general chemistry accuracy estimate.

## v0.3 — connected integer relation graph

Candidate graph law:

`sum_j b_ij = d_i`, with `b_ij in {0,1,2,3}` and graph connectivity.

Software controls recover coarse relation-order patterns for H2, F2, O2, N2,
H2O, NH3, CH4, CO2, HCN, C2H2, C2H4 and C2H6.

B2H6, PCl5, SF6 and KrF2 remain explicit failures at this layer.

## v0.4 — three-centre hyperrelation candidate

The B2H6 failure is handled by a separate minimal-augmentation primitive rather
than by changing `d(v)`:

- pair relation load uses integer half-units;
- ordinary bond order `b` consumes `2b` half-units on both endpoints;
- symmetric bridge consumes `1:2:1` on outer:bridge:outer;
- valid 2c graphs always win before any 3c augmentation is admitted.

B2H6 first closes with two bridges plus four terminal pair relations.  The same
structural pattern transfers to Al2Cl6, Al2Br6 and Ga2Cl6 without a rule change.

The half-unit representation is not interpreted as literal fractional electrons.

## v0.5 — coordination/reorganization ladder candidate

For heavier above-half main-group centres:

`d0=min(v,C-v)`, `d*=max(v,C-v)`, `d_q=d0+2q`.

Frozen examples:

- P: `(3,5)`;
- S: `(2,4,6)`;
- Cl: `(1,3,5,7)`;
- As: `(3,5)`;
- Se: `(2,4,6)`;
- Br: `(1,3,5,7)`;
- second-period N/O/F remain unexpanded;
- closed-shell Kr remains zero in this gate.

A later null analysis showed that the `+2` sequence largely reduces to ordinary
paired-electron parity information.  It is therefore **not promoted as new
physics by itself**.

ClF7 and BrF7 remain structurally generated but were independently recorded as
energetically unstable against F2 loss rather than deleted post hoc.

## v0.6 — parity-matched validation

On the frozen SF_n sequential dissociation series, parity-only M0 and shell-
ladder M1 produce identical labels and equal rank performance.

Verdict: **NO incremental shell-gate information over parity on SF_n**.

The N/P and O/S retrospective contrast supports logical discrimination by the
`n>=3` gate but is not blind validation because those labels were already known.

## v0.7 — held-out ligand-family lookup

A Cl/Br family panel was frozen before lookup.  Positive primary-source support
was resolved for several heavier-element entries, but the resolved subset was
predicted identically by M0 and M1.

Verdict: **existence lookup is a poor primary discriminator** because reliable
positive reports are much easier to certify than global chemical nonexistence.

The next target was therefore changed to a common computable energetic control.

## v0.8 — energetic admission contract

Preregistered pair-loss channel:

`XY_n -> XY_(n-2) + Y2`

with

`DeltaE_pair = E(XY_(n-2)) + E(Y2) - E(XY_n)`.

Admission requires common-method energies plus harmonic local-minimum checks.
Missing/incomparable calculations remain UNKNOWN; an invalid preregistered
product invalidates that channel rather than generating a false negative.

Frozen conventional method policy:

- Stage A geometry/Hessian/ZPE: r2SCAN-3c;
- Stage B energy confirmation: DLPNO-CCSD(T1)/TightPNO with common basis/CBS policy;
- gas phase;
- common multiplicity and seed-geometry policy;
- no candidate-specific rescue.

This is a conventional control gate, not a Resonant-Chemistry energy term.

## v0.9 — generic closed-shell activation candidate

KrF2 motivated a new gate, but krypton is **not special-cased**.

Generic eligibility:

- centre: full outer `s/p` shell, frozen relation degree zero, `n>=2`;
- ligand: frozen relation degree one on the `ABOVE_HALF` branch.

Within the current H–Kr domain this mechanically yields:

- centres: Ne, Ar, Kr;
- ligands: F, Cl, Br;
- nine frozen `XY2` structural candidates.

The topology label is a symmetric linear 3c4e candidate with `q_cs=1`; it does
not imply thermodynamic stability.

## v0.9 post-freeze topology warning

Post-freeze literature immediately showed that **stoichiometry is not topology**:

- KrF2 has established three-centre bonding descriptions;
- KrCl2 has primary experimental literature describing van der Waals isomers;
- ArF2 has environment-specific high-pressure theoretical stabilization;
- NeF2 has method/descriptor-sensitive theoretical literature.

Therefore formula matching or local-minimum existence cannot validate the v0.9
3c4e topology by itself.

## v0.10 — electronic-topology admission contract

Three independent diagnostic families are frozen:

1. `ORBITAL_SUBSPACE`;
2. `REAL_SPACE_FORCE`;
3. `FRAGMENTATION_ISOMER_ENERGY`.

Each reports `SUPPORT_3C4E`, `SUPPORT_VDW`, `INCONCLUSIVE`, or `NOT_RUN` while
preserving raw method provenance.

Preregistered aggregator:

- >=2 independent families support 3c4e and none support VDW -> consistent 3c4e;
- symmetric rule for VDW;
- opposing informative families -> mixed/conflicting;
- fewer than two agreeing families -> UNKNOWN;
- no local minimum -> rejected without stable-topology label.

The 2-of-3 policy is a validation contract, not a physical constant.

Held-out reference lookup after freezing v0.10 found primary-source VDW
classifications for NeCl2, NeBr2 and ArBr2, in conflict with the broad v0.9
structural 3c4e label.  Formal v0.10 labels remain UNKNOWN until a second
independent admitted diagnostic family is available.  KrBr2 remains UNKNOWN.

`ELECTRONIC_TOPOLOGY_JOB_MATRIX_V0_10A.json` freezes the next common analysis
matrix; no single QTAIM BCP, canonical MO diagram, or arbitrary bond-order
threshold can resolve topology alone.

## v0.11 — conventional atomic activation control

Before fitting any new relational score, v0.11 asks whether existing isolated-
atom controls already contain useful explanatory information.

Frozen raw vector for centre X and ligand Y:

- `I_X^HF = E_HF(X+) - E_HF(X)`;
- `A_Y^HF = E_HF(Y) - E_HF(Y-)`;
- `Delta_CT^HF = I_X^HF - A_Y^HF`;
- neutral centre/ligand outer-`p` mean radii and radial sigmas;
- explicit robust-HF quality flag.

No scalar classifier, fitted weight, or threshold is defined.

### First physical execution

GitHub Actions run `31781583863` produced and preserved the raw nine-vector
artifact (`artifact 9211970960`, ZIP SHA256
`3561db6e5307f81f156025357639f1e3de8d08090a3fc4cc709f1a0c92b20941`).

Result: **FAIL CLOSED — atomic quality failures present**.

Observed pair-level pattern:

- all Ne/Ar/Kr + Cl vectors: quality PASS;
- all Ne/Ar/Kr + F vectors: quality FAIL;
- all Ne/Ar/Kr + Br vectors: quality FAIL.

This localizes the issue to ligand-side atomic controls, but the first schema
cannot distinguish neutral from anion failure.  Raw values from failed controls
are not admitted quantitative descriptors.

v0.11B therefore repeats the exact same 12 unique atom/charge solves only to
record per-state convergence, global-stage index and virial quality.  No solver
setting or physical operator is changed.

## Live bibliography / provenance invariant

The working textbook now uses a modular live bibliography under
`monograph/bibliography/*.bib`.

Current modules include:

- `references.bib` — active source ledger;
- `compound_legacy.bib` — backfilled provenance from older compound gates.

`monograph/main.tex` wires both modules and uses `\nocite{*}` so the current
source ledger appears in the working PDF.

CI invariant:

- any DOI used by active compound benchmarks/docs but absent from the live
  bibliography -> FAIL;
- duplicate BibTeX key or DOI -> FAIL;
- a bibliography module present but not wired into the monograph -> FAIL.

The first audit exposed 11 historical missing DOI records; all were backfilled
without changing any model result.

## Current CI state

`compound-relations-ci` is active on the working branch.

Verified successful run `31781739029` at commit
`b013650f6ee145f55b64aa5eb51367a7215ad79a` passed:

- complete Python test discovery;
- compound benchmark JSON parsing;
- live bibliography DOI/key/wiring audit;
- branch-surface verification.

A separate `bibliography-ci` now builds the textbook through LaTeX/BibTeX and
rejects unresolved citations/references; its first branch execution is part of
the current verification trajectory.

The v0.11 physical-control workflow is intentionally fail-closed and is tracked
separately from software/provenance CI.

## Molecular extension

The conventional multicentre molecular physics solver remains a separate open
control frontier.  The compound-relation layers are structural/admission
interfaces into that future solver; they do not replace Born–Oppenheimer or
standard electronic-structure calculations.

## TIR / PhaseNav / semantic admission

- `kappa = ln(2)/(24*pi)` remains model-defined metadata;
- `W_AB` remains reserved/candidate until tied to a no-refit observable;
- 36D PhaseNav remains a representation interface, not proof of 36 physical dimensions;
- semantic/affective mappings may consume immutable control invariants but may
  not rewrite conventional physical controls;
- no TIR or affective correction is promoted into atomic or molecular energies.

## Not claimed

- a validated knot-shell law;
- a topological force term in a Hamiltonian;
- a validated energetic Resonant-Chemistry molecular solver;
- literal fractional-electron meaning of v0.4 half-unit bookkeeping;
- literal expanded-octet/d-orbital mechanism for v0.5;
- independent physical novelty of the v0.5 `+2` ladder by itself;
- general chemical accuracy from the v0.2 formula screen;
- blind validation from retrospective/preknown cases;
- a 3c4e topology inferred solely from an `XY2` formula, linear geometry, one
  QTAIM critical point, or one orbital picture;
- quantitative validity of v0.11 atomic descriptors for states that fail the
  robust atomic quality gate;
- complete transition-metal, hypervalent, radical, electron-deficient, or
  noble-gas chemistry;
- canonical promotion of the compound-relation candidate stack.
