# Competing relational-state ensemble v0.13

## Core change

Earlier compound gates often produced one structural candidate from a given
shell relation.  The closed-shell XY2 track demonstrated why that is too
restrictive: **composition does not determine electronic topology**.

KrF2 has an established activated three-centre bonding description, while
NeCl2, NeBr2, ArBr2 and KrCl2-type reference literature contains weak
rare-gas/halogen complexes or van der Waals isomers at the same broad `XY2`
stoichiometric level.

v0.13 therefore changes the representation from

`composition -> one candidate graph`

to

`composition -> unranked ensemble of competing relational states -> physical admission`.

This does not erase v0.9.  The v0.9 activated branch remains one member of the
larger state ensemble.

## Frozen closed-shell XY2 ensemble

Every one of the nine v0.9 compositions receives exactly the same three state
candidates:

### `ACTIVATED_LINEAR_3C4E`

- topology family: `ACTIVATED_THREE_CENTRE_FOUR_ELECTRON`;
- seed: linear ligand--centre--ligand;
- source: the v0.9 closed-shell activation branch.

### `WEAK_COMPLEX_LINEAR_END_ON`

- topology family: `WEAK_COMPLEX_X_DOT_LIGAND_DIMER`;
- seed: linear centre--ligand--ligand;
- source: v0.13 competing weak-complex branch.

### `WEAK_COMPLEX_T_SHAPED`

- same weak-complex topology family;
- seed: centre approaching the side of the ligand dimer;
- source: v0.13 competing weak-complex branch.

The nine compositions therefore become 27 state candidates.

## No prior ranking

Every candidate stores

`prior_rank = None`

and

`prior_probability = None`.

The implementation rejects attempts to assign those fields inside v0.13.
Known KrF2/VDW examples are deliberately **not** converted into priors.

This is important because the currently opened reference set is small,
chemically biased, and already used to discover the topology ambiguity.

## Admission

The state ensemble itself makes no stability decision.

Candidate states are intended to be consumed by two already-separated physical
interfaces:

1. conventional energetic/local-minimum control (v0.8 family);
2. multi-diagnostic electronic-topology admission (v0.10 family).

The physical layer may choose one state, several metastable states, or reject
all enumerated states.

## Why this is useful beyond noble-gas XY2

The architecture generalizes the lessons of the preceding gates:

- B2H6 required a 3-centre bridge branch rather than rewriting the ordinary 2c
  relation law;
- PCl5/SF6 required higher coordination branches rather than deleting the base
  state;
- closed-shell XY2 needs activated and weak-complex branches to coexist until
  physical admission.

Thus a compound can be represented as a **competition among relational modes**
rather than a single immutable atom-by-atom bond assignment.

## Bibliography

No new external source was introduced to define v0.13.  It uses source classes
already entered in the live modular bibliography during v0.9/v0.10.  The
`source-used -> bibliography-in-same-iteration` invariant therefore remains
satisfied without adding a duplicate record.

## Epistemic status

`IMPLEMENTED_MODEL_ARCHITECTURE_CANDIDATE / UNRANKED / PHYSICAL_ADMISSION_NOT_YET_RUN / CANON_NOT_PROMOTED`
