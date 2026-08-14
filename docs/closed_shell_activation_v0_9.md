# Closed-shell activation gate v0.9

## Purpose

The frozen v0.1 relation degree assigns a completely filled outer shell
`d=0`.  KrF2 is therefore an explicit false negative of the ordinary
nearest-closed-shell relation graph.  v0.9 introduces a separate structural
candidate gate without changing v0.1, v0.4, or v0.5.

The key anti-fit decision is that **krypton is not special-cased**.

## Generic shell rule

A centre is eligible when its current H--Kr control bookkeeping gives:

- completely filled outer `s/p` shell;
- frozen relation degree `d=0`;
- principal shell `n >= 2`.

A ligand is eligible when it has:

- frozen relation degree `1`;
- `ABOVE_HALF` shell branch.

Within the present H--Kr main-group domain these conditions mechanically give:

- centres: `Ne`, `Ar`, `Kr`;
- ligands: `F`, `Cl`, `Br`.

Hence the frozen v0.9 structural atlas contains nine candidates:

`NeF2`, `NeCl2`, `NeBr2`, `ArF2`, `ArCl2`, `ArBr2`, `KrF2`, `KrCl2`, `KrBr2`.

The unfamiliar members are deliberately retained.  The structural generator is
not allowed to delete a candidate after later energetic evidence is opened.

## Relation primitive

v0.9 assigns one representation-level activation index

`q_cs = 1`

and one symmetric candidate relation

`ligand -- centre -- ligand`

with effective relation degree `2` and topology label
`SYMMETRIC_THREE_CENTRE_FOUR_ELECTRON_CANDIDATE`.

This bookkeeping is inspired by the established three-centre bonding description
of KrF2 but does **not** assert literal fractional electrons, an excitation
energy, an oxidation state, or a new Hamiltonian term.

## Conventional physical control

For each candidate the preregistered whole-pair loss channel is

`XY2 -> X + Y2`.

A separate conventional quantum-chemistry calculation must determine:

1. whether the candidate geometry optimizes to a harmonic local minimum;
2. the sign and magnitude of the dissociation energy under one common method
   policy;
3. whether the electronic structure is genuinely compatible with the proposed
   three-centre representation.

A structurally generated candidate may therefore receive a negative energetic
label without being deleted from the prediction ledger.

## KrF2 motivation and provenance

KrF2 is **motivation, not blind validation** for v0.9.

Primary sources already entered in `monograph/bibliography/references.bib`:

- `brundle_jones_1971_krf2_photoelectron`, DOI `10.1039/C29710001198`:
  valence photoelectron spectrum and molecular-orbital ordering;
- `collins_cruickshank_breeze_1974_krf2_bonding`, DOI
  `10.1039/F29747000393`: ab initio orbital contours explicitly illustrating
  the three-centre bond;
- `hoffman_swafford_cave_1998_krf2`, DOI `10.1063/1.477768`: CCSD(T)
  treatment of linear ground-state KrF2 and dissociation energetics;
- `lehmann_dixon_schrobilgen_2001_krf2`, DOI `10.1021/ic001167w`:
  low-temperature X-ray structures and theoretical treatment.

Additional historical synthesis/structure/electronic-structure records are also
kept in the central bibliography.

## Held-out rule

The other eight atlas members are frozen as `UNVALIDATED_STRUCTURAL_CANDIDATE`
in the v0.9 benchmark artifact.  Their external labels are not used to modify
the generator.

## Epistemic status

`MODEL_DEFINED / STRUCTURAL_CANDIDATE / KRF2_MOTIVATED / NOT_BLIND_VALIDATED / NOT_ENERGETICALLY_VALIDATED`
