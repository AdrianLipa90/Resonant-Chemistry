# Resonant Chemistry Interactive Companion

Run from the repository root:

```text
python3 -m http.server 8000
```

Then open `http://localhost:8000/web/`.

## Current browser surfaces

- Control Atlas: reads repository benchmark records; it does not replace SCF/CI execution.
- Shell Lab: particle-hole shell algebra plus a deterministic 36-lane PhaseNav representation.
- Carbon Relaxation: visualization of the recorded state-averaged p-relaxation benchmark.
- Topology / Conformal Lab: diagnostic `zeta = Phi - z*` and `eta = 1/zeta` controls.

## PhaseNav 36D contract

`web/phasenav36d.js` contains reusable browser primitives for exact 36-lane vectors: gauge locking, mean phase, order parameter, distance, phase superposition and Bloch projection. Dimension mismatch and non-finite lanes fail closed.

The browser representation is an interactive project layer. It does not by itself validate a scientific interpretation, and heavy atomic solvers remain in the Python implementation.

## Epistemic boundary

Displayed records retain their repository status. A benchmark receipt proves the recorded execution under its stated conditions; visualization is not a new solver result.
