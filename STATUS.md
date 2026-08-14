# Resonant Chemistry Status

## 2026-08-14 - shell topology / compound relation checkpoint

State: **CONTROL STACK IMPLEMENTED / SHELL-TOPOLOGY CANDIDATE / COMPOUND-RELATION CANDIDATE / 3C-HYPERRELATION CANDIDATE / COORDINATION-LADDER CANDIDATE / CANON NOT PROMOTED**

Integration source: `compound-relations-v0.3`.

## Control physics

Implemented and covered by repository tests/benchmarks:

- atomic identity and electronic configurations through Kr;
- hydrogenic analytic and numerical radial controls;
- helium variational, RHF, finite-CI, natural-occupation and entropy controls;
- Li open-shell UHF;
- multi-channel average-of-configuration HF;
- global DIIS/quality fallback without element-specific branches;
- H-Kr control coverage with explicit convergence/virial caveats;
- p/d equivalent-shell LS multiplets;
- weak spin-orbit J ordering;
- B-Ne atom-specific radial F^k / Pauli-zeta spectroscopy control;
- period-2 active CI and correlated spin-orbit rediagonalization;
- carbon correlation-channel and sparse-multichannel diagnostics.

Current correlation frontier: **state-averaged orbital optimization / MCSCF for carbon 3P, 1D, 1S without experimental fitting**.

## Shell-level topology candidate

The primary candidate object is a subshell state `(n,l,k)` around one or more explicit nuclear Coulomb centres. It is not an atom-to-knot identification.

Implemented primitives:

- shell capacity `C_l=2(2l+1)`;
- particle-hole involution `k -> C_l-k`;
- self-dual half filling `k=2l+1`;
- 3D exchange permutation parity;
- declared-plane electron-nucleus and electron-electron winding diagnostics;
- conformal inverse coordinate with `z*=1/2` retained as a falsifiable model anchor;
- shell-only symmetry module and frozen p/d/f symmetry benchmark.

Physical validation of a knot-shell relation remains **OPEN**.

The previous direct knot-gap versus atom-gap association remains **REJECTED / NOT PROMOTED** because it did not beat the null test. The corrected next test is shell particle-hole symmetry followed by principal-shell transfer (`2p^k -> 3p^k`) before any joint knot comparison.

## Compound relation candidate

A non-energetic main-group bridge from the atomic bookkeeping to compounds is implemented as a candidate layer.

Frozen v0.1 rule:

- nuclei remain explicit and integer-Z;
- outer s/p shell relation degree `d=min(v,C-v)` with `C=2` for `n=1` and `C=8` thereafter;
- binary endpoint balance `n_A*d_A = n_B*d_B`;
- 231 H-Kr main-group binary skeleton candidates, with Sc-Zn deliberately fail-closed;
- particle-hole complementarity retained as representation metadata, not bond energy.

Post-blind v0.2 diagnostic screening is recorded separately from the prediction layer. The 18-entry panel is **not** a statistically random sample and the observed 17/18 primary-formula presence count is **not** promoted as a general chemistry accuracy claim. Its useful result is a falsifier taxonomy: B2H6 requires a three-centre/electron-deficient gate; PCl5 and SF6 require coordination/reorganization states; KrF2 is a closed-shell false negative of v0.1.

v0.3 adds connected integer two-centre relation graphs with
`sum_j b_ij=d_i`, `b_ij in {0,1,2,3}`. Software controls recover the expected coarse relation-order patterns for H2, F2, O2, N2, H2O, NH3, CH4, CO2, HCN, C2H2, C2H4 and C2H6. Negative controls B2H6, PCl5, SF6 and KrF2 remain explicit failures rather than post-hoc fits.

## Three-centre hyperrelation candidate v0.4

The B2H6 falsifier is addressed by a separate minimal-augmentation gate without changing the frozen two-centre degree law.

- relation load is represented in integer half-units;
- atom target load is `2*d_i`;
- ordinary pair bond order `b` consumes `2*b` half-units on each endpoint;
- symmetric three-centre bridge consumes `1:2:1` half-units on outer:bridge:outer;
- candidates are searched in increasing augmentation order, so a valid 2c graph always wins before any 3c primitive is admitted;
- bridge eligibility is shell-defined: bridge degree `1`, each outer degree `>=2`, with one 3c primitive per bridge centre in v0.4.

Local prototype behavior before branch-CI execution:

- CH4 and H2O remain at augmentation order `0`;
- B2H6 first closes at augmentation order `2`, producing two bridge centres plus four terminal pair bonds;
- the same topology transfers without rule changes to Al2Cl6, Al2Br6 and Ga2Cl6, consistent with independent bridged-dimer structural literature;
- PCl5 and SF6 remain unresolved coordination/reorganization cases;
- KrF2 remains an unresolved closed-shell excitation/polarization case.

`benchmarks/HYPERRELATION_BRIDGE_BENCHMARK_V0_4.json` is explicitly marked `LOCAL_PROTOTYPE_PASS_BRANCH_CI_NOT_RUN`: the external checkout attempt failed because the isolated execution container could not resolve `github.com`. This infrastructure failure is not counted as a model or software PASS/FAIL.

