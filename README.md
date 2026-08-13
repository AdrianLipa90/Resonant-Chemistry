# Resonant-Chemistry

Resonant Chemistry is a control-first research programme for atomic, shell, and eventually molecular structure. Standard quantum chemistry remains the physical baseline. Relational/TIR, PhaseNav, conformal, topological, semantic, and affective layers are admitted only at the epistemic status actually supported by derivation and validation.

## Current working line

Working branch: `shell-nbody-topology-v0.1`.

The primary formalization surface is now the **complete LaTeX textbook** in `monograph/`. Markdown notes are supplemental; important equations, assumptions, negative results, validation rules, and open gates belong in the textbook.

Build target:

```text
monograph/main.tex -> full project textbook PDF
```

GitHub Actions workflow `.github/workflows/monograph-ci.yml` runs the full Python test discovery, repository-structure audit, LaTeX build, undefined-reference gate, hashes, and PDF artifact upload.

## Implemented control ladder

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
- carbon radial-p, s, d, sparse multichannel, and virtual-s correlation diagnostics;
- shell-level N-body topology primitives with explicit nuclear Coulomb centres;
- shell particle-hole symmetry primitives independent of atom labels;
- conformal knot diagnostics retained as a candidate, with the failed direct knot-gap/atom-gap comparison preserved as a negative control.

The current carbon correlation frontier is state-averaged orbital optimization/MCSCF over a common 3P, 1D, 1S objective without experimental term-energy fitting.

## Correct topology comparison level

The candidate comparison is **not `knot <-> atom`**. The object is a shell/subshell occupation `(n,l,k)` around explicit nuclear attractive Coulomb centres. For a shell of orbital angular momentum `l`,

```text
capacity C_l = 2(2l+1)
particle-hole partner k* = C_l-k
self-dual half filling k = 2l+1
```

Thus `p1<->p5`, `p2<->p4`, `p3<->p3`; similarly `d5` and `f7` are self-dual. In unrestricted 3D, identical-particle exchange topology is permutation-based; braid-group language is reserved for effective 2D/constrained sectors. Projected windings are diagnostics, not new forces.

## Repository map

- `monograph/` - primary LaTeX textbook and full-PDF build target.
- `reschem/` - executable physical and candidate representation modules.
- `tests/` - deterministic/regression tests.
- `benchmarks/` - machine-readable numerical checkpoints and candidate receipts.
- `semantic_cards/` - state-derived physical records plus explicitly separated interpretive fields.
- `THEORY/` and `docs/` - supplemental formal/operational notes.
- `web/` - interactive dashboards and explorers.
- `.github/workflows/` - CI and reproducibility gates.

## Claim taxonomy

- **ESTABLISHED CONTROL** - standard mathematics/physics used as baseline.
- **MODEL-DEFINED** - explicitly defined project quantity without implied physical promotion.
- **CANDIDATE** - proposed relation awaiting discriminating tests.
- **IMPLEMENTED** - executable implementation exists.
- **TESTED** - passed the stated software/numerical gate.
- **VALIDATED CONTROL** - conventional model passed its frozen control benchmark.
- **CANON** - promoted only by an explicit project decision with provenance.

Implementation does not imply validation; a numerical match does not establish ontology; a historical receipt is not current runtime evidence.
