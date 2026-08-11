# Resonant-Chemistry

Resonant Chemistry is an exploratory chemistry formalism built on top of standard quantum chemistry and the Fundamental Theory of Informational Relations (TIR).

## Current status

The repository is in **foundational development**. Standard atomic physics is the control layer. TIR-derived relational objects are introduced only where they can be defined without replacing established quantum mechanics.

Current working branch: `atom-foundations-v0.1`.

## First milestone: build the atom

The first implementation defines an atom by nuclear composition `(Z,N)`, charge `q`, electron count `N_e=Z-q`, a fermionic electronic state space, and a Hamiltonian control layer. A lightweight solver provides deterministic atomic bookkeeping and exact non-relativistic hydrogenic energies for one-electron species. Multi-electron energies are intentionally not guessed in v0.1.

## Layout

- `THEORY/02_ATOM_FORMALISM.md` — formal definition and epistemic boundaries.
- `reschem/atom.py` — atom data model and electron configuration engine.
- `solver.py` — command-line atomic solver.
- `web/atom_builder.html` — self-contained interactive atom builder.
- `monograph/` — LaTeX monograph source; Chapter 1 is the atom.
- `tests/` — deterministic unit tests.

## Claim taxonomy

- **ESTABLISHED** — standard mathematics/physics used as control.
- **TIR-DEFINED** — explicit definition inherited or adapted from TIR.
- **CANDIDATE** — new ResChem construction awaiting discriminating tests.
- **TESTED** — passed an explicit test without post-hoc alteration.
- **CANON** — promoted only after provenance and validation.