## Coordination / reorganization ladder candidate v0.5

PCl5 and SF6 motivate a distinct heavier-main-group coordination gate. The frozen ground-state relation degree is not overwritten.

For outer s/p occupation `v` and capacity `C`:

- `d0=min(v,C-v)` remains the base state;
- `d*=max(v,C-v)` defines the dual endpoint of the representation interval;
- for `n>=3`, `v>C/2`, and `d0>0`, candidate states are `d_q=d0+2q` up to `d*`;
- second-period N/O/F remain unexpanded in v0.5;
- closed-shell centres remain fail-closed.

Frozen ladders:

- N `(3)`, O `(2)`, F `(1)`;
- P `(3,5)`, S `(2,4,6)`, Cl `(1,3,5,7)`;
- As `(3,5)`, Se `(2,4,6)`, Br `(1,3,5,7)`;
- Kr `(0)`.

For frozen degree-one ligands this produces PCl3/PCl5, SF2/SF4/SF6 and BrF/BrF3/BrF5/BrF7. PCl5 and SF6 are motivating known cases rather than blind validation. BrF5 provides an independent structural cross-check. Unsupported top rungs such as ClF7/BrF7 remain visible `UNVALIDATED_CANDIDATE`s rather than being deleted post hoc.

A parity reduction was identified after freezing v0.5: for neutral centres with monovalent odd-electron ligands, the `+2` sequence largely preserves the ordinary even-electron/paired-electron coordination parity. Therefore the earlier all-integer `d0..d*` null is **REJECTED AS TOO WEAK** and the `+2` ladder is not promoted as independent new physics.

The potentially testable content is narrowed to the shell-derived bounds `d0,d*`, the `n>=3` admission gate, transfer across ligand families, and any independently defined ranking of allowed `q` states. Revised comparison:

- `M0`: parity-only coordination set;
- `M1`: M0 plus shell-derived `d0/d*` bounds and `n>=3` gate;
- `M2`: M1 plus an independent ranking observable.

Promotion requires M1 or M2 to outperform M0 on frozen held-out energetic/structural targets such as sequential bond energies, relative electronic energies, resolved coordination states, or equilibrium structure.

`q` is **MODEL-DEFINED REORGANIZATION METADATA**: it is not oxidation state, orbital occupation, a literal expanded-octet mechanism, or an energy level.

This compound layer remains **MODEL-DEFINED / STRUCTURAL-CANDIDATE / NOT AN ENERGETIC MOLECULAR SOLVER**.

## Molecular extension

The conventional multicentre physics extension remains formalized but not yet implemented as a validated solver:

- multicentre Hamiltonian with explicit nuclei;
- shell reorganization rather than immutable atom-shell identities;
- projected multicentre winding diagnostics separated from Berry phase and 3D exchange topology;
- conventional control sequence remains H2+ followed by H2, HeH+, and LiH.

The compound-relation layer above is a structural candidate interface into this future solver; it does not replace Born-Oppenheimer/electronic-structure controls.

## TIR / PhaseNav / semantic admission

- `kappa = ln(2)/(24*pi)` remains model-defined metadata in the atomic control stack;
- `W_AB` remains a reserved/candidate relation operator until a no-refit observable is defined;
- 36D PhaseNav is treated as a representation interface, not proof of 36 physical dimensions;
- semantic and affective mappings may consume immutable control invariants but may not rewrite them;
- no TIR or affective correction is promoted into the validated atomic or molecular Hamiltonians.

## Documentation contract

`monograph/main.tex` is the primary scientific formalization surface. The full project is structured as one LaTeX textbook with control physics, scalable solvers, spectroscopy, correlation, shell topology, conformal diagnostics, multicentre extension, relational admission, benchmark ledger, equation-to-code map, validation contract, and open gates.

CI workflow: `.github/workflows/monograph-ci.yml`.

Release gate: complete Python test discovery -> repository-structure audit -> full `latexmk` build -> undefined-reference rejection -> PDF/hash artifact.

## Current CI note

The first full-suite textbook CI exposed a real cross-version numerical regression: the historical fixed single-stage Na-Ar DIIS recipe left Al outside the convergence criterion with the current NumPy/SciPy stack. The test and textbook were corrected to make the later **global non-element-specific robust quality ladder** the normative release gate; the old single-stage numbers remain a historical frozen benchmark, not a cross-version contract.

The current `compound-relations-v0.3` branch has no automatic GitHub Actions run recorded yet for the compound relation commits. Branch-level implementation status must therefore not be conflated with CI validation.

## Not claimed

- a validated knot-shell law;
- a topological force term in the Hamiltonian;
- braid-group invariance for unrestricted 3D electron dynamics;
- high-precision spectroscopy across all H-Kr species;
- a validated TIR correction to atomic or molecular energies;
- a validated energetic molecular solver for the compound relation layer;
- literal fractional-electron meaning of the v0.4 half-unit bookkeeping;
- literal expanded-octet or d-orbital mechanism for the v0.5 coordination ladder;
- independent novelty of the v0.5 `+2` parity ladder by itself;
- complete transition-metal, hypervalent, radical or electron-deficient chemistry;
- canonical promotion of the candidate compound-relation layer.
