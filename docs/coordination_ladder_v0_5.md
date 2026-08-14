# Coordination / reorganization ladder v0.5

## Motivation

The frozen nearest-closed-shell relation degree succeeds as a low-coordinate
skeleton but leaves PCl5 and SF6 as explicit v0.3 failures. v0.5 introduces a
separate **discrete coordination/reorganization candidate**, without changing
v0.1 or reinterpreting nuclear charge.

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
set. Unsupported rungs remain visible falsifiable predictions.

## External structure cross-checks

These checks are not blind with respect to PCl5/SF6 because those molecules
motivated the gate. They are used only to establish that the discrete ladder is
at least aligned with known higher-coordinate chemistry before broader held-out
testing.

Primary sources:

- PCl5: W. J. Adams and L. S. Bartell, *Journal of Molecular Structure* 8
  (1971) 23-30, DOI `10.1016/0022-2860(71)80038-8`. Gas-phase electron
  diffraction gives the five-coordinate trigonal-bipyramidal molecule.
- SFn: *J. Phys. Chem. A* (2009), DOI `10.1021/jp901949b`. Multireference
  calculations analyze the SFn sequence through SF6 and explicitly treat
  pair recoupling as the mechanism enabling higher coordination.
- BrF5: *J. Chem. Soc. D* (1971), DOI `10.1039/C29710001567`. Gas-phase
  electron diffraction combined with rotational constants determines the
  molecular structure of BrF5.

The literature does not license the entire ladder. In particular, the top
`q=3` rungs generated for Cl and Br remain **UNVALIDATED** in this gate.

## Why n >= 3 is an explicit model gate

v0.5 deliberately keeps second-period N/O/F on their frozen base relation
degrees while allowing the reorganization ladder only from principal shell 3
upward. This is a model choice, not a theorem. It prevents P/S/Cl behavior from
being silently projected back onto their second-period analogues and gives a
clean falsification target for future quantum-chemical comparison.

## Next validation gate

Freeze the full H-Kr coordination ladder before further literature/database
screening. Then score each generated monovalent-ligand rung as:

- independently realized;
- computationally supported only;
- unresolved;
- falsified under a preregistered existence/stability criterion.

Do not remove unsupported high-q rungs after the screen. Compare the ladder
against a null model that permits every coordination number from `d0` through
`d*`; the `+2` parity structure only earns status if it predicts the observed
families better than that null.

## Epistemic status

`MODEL_DEFINED / MOTIVATED_BY_KNOWN_FALSIFIERS / NOT_BLIND_VALIDATED / NOT_ENERGETICALLY_VALIDATED`
