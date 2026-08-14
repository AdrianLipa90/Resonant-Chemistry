# Resonant Chemistry Status

## 2026-08-13 - shell topology / compound relation checkpoint

State: **CONTROL STACK IMPLEMENTED / SHELL-TOPOLOGY CANDIDATE / COMPOUND-RELATION CANDIDATE / CANON NOT PROMOTED**

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

A non-energetic main-group bridge from the atomic bookkeeping to compounds is now implemented as a candidate layer.

Frozen v0.1 rule:

- nuclei remain explicit and integer-Z;
- outer s/p shell relation degree `d=min(v,C-v)` with `C=2` for `n=1` and `C=8` thereafter;
- binary endpoint balance `n_A*d_A = n_B*d_B`;
- 231 H-Kr main-group binary skeleton candidates, with Sc-Zn deliberately fail-closed;
- particle-hole complementarity retained as representation metadata, not bond energy.

Post-blind v0.2 diagnostic screening is recorded separately from the prediction layer. The 18-entry panel is **not** a statistically random sample and the observed 17/18 primary-formula presence count is **not** promoted as a general chemistry accuracy claim. Its useful result is a falsifier taxonomy: B2H6 requires a three-centre/electron-deficient gate; PCl5 and SF6 require coordination/reorganization states; KrF2 is a closed-shell false negative of v0.1.

v0.3 adds connected integer two-centre relation graphs with
`sum_j b_ij=d_i`, `b_ij in {0,1,2,3}`. Software controls recover the expected coarse relation-order patterns for H2, F2, O2, N2, H2O, NH3, CH4, CO2, HCN, C2H2, C2H4 and C2H6. Negative controls B2H6, PCl5, SF6 and KrF2 remain explicit failures rather than post-hoc fits.

This layer is **MODEL-DEFINED / SOFTWARE-TESTED / NOT AN ENERGETIC MOLECULAR SOLVER**.

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

## Not claimed

- a validated knot-shell law;
- a topological force term in the Hamiltonian;
- braid-group invariance for unrestricted 3D electron dynamics;
- high-precision spectroscopy across all H-Kr species;
- a validated TIR correction to atomic or molecular energies;
- a validated energetic molecular solver for the compound relation layer;
- complete transition-metal, hypervalent, radical or electron-deficient chemistry;
- canonical promotion of the candidate compound-relation layer.
