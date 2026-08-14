# Relation Graph Gate v0.3

## Status

**MODEL-DEFINED / SOFTWARE-TESTED / NOT AN ENERGETIC SOLVER**

v0.3 keeps the v0.1 shell relation degree frozen and asks a stronger structural
question: can a composition be represented by one connected integer two-centre
relation graph?

For each atom `i`,

\[
\sum_{j\ne i} b_{ij}=d_i,
\qquad
b_{ij}\in\{0,1,2,3\}.
\]

No element-specific bond-order table is supplied.

For the software-control set, the degree constraints recover a unique coarse
symmetry-quotient graph for:

- H2: single relation;
- F2: single relation;
- O2: double relation;
- N2: triple relation;
- H2O: two single relations;
- NH3: three single relations;
- CH4: four single relations;
- CO2: two double relations;
- HCN: single + triple;
- C2H2: C-C triple + two C-H singles;
- C2H4: C-C double + four C-H singles;
- C2H6: C-C single + six C-H singles.

Negative controls remain failures rather than being repaired post hoc:

- B2H6 -> no connected two-centre graph: a three-centre/electron-deficient gate is required;
- PCl5 and SF6 -> no graph: a coordination/reorganization state is required;
- KrF2 -> no graph: a closed-shell excitation/polarization gate is required.

The current graph signature removes obvious permutations of equivalent atoms
for these small regression controls.  It is not claimed to be a complete graph
isomorphism canonicalizer or constitutional-isomer enumerator.
