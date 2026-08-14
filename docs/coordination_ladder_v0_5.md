# Coordination / reorganization ladder v0.5

## Motivation

The frozen nearest-closed-shell relation degree succeeds as a low-coordinate
skeleton but leaves PCl5 and SF6 as explicit v0.3 failures. v0.5 introduces a
separate **discrete coordination/reorganization representation**, without
changing v0.1 or reinterpreting nuclear charge.

For an outer s/p shell with occupation `v` and closed-shell capacity `C`:

\[
d_0 = \min(v,C-v),\qquad d_* = \max(v,C-v).
\]

For an above-half main-group centre with principal shell `n >= 3`, v0.5 admits

\[
d_q=d_0+2q
\]

until `d_q=d_*`.

`q` counts candidate pair-reorganization steps. It is **not** an oxidation
state, excitation quantum number, d-orbital occupation, bond order, or energy.
The rule is representation-level bookkeeping motivated by the need for a
separate higher-coordination gate.

## Frozen ladder produced by the rule

Second period remains unexpanded:

- N: `3`
- O: `2`
- F: `1`

Heavier above-half p-block centres:

- P: `3 -> 5`
- S: `2 -> 4 -> 6`
- Cl: `1 -> 3 -> 5 -> 7`
- As: `3 -> 5`
- Se: `2 -> 4 -> 6`
- Br: `1 -> 3 -> 5 -> 7`

Closed-shell Kr remains `0` and is not activated by this gate.

For a ligand whose frozen relation degree is one, the star-skeleton generator
therefore produces, for example:

- P/Cl: PCl3, PCl5
- S/F: SF2, SF4, SF6
- Br/F: BrF, BrF3, BrF5, BrF7

The last example is intentionally important: v0.5 does **not** delete a high-q
candidate merely because it is not already supported by the present validation
set. Unsupported rungs remain visible falsifiable candidates.

## External structure cross-checks

These checks are not blind with respect to PCl5/SF6 because those molecules
motivated the gate. They are used only to establish that the discrete ladder is
aligned with known higher-coordinate chemistry before broader testing.

Primary sources:

- PCl5: W. J. Adams and L. S. Bartell, *Journal of Molecular Structure* 8
  (1971) 23-30, DOI `10.1016/0022-2860(71)80038-8`. Gas-phase electron
  diffraction gives the five-coordinate trigonal-bipyramidal molecule.
- SFn: *J. Phys. Chem. A* (2009), DOI `10.1021/jp901949b`. Multireference
  calculations analyze the SFn sequence through SF6 and explicitly treat
  pair recoupling as a mechanism enabling higher coordination.
- BrF5: *J. Chem. Soc. D* (1971), DOI `10.1039/C29710001567`. Gas-phase
  electron diffraction combined with rotational constants determines the
  molecular structure of BrF5.

The literature does not license the entire ladder. In particular, the top
`q=3` rungs generated for Cl and Br remain **UNVALIDATED** in this gate.

## Important reduction: +2 parity is not yet a new physical law

After freezing v0.5, the `+2` structure was compared with ordinary electron
counting. For a neutral centre bound to monovalent halogen-like ligands, adding
one ligand changes the valence-electron count by an odd number. Consequently,
closed-shell neutral candidates preserve one coordination-number parity.

Therefore the sequence `d0, d0+2, ...` is at least partly an alternative
representation of familiar even-electron/paired-electron parity. It must **not**
be advertised as an independently validated new law merely because PCl5, SF4,
SF6 or BrF5 lie on the ladder.

This observation invalidates the originally proposed weak null model that
allowed every integer coordination from `d0` to `d*`: such a null mixes
closed-shell rungs with odd-electron/radical rungs and would make the candidate
look artificially predictive.

## What remains genuinely testable

The potentially nontrivial content of v0.5 is now narrowed to:

1. the shell-derived lower bound `d0`;
2. the shell-derived upper endpoint `d*`;
3. the explicit `n >= 3` admission gate;
4. whether a particular allowed `q` state is energetically or structurally
   stabilized;
5. whether the same representation transfers across ligand families without
   element-specific fitting.

A fair null must preserve electron parity. Future testing should compare the
candidate against a **parity-matched null** and use independent observables such
as sequential bond energies, relative electronic energies, experimentally
resolved coordination states, or equilibrium structures.

The 2009 multireference SFn study is particularly suitable because it reports
sequential bonding energetics and electronic reorganization across the series,
not merely the existence of SF4/SF6.

## Why n >= 3 is an explicit model gate

v0.5 deliberately keeps second-period N/O/F on their frozen base relation
degrees while allowing the reorganization ladder only from principal shell 3
upward. This is a model choice, not a theorem. It prevents P/S/Cl behavior from
being silently projected back onto their second-period analogues and gives a
clean falsification target for future quantum-chemical comparison.

## Revised next validation gate

Freeze a parity-matched held-out set before scoring. For each centre/ligand
family, retain all candidate rungs and record independent energetic/structural
observables. Do not remove unsupported high-q rungs after the screen.

The next model comparison is:

- `M0`: parity-only coordination set;
- `M1`: parity + v0.5 shell bounds (`d0..d*`) + `n>=3` gate;
- `M2`: M1 plus an independently defined ranking observable (not fitted to the
  target family).

v0.5 can only be promoted above bookkeeping if M1 or M2 outperforms M0 on a
frozen held-out set.

## Epistemic status

`MODEL_DEFINED / MOTIVATED_BY_KNOWN_FALSIFIERS / PARITY_REDUCTION_IDENTIFIED / NOT_BLIND_VALIDATED / NOT_ENERGETICALLY_VALIDATED`
