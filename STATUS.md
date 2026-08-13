# Resonant Chemistry Status

## 2026-08-13 - shell topology / full textbook checkpoint

State: **WORKING BRANCH / CONTROL STACK IMPLEMENTED / SHELL-TOPOLOGY CANDIDATE / CANON NOT PROMOTED**

Working branch: `shell-nbody-topology-v0.1`.

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

## Molecular extension

Formalized but not yet implemented as a validated solver:

- multicentre Hamiltonian with explicit nuclei;
- shell reorganization rather than immutable atom-shell identities;
- projected multicentre winding diagnostics separated from Berry phase and 3D exchange topology;
- first implementation target: H2+ control, followed by H2, HeH+, and LiH.

## TIR / PhaseNav / semantic admission

- `kappa = ln(2)/(24*pi)` remains model-defined metadata in the atomic control stack;
- `W_AB` remains a reserved/candidate relation operator until a no-refit observable is defined;
- 36D PhaseNav is treated as a representation interface, not proof of 36 physical dimensions;
- semantic and affective mappings may consume immutable control invariants but may not rewrite them;
- no TIR or affective correction is promoted into the validated atomic Hamiltonians.

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
- a validated TIR correction to atomic energies;
- a molecular topology solver beyond the current formal specification;
- canonical promotion of the working-branch candidate layer.
