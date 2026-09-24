# Rigid Relative-Orientation Spectroscopy Control v0.1

Status: `STANDARD_GEOMETRY_CONTROL / ANALYTIC_TWO_ORBITAL_CONTROL / AB_INITIO_SPECTROSCOPIC_BINDING_OPEN`

This control isolates one chemical variable: the relative orientation of one
fragment with respect to another while declared internal distances are held
fixed. It does not claim that every molecular coupling follows the analytic
two-orbital law below.

## 1. Global rotation is not the observable

A rigid rotation of an isolated field-free molecule changes only the laboratory
frame. The control parameter here is an internal relative orientation, torsion,
bend, or registry coordinate.

For a selected fragment with coordinates (r_i), pivot (r_0), unit axis
(hat n), and relative angle (	heta),

[
r_i(	heta)
=
r_0 + R_{hat n}(	heta),[r_i(0)-r_0].
]

The implementation uses the Rodrigues proper-rotation matrix and preserves all
intra-fragment distances exactly up to floating-point roundoff.

## 2. Rigid XY2 orientation control

For the explicit (Xcdots Y_2) control,

[
Y_1=(0,0,-r_{YY}/2), qquad
Y_2=(0,0,+r_{YY}/2),
]

and

[
X(	heta)
=
(Dsin	heta,0,Dcos	heta).
]

Therefore

[
|Y_2-Y_1|=r_{YY}
]

and

[
|X-operatorname{mid}(Y_1,Y_2)|=D
]

are frozen while only relative orientation changes.

This is deliberately stricter than comparing the existing linear and T-shaped
molecular seeds, because those seeds can also differ radially.

## 3. Analytic p-p control

The minimal two-orbital Hamiltonian is

[
H(	heta)=
egin{pmatrix}
epsilon_A & t_0cos	heta \
t_0cos	heta & epsilon_B
end{pmatrix}.
]

Its eigenvalue gap is exactly

[
Delta E(	heta)
=
2sqrt{
left(rac{epsilon_A-epsilon_B}{2}ight)^2
+t_0^2cos^2	heta
}.
]

For (epsilon_A=epsilon_B),

[
Delta E(	heta)=2|t_0cos	heta|.
]

At (	heta=pi/2), the orientation-dependent control coupling vanishes and
the remaining gap is (|epsilon_A-epsilon_B|).

This is an analytic benchmark, not a universal Slater-Koster or ab-initio
binding law.

## 4. Repository responsibility boundary

Resonant-Chemistry owns in this gate:

- rigid geometry generation;
- declared orientation coordinate (	heta);
- analytic control Hamiltonian;
- control-state energies and gaps.

It does **not** infer:

- wavelength;
- oscillator strength;
- visible color;
- transition density;
- phase-microscope observables.

Those belong to Orbital Eclipse Spectroscopy once a real electronic-state
backend provides state pairs and a common orbital basis.

The intended production chain remains

[
	ext{RC geometry/states}
ightarrow
	ext{OES transition RDM}
ightarrow
(Delta E,mu,f,ho_{FI}).
]

## 5. Next physical gate

The next gate is a rigid molecular scan at fixed radial coordinates using a
standard electronic-structure backend. State identity must be tracked by
overlap/subspace continuity rather than root number alone, especially near
degeneracies or avoided crossings.

No experimental spectrum is consumed by this control.
