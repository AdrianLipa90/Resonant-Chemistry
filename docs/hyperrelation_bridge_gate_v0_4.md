# Hyperrelation bridge gate v0.4

## Scope

This gate keeps the frozen two-centre relation law unchanged and adds one
separate candidate primitive for compositions that cannot form a connected
2c relation graph.

Relation load is represented in integer half-units:

- atom target: `2*d_i`, where `d_i` is the frozen shell relation degree;
- ordinary pair bond of order `b`: `2*b` half-units on each endpoint;
- symmetric 3-centre bridge `(outer, bridge, outer)`: `1 + 2 + 1` half-units.

The 1:2:1 bookkeeping is representation metadata. It must not be read as a
literal partition of electron density or a bond-energy model.

## Minimal-augmentation principle

Candidates are searched by augmentation order `q = 0,1,2,...` and the search
stops at the first `q` that admits a connected load-conserving graph.

Therefore:

1. ordinary 2c chemistry remains preferred whenever it already closes;
2. a 3c primitive cannot silently replace a valid simpler graph;
3. the number of bridges is predicted by the smallest augmentation necessary
   for closure, rather than fitted after seeing a structure.

Bridge eligibility is shell-defined rather than element-labelled:

- bridge centre: relation degree `1`;
- both outer centres: relation degree `>= 2`;
- one 3c primitive per bridge centre in v0.4.

## Primary falsifier rescue: B2H6

The v0.3 pair graph rejects B2H6 as a connected two-centre graph. Under the
v0.4 minimal augmentation, the first admissible quotient graph occurs at
`q=2` and contains:

- two symmetric 3c bridge centres;
- four ordinary terminal pair bonds;
- exact conservation of every atom's frozen relation load.

This matches the established qualitative bonding picture of diborane with
bridging hydrogen atoms and 3-centre interactions. The external structure is
used as a validation target, not as an element-specific rule in the solver.

Primary research references:

- J. Chem. Theory Comput. 2014, DOI `10.1021/ct500490b` — electronic-density
  analysis explicitly discusses the 3-centre/two-electron bonding pattern in
  B2H6.
- J. Phys. Chem. A 2024, DOI `10.1021/acs.jpca.4c03492` — modern electronic
  force-density analysis of terminal and bridging B-H interactions in
  diborane.

## Transfer test: group-13 halide dimers

Without changing the rule, the same topology is generated for:

- Al2Cl6;
- Al2Br6;
- Ga2Cl6.

For each composition the minimal candidate has two bridge centres and four
terminal pair bonds.

Independent experimental/theoretical literature describes Al2Cl6 and Al2Br6
as bridged dimers and reports halogen-bridged Ga2Cl6:

- J. Phys. Chem. A 1999, DOI `10.1021/jp9842042` — gas-phase electron
  diffraction plus ab-initio structures of Al2Cl6 and Al2Br6;
- J. Chem. Soc., Faraday Trans. 2 1976, DOI `10.1039/F29767200539` —
  photoelectron spectra and ab-initio calculations of halogen-bridged
  Al2Cl6, Al2Br6 and Ga2Cl6.

This transfer is more informative than reproducing diborane alone because the
bridge atom changes from H to a halogen while the solver still receives only
shell relation degrees and nuclear identities.

## Boundaries deliberately left open

The gate does **not** fix the other v0.3 falsifiers:

- PCl5 remains unresolved: coordination/reorganization state required;
- SF6 remains unresolved: coordination/reorganization state required;
- KrF2 remains unresolved: closed-shell excitation/polarization required.

This separation is intentional. Three-centre bridging, higher coordination,
and closed-shell activation remain distinct candidate operators until
independent tests justify a unification.

## Epistemic status

`MODEL_DEFINED / SOFTWARE-CANDIDATE / EXTERNAL-STRUCTURE-CROSSCHECKED / NOT_ENERGETICALLY_VALIDATED`

No bond energy, equilibrium geometry, formation enthalpy, reaction pathway or
material stability is predicted by v0.4.
