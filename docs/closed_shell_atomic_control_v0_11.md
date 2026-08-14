# Closed-shell atomic control vector v0.11

## Purpose

v0.9 showed that a shell-only structural generator is deliberately broad.
v0.10 then exposed several post-preregistered cases whose literature reference
class is van der Waals rather than the generated 3c4e topology.

v0.11 asks a narrower question before introducing any new relational score:

> Do the conventional **isolated-atom controls already present in the repo**
> contain explanatory information about closed-shell activation versus weak
> complex formation?

This is not a molecular solver and is not a new Hamiltonian term.

## Frozen raw vector

For centre `X` and ligand `Y`, using the same robust average-of-configuration
atomic Hartree--Fock implementation for every species and charge state:

\[
I_X^{HF}=E_{HF}(X^+)-E_{HF}(X),
\]

\[
A_Y^{HF}=E_{HF}(Y)-E_{HF}(Y^-),
\]

\[
\Delta_{CT}^{HF}=I_X^{HF}-A_Y^{HF}.
\]

The vector also records the occupancy-weighted mean radius and radial standard
deviation of the neutral atom's outermost represented `p` channel for both the
centre and ligand.

The full vector is therefore:

- centre HF ionization cost;
- ligand HF attachment gain;
- their raw difference `Delta_CT`;
- centre outer-`p` mean radius and radial sigma;
- ligand outer-`p` mean radius and radial sigma;
- one explicit quality flag covering all neutral/cation/anion atomic solves.

## Critical interpretation limits

`I_X^HF` and `A_Y^HF` are **finite differences inside the current atomic HF
control model**.

In particular:

- `A_Y^HF` is not asserted to be an accurate experimental electron affinity;
- a finite-basis Hartree--Fock anion can be qualitatively imperfect;
- `Delta_CT^HF` is not asserted to represent literal electron transfer in a
  3c4e bond;
- no scalar score or fitted combination of the vector components exists in
  v0.11;
- no threshold is selected from KrF2, NeCl2, NeBr2, ArBr2, or any other
  already-opened label.

## Anti-fit rule

The nine v0.9 candidates receive their raw atomic vectors before any scalar
classifier is designed:

`NeF2`, `NeCl2`, `NeBr2`, `ArF2`, `ArCl2`, `ArBr2`, `KrF2`, `KrCl2`, `KrBr2`.

Post-execution inspection may ask whether a known reference class occupies an
interesting region of the raw descriptor space, but such inspection is
**exploratory post-falsifier analysis**, not blind validation.

Any later predictive scalar must be frozen and tested on a genuinely new
transfer set.

## Execution contract

The executable benchmark is
`scripts/run_closed_shell_atomic_control_v0_11.py`.

It uses `reschem.atomic_hf_diis.solve_atom_average_hf_robust`, the repository's
existing non-element-specific quality ladder.  No charged species receives a
special rescue path.

The run writes
`benchmarks/CLOSED_SHELL_ATOMIC_CONTROL_V0_11.json` and returns nonzero if any
required atomic solve fails its quality gate.  CI uploads the raw JSON even on
failure so the failure cannot disappear.

## Epistemic status

`CONVENTIONAL_CONTROL_DESCRIPTOR / PREREGISTERED_RAW_VECTOR /
NO_SCALAR_CLASSIFIER / NO_MOLECULAR_ENERGY / PHYSICAL_EXECUTION_PENDING_OR_RECEIPT_DEPENDENT`
