# H3+ Conical-Intersection Berry Benchmark v0.1

Status: PREREGISTERED_MOLECULAR_STANDARD_QM_CONTROL / FCI_STO3G / NO_NEW_PHYSICS / RESULT_PENDING

## 1. External benchmark basis

Wang and Mazziotti, Phys. Chem. Chem. Phys. 26, 11491-11497 (2024), DOI 10.1039/D4CP00391H, use H3+ as a conical-intersection benchmark, compare against full configuration interaction in STO-3G, and parameterize the three nuclei as (R,0), (R,pi), and (rho,theta). Their fixed-R CI optimization example uses R=2.0 bohr. The first and second excited states form the symmetry-required E' degeneracy at D3h geometry.

This gate uses those published structural facts only to freeze a standard-QM control. No experimental or calculated target Berry result from that paper is ingested into the decision rule.

## 2. Geometry and loop

Fix

\[
R=2.0\,a_0.
\]

The first two protons are placed at

\[
(+R,0),\qquad (-R,0).
\]

For an equilateral D3h geometry in this slice,

\[
\rho_0=\sqrt 3 R,
\qquad
\theta_0=\frac{\pi}{2}.
\]

The third proton is at

\[
(\rho\cos\theta,\rho\sin\theta).
\]

Freeze the encircling loop

\[
\rho(\varphi)
=
\rho_0+\Delta\rho\cos\varphi,
\]

\[
\theta(\varphi)
=
\theta_0+\Delta\theta\sin\varphi,
\]

with

\[
\Delta\rho=0.15\,a_0,
\qquad
\Delta\theta=0.05,
\qquad
N=24.
\]

No radius adjustment is allowed after inspecting the Berry result. A future protocol version may change the loop only before seeing its new result.

The non-encircling control uses the same radii and sampling but shifts the loop centre by

\[
\rho_{\rm shift}=0.60\,a_0.
\]

## 3. Electronic-structure control

At each geometry:

1. charge = +1;
2. spin = 0;
3. RHF reference;
4. STO-3G;
5. singlet FCI;
6. compute the first three singlet roots.

The target manifold is the two excited singlet roots. Start from root index 1 at the first geometry.

## 4. State tracking

Raw eigenvector order and sign are not observables.

For adjacent geometries \(k,k+1\), compute the AO cross-overlap and transform it to the two MO bases. Then evaluate the many-electron overlap with the PySCF FCI overlap routine using the non-orthogonal one-particle overlap matrix.

Among excited roots 1 and 2 at geometry \(k+1\), continue the branch with the largest absolute overlap with the currently tracked state.

This is the only root-tracking rule. The expected final Berry sign is not used in tracking.

Fail closed if:

- RHF or FCI fails;
- root count is not three;
- adjacent tracked overlap is numerically zero;
- excited-state gap closes on a sampled point rather than inside the loop;
- orbital dimensions differ;
- any value is nonfinite.

## 5. Wilson/Berry readout

For tracked many-electron states \(\Psi_k\), define

\[
U_{k,k+1}
=
\frac{\langle\Psi_k|\Psi_{k+1}\rangle}
{|\langle\Psi_k|\Psi_{k+1}\rangle|}.
\]

Use the cross-geometry MO overlap in the FCI overlap.

The closed product is

\[
W=\prod_k U_{k,k+1},
\]

including the last-to-first overlap.

Pre-registered standard-QM predictions:

- encircling D3h CI: \(W\approx -1\), \(|\Gamma|\approx\pi\);
- shifted non-encircling loop: \(W\approx +1\), \(\Gamma\approx0\).

Decision tolerance:

\[
|\operatorname{Im}W|<10^{-6}
\]

and

\[
|\operatorname{Re}W+1|<10^{-4}
\]

for the encircling loop,

\[
|\operatorname{Re}W-1|<10^{-4}
\]

for the non-encircling loop.

## 6. RFC interpretation

If the standard-QM benchmark passes, the same-state-family RFC identification

\[
\mathcal A_-^{RFC}
=
+i\langle\Psi|d\Psi\rangle
\]

is no longer merely a synthetic two-level control: it is exercised on an ab-initio molecular electronic state family.

This closes only STANDARD_QM_MOLECULAR_BERRY_BINDING.

It does not establish an additional RFC physical field. Any beyond-standard contribution must produce a residual not already contained in this FCI Berry/QGT baseline.

## 7. Evidence firewall

The benchmark result must be persisted separately from this preregistration.

A failed sign, broken tracking path, or unstable overlap is evidence and may not be repaired in place after inspection.

The next version must receive a new protocol ID and retain this result.
