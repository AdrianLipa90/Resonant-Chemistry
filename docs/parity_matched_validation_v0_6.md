# Parity-matched coordination validation v0.6

## Purpose

v0.5 introduced a heavier-main-group coordination ladder

\[
d_q=d_0+2q,
\]

with an explicit principal-shell gate `n>=3`.  The first energetic comparison
must determine whether this shell gate contributes information beyond a much
simpler parity-only null.

## M0: parity-only null

M0 uses the same base and dual shell bounds as v0.5 but removes the principal
shell gate.  Every above-half non-closed main-group centre is allowed the same
`+2` progression.

For example:

- N: `(3,5)` under M0, versus `(3)` under M1;
- O: `(2,4,6)` under M0, versus `(2)` under M1;
- P: `(3,5)` under both;
- S: `(2,4,6)` under both.

This is deliberately a strong null because it preserves the electron-parity
structure that motivated the v0.5 self-critique.

## SF_n energetic test

Woon and Dunning, *J. Phys. Chem. A* **113** (2009) 7915-7926,
DOI `10.1021/jp901949b`, report sequential dissociation energies for the SF_n
series.  The frozen values used here are:

| dissociation | D0 kcal/mol |
|---|---:|
| SF2 -> SF + F | 89.5 |
| SF3 -> SF2 + F | 54.5 |
| SF4 -> SF3 + F | 96.2 |
| SF5 -> SF4 + F | 39.2 |
| SF6 -> SF5 + F | 105.6 |

On `n=2..6`, M0 labels even n as the high-energy class.  M1 labels sulfur
coordination rungs `(2,4,6)` as the high-energy class.  These labels are
identical.

The pairwise rank AUC is therefore:

- M0: `1.0`;
- M1: `1.0`;
- incremental `Delta AUC = 0.0`.

Mean D0 is 97.1 kcal/mol for the even/rung class and 46.85 kcal/mol for the
odd/intermediate class.

**Verdict:** the SF_n energetic alternation does not validate an incremental
shell-ladder effect.  It is already captured by the parity-only null.

## Retrospective period-gate sanity check

The same primary paper explicitly contrasts stable hypervalent third-period
species with second-period analogues, noting stable PF5 and SF6 while the
corresponding NF5 and OF6 species have not been observed.

This four-entry panel was already known during development, so it is not blind
validation.  It is only a logical sanity check of the explicit `n>=3` gate.

- M0 parity-only predicts all four high-coordinate candidates -> `2/4` correct.
- M1 shell gate blocks NF5 and OF6 while permitting PF5 and SF6 -> `4/4` correct.

That result is encouraging but cannot be used for promotion because the labels
were not held out.

## Next real held-out test

Freeze a ligand-family panel **before** inspecting realization labels.  Compare:

- M0: parity-only shell bounds;
- M1: parity + principal-shell gate;
- M2: M1 plus an independently defined energetic/reorganization descriptor.

The held-out panel should contain both second/third-period analogue pairs and
unsupported high-q rungs.  No candidate is removed after labels are revealed.

## Epistemic status

`M0 VS M1 INCREMENTAL TEST COMPLETE / SF_N DELTA=0 / PERIOD CONTRAST RETROSPECTIVE ONLY / M2 NOT YET DEFINED`
