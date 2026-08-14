# Resonant-Chemistry

Resonant Chemistry is a control-first research programme for atomic, shell, compound, and molecular structure. Standard quantum chemistry remains the physical baseline. Relational/TIR, PhaseNav, conformal, topological, semantic, and affective layers are admitted only at the epistemic status actually supported by derivation and validation.

## Source of truth and current working line

The repository default branch **`main` is the project Source of Truth**. Research increments may be developed on dedicated branches, but branch state is not canon until merged. Documentation and build gates must therefore describe and validate `main`, not a historical working branch.

The primary formalization surface is the **complete LaTeX textbook** in `monograph/`. Markdown notes are supplemental; important equations, assumptions, negative results, validation rules, and open gates belong in the textbook or are explicitly cross-referenced from it.

Build target:

```text
monograph/main.tex -> full project textbook PDF
```

The repository keeps separate software, numerical, bibliography, and manuscript gates. A successful build or unit test is not a scientific promotion.

## Implemented control and candidate ladder

The repository currently contains:

- atomic identity and electron configurations through Kr, including neutral Cr/Cu exceptions;
- analytic and numerical hydrogenic controls;
- helium variational, RHF, finite-CI, and state-invariant controls;
- lithium open-shell UHF;
- blind/reference-isolated s-shell and multi-l Hartree-Fock batches;
- global non-element-specific DIIS/quality stabilization and H-Kr control coverage;
- equivalent-shell p/d LS multiplets and weak-coupling J ordering;
- period-2 atom-specific F^k / Pauli spin-orbit spectroscopy controls;
- finite active-space and correlated spin-orbit CI;
- carbon radial-p, s, d, sparse multichannel, virtual-s, and state-averaged active-external orbital-relaxation diagnostics;
- shell-level N-body topology primitives with explicit nuclear Coulomb centres;
- shell particle-hole symmetry primitives independent of atom labels;
- conformal knot diagnostics retained as a candidate, with the failed direct knot-gap/atom-gap comparison preserved as a negative control;
- compound-relation gates v0.1-v0.12 with explicit nulls, falsifiers, energetic contracts, and failed/non-promoted paths retained;
- v0.13 competing-state architecture, in which a composition carries an **unranked ensemble** of relational-state candidates until conventional physical admission;
- v0.14A/A1 common molecular relaxation screening under one frozen B97M-V/VV10/def2-TZVPD policy, with the numerical grid amendment recorded separately from the original preregistration.

## Current molecular checkpoint: v0.14A1

The frozen v0.14A1 screen defines nine closed-shell `XY2` compositions and five common starts per formula: three activated-linear starts, one weak end-on start, and one weak T-shaped start.

Current durable execution state:

- common F2/Cl2/Br2 dimer prepass: recorded;
- backend smoke after the global A1 pruning amendment: recorded;
- eight of nine formula receipts recovered and persisted;
- **40 of 45 frozen XY2 starts have durable first-attempt evidence**;
- `ArBr2` remains `MISSING_EXECUTION`, not a negative chemical result;
- no Hessian/local-minimum admission has been run;
- no geometry-only 3c4e/VDW label is admitted;
- no lowest-screening-energy result is called a validated ground state.

The next molecular gate is therefore to complete the missing `ArBr2` execution under the same frozen policy. Only after **9/9 formula receipts and 45/45 starts** are durably present may a separately preregistered Hessian/local-minimum gate be opened.

## Current atomic/correlation frontier

The first state-averaged active-external radial-p relaxation gate for carbon has already produced a variationally informative direction under its frozen equal-weight objective. The next correlation extension is a multidimensional state-averaged orbital optimizer/MCSCF-type control, still without experimental term-energy fitting.

The v0.11/v0.12 atomic finite-difference activation-control path remains a useful negative/numerical diagnostic but is **not admitted as a molecular chemistry classifier**.

## Correct topology comparison level

The candidate comparison is **not `knot <-> atom`**. The object is a shell/subshell occupation `(n,l,k)` around explicit nuclear attractive Coulomb centres. For a shell of orbital angular momentum `l`,

```text
capacity C_l = 2(2l+1)
particle-hole partner k* = C_l-k
self-dual half filling k = 2l+1
```

Thus `p1<->p5`, `p2<->p4`, `p3<->p3`; similarly `d5` and `f7` are self-dual. In unrestricted 3D, identical-particle exchange topology is permutation-based; braid-group language is reserved for effective 2D/constrained sectors. Projected windings are diagnostics, not new forces.

For molecular `XY2` candidates, **stoichiometry and geometry seed are not electronic topology verdicts**. v0.10 requires independent diagnostic families before a 3c4e/VDW topology label can be admitted.

## Repository map

- `monograph/` - primary LaTeX textbook and full-PDF build target.
- `reschem/` - executable physical and candidate-representation modules.
- `tests/` - deterministic/regression tests.
- `benchmarks/` - machine-readable numerical checkpoints, preregistrations, and receipts.
- `semantic_cards/` - state-derived physical records plus explicitly separated interpretive fields.
- `THEORY/` and `docs/` - supplemental formal/operational notes.
- `web/` - interactive dashboards and explorers.
- `.github/workflows/` - CI, execution, and reproducibility gates.

The live bibliography is modular under `monograph/bibliography/` and currently includes the active ledger, historical compound provenance, and molecular-screening methods/software sources.

## Claim taxonomy

- **ESTABLISHED CONTROL** - standard mathematics/physics used as baseline.
- **MODEL-DEFINED** - explicitly defined project quantity without implied physical promotion.
- **CANDIDATE** - proposed relation awaiting discriminating tests.
- **IMPLEMENTED** - executable implementation exists.
- **TESTED** - passed the stated software/numerical gate.
- **VALIDATED CONTROL** - conventional model passed its frozen control benchmark.
- **CANON** - promoted only by an explicit project decision with provenance.

Implementation does not imply validation; a numerical match does not establish ontology; a historical receipt is not current runtime evidence; an execution timeout or missing receipt is not a chemical falsification.
