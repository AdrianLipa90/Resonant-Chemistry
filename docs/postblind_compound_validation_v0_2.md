# Post-blind Compound Screening v0.2

## Status

**POST-BLIND DIAGNOSTIC SCREENING / NOT CANONICAL PHYSICAL VALIDATION**

The v0.1 shell-relation rule was frozen before consulting the 18-entry
diagnostic chemistry panel recorded in
`benchmarks/POSTBLIND_COMPOUND_VALIDATION_V0_2.json`.

The panel is not a statistically random sample of all binary chemistry, so its
17/18 primary-formula presence count must **not** be reported as a general
94.4% chemistry accuracy claim.  Formula existence is also weaker than
predicting dominant phase, thermodynamic stability, geometry, spectra or bond
energetics.

The useful result is the failure taxonomy:

- **B-H:** BH3 is represented, while B2H6 exposes electron-deficient / three-centre structure not captured by endpoint balance.
- **P-Cl:** PCl3 is represented, while PCl5 shows an additional coordination state.
- **S-F:** SF2 is represented, while SF6 shows a higher coordination state.
- **Kr-F:** KrF2 is a direct false negative because the v0.1 closed-shell reduction gives Kr relation degree zero.

These observations argue against repairing the model by fractional nuclear
charge or by silently altering the frozen shell degree.  The next candidate
coordinates should instead represent distinct relation mechanisms while nuclei
remain explicit and integer-Z:

1. three-centre / electron-deficient relation primitives;
2. discrete coordination/reorganization states;
3. closed-shell excitation/polarization states.
