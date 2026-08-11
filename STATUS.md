# Resonant Chemistry Status

## v0.1 — Atom foundations

State: **CANDIDATE / IMPLEMENTED ON WORKING BRANCH**

Implemented:
- atomic identity `(Z,N,q,A,N_e)`;
- elements H..Kr;
- baseline configurations through Kr with neutral Cr/Cu exceptions;
- analytic one-electron hydrogenic benchmark;
- independent finite-difference radial Schrödinger eigensolver;
- TIR `kappa` carried as metadata only;
- reserved chemistry-level `W_AB` interface, not yet given physical dynamics;
- interactive self-contained HTML atom builder;
- LaTeX monograph Chapter 1;
- unit-test suite.

Not claimed:
- ab-initio multi-electron energy solver;
- Hartree-Fock, DFT or CI;
- chemistry-level holonomy validation;
- new periodic-table predictions;
- any replacement of Coulomb/QM/QED control physics.

Next gate:
1. validate numerical radial convergence across grid sizes;
2. expose radial probability in the interactive HTML;
3. add Hartree-Fock control for He and H2 as the first many-electron layer;
4. implement active orbital subspaces;
5. derive overlap matrix and chemistry-level `W_AB`;
6. begin H2 vs He2 bond benchmark.
