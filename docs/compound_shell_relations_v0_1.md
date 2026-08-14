# Compound Shell Relations v0.1

## Status

**MODEL-DEFINED / SOFTWARE-TESTED / NOT A VALIDATED MOLECULAR LAW**

The current repository already treats a subshell occupation `(n,l,k)` as the
shell-level comparison object and keeps nuclei explicit.  This gate adds a
deterministic bridge from isolated-atom bookkeeping to candidate binary
stoichiometry without changing nuclear identity.

For a main-group outer `s/p` shell, let `v` be the outer-shell electron count
and `C` the nearest closed-shell capacity (`2` for `n=1`, `8` thereafter).
Define

\[
d(v)=\min(v,C-v).
\]

For Li..Ne this yields

\[
1,2,3,4,3,2,1,0,
\]

without storing an element-specific table of simple valences.

For a binary pair A,B, the minimal endpoint-balanced counts satisfy

\[
n_A d_A=n_B d_B,
\]

hence after gcd reduction

\[
n_A:n_B=d_B:d_A.
\]

Representative software controls generated from the current H..Kr atomic
bookkeeping include CH4, NH3, H2O (caller ordering may print OH2), CO2, B2O3,
Al2O3, SiO2, NaCl, MgCl2, AlCl3 and SiCl4.

## Particle-hole coordinate

Each profile also carries

\[
x=(v-C/2)/(C/2),
\]

and the bounded diagnostic

\[
\chi_{ph}=1-|x_A+x_B|/2.
\]

`chi_ph=1` means the normalized offsets from half filling cancel exactly.  It
is representation metadata, not electronegativity, bond order or bond energy.

## Fail-closed scope

v0.1 deliberately does **not** claim to solve:

- Sc..Zn transition-metal relation states;
- multiple oxidation/coordination states;
- hypervalent chemistry;
- electron-deficient or three-centre bonding;
- radicals;
- molecular geometry;
- energetic stability.

Those are later gates.  The frozen binary atlas is stored as a benchmark so
failures can be measured without tuning `d(v)` after looking at chemistry data.
