# Chemical Berry Loop Positive Control v0.1

Status: STANDARD_QM_CONTROL / SYNTHETIC_CONICAL_INTERSECTION_POSITIVE_LOOP / MOLECULAR_BINDING_OPEN

## 1. Purpose

The H2+ gate supplies an exact beta1=0 null for graph holonomy. The first positive control must therefore contain a genuine gauge-invariant closed phase loop.

RFC F1 already defines

\[
\mathcal A_- = +i\langle u|du\rangle,
\]

which is the standard Berry connection for a normalized state family in that sign convention.

Resonant Chemistry already carries parameter-dependent Hamiltonian/QGT machinery. The cleanest common control is therefore a normalized chemical eigenstate family

\[
H(\lambda)|n(\lambda)\rangle = E_n(\lambda)|n(\lambda)\rangle
\]

transported around a closed parameter loop.

The physical identity asserted here is only the standard-QM control identity

\[
\boxed{
u(\lambda)\equiv n(\lambda)
\quad\Longrightarrow\quad
\mathcal A_-^{RFC}
=
+i\langle n|dn\rangle.
}
\]

This does not establish any additional RFC field or new chemical interaction.

## 2. Discrete gauge-invariant Wilson loop

For normalized eigenvectors sampled along a closed loop,

\[
|n_0\rangle,\ldots,|n_{N-1}\rangle,
\]

define the normalized overlap transporter

\[
U_{k,k+1}
=
\frac{\langle n_k|n_{k+1}\rangle}
{|\langle n_k|n_{k+1}\rangle|}.
\]

The closed Wilson product is

\[
\boxed{
W_n
=
\prod_{k=0}^{N-1}U_{k,k+1},
}
\]

with \(n_N\equiv n_0\).

Under arbitrary local rephasings

\[
|n_k\rangle\mapsto e^{i\chi_k}|n_k\rangle,
\]

the endpoint factors telescope and

\[
\boxed{W_n' = W_n}.
\]

The discrete Berry phase is

\[
\boxed{
\Gamma_n=\operatorname{Arg}W_n.
}
\]

This is a standard geometric-phase observable of the declared state family.

## 3. Synthetic conical-intersection control

Use the real two-level Hamiltonian

\[
\boxed{
H(x,y)=x\sigma_x+y\sigma_z.
}
\]

The degeneracy lies at \((x,y)=(0,0)\).

For a loop encircling the origin,

\[
(x,y)=(\cos\varphi,\sin\varphi),
\qquad
0\le\varphi<2\pi,
\]

the lower adiabatic state acquires the Berry/Wilson phase

\[
\boxed{\Gamma=\pi\pmod{2\pi}},
\qquad
\boxed{W=-1}.
\]

For a contractible loop that does not enclose the degeneracy, the control gives

\[
\boxed{\Gamma=0\pmod{2\pi}},
\qquad
\boxed{W=+1}.
\]

The result must be invariant under arbitrary pointwise eigenvector rephasing.

## 4. Why this closes the mathematical edge/path realization

For this control, the RC path is the declared closed path in Hamiltonian parameter space and the RFC path is the same path after the explicit state-family identification \(u=n\).

Therefore

\[
\iota:
\lambda_k^{RC}
\mapsto
\lambda_k^{RFC}
\]

is the identity on the declared parameter path, and the connection one-form is the same Berry connection.

Thus the prior broad gate

COMMON_PHYSICAL_EDGE_PATH_REALIZATION

splits into two layers:

1. STANDARD_QM_BERRY_PATH_BINDING — closed by this synthetic control;
2. NEW_PHYSICAL_CARRIER_BINDING — still open for any claim beyond standard Berry/QGT physics.

## 5. Relationship to the phase-dressed graph Hamiltonian

This control does not claim that a molecular bond graph is the state-transport graph.

It establishes only that a cyclic normalized eigenstate bundle already provides a physically standard phase loop. Any later use of

\[
V_I^{(1)}
=
\sum_a\delta\Phi_a
\frac{\partial H}{\partial\Phi_a}
\]

must declare whether \(\Phi_a\) is:

- a standard Berry/geometric phase coordinate already contained in the control Hamiltonian; or
- an additional independently sourced phase coordinate.

Double counting is forbidden.

## 6. Falsification controls

The gate fails if any of the following occurs:

- the Wilson product changes under local eigenvector rephasing;
- the encircling loop does not give \(W=-1\) within numerical tolerance;
- the off-degeneracy contractible loop does not give \(W=+1\);
- an adjacent overlap vanishes, making the discrete transporter undefined;
- a claimed new-physics contribution cannot be separated from the standard Berry/QGT baseline.

## 7. Epistemic boundary

Closed here:

- standard normalized-state Berry connection;
- discrete gauge-invariant Wilson loop;
- conical-intersection positive phase control;
- contractible-loop null;
- RFC F1 ↔ standard chemical Berry connection type match when the same normalized state family is explicitly used.

Open:

- molecule-specific conical-intersection realization;
- any beyond-standard-QM phase source;
- any additional physical \(V_I\) beyond the standard Berry/QGT baseline.
