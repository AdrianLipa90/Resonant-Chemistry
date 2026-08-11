# Resonant Chemistry Status

## v0.1 — Atom foundations

State: **CANDIDATE / IMPLEMENTED ON WORKING BRANCH**

Implemented:
- atomic identity `(Z,N,q,A,N_e)`;
- elements H..Kr;
- baseline configurations through Kr with neutral Cr/Cu exceptions;
- one-electron hydrogenic benchmark;
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
1. run tests;
2. add numerical radial Schrödinger solver as an independent hydrogenic cross-check;
3. implement active orbital subspaces;
4. derive overlap matrix and chemistry-level `W_AB`;
5. begin H2 vs He2 bond benchmark.
