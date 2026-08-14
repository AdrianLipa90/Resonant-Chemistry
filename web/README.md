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
- Semantic Card Atlas: reads the persisted semantic coverage, entity-registry contract, molecular formula cards, surface-sync contract, and v0.14A1 activated-survival matrix directly from repository JSON/JSONL.

## Semantic Card Atlas contract

`semantic_card_atlas.html` + `semantic_cards.js` are a read-only projection of repository state. They must not maintain a second semantic truth in JavaScript.

The atlas currently exposes:

- 36 canonical neutral atom bases H→Kr;
- 231 deterministic v0.1 compound candidates;
- 27 deterministic v0.13 competing relational-state candidates;
- 10 v0.14A1 molecular cards;
- model/gate coverage through v0.14A1;
- the 3×3 noble-gas `XY2` screen matrix with `ArBr2 = MISSING_EXECUTION_NOT_CHEMICAL_FAIL`.

Screening values remain screening evidence. The browser does not assign Hessian/local-minimum status, ground-state ranking, electronic topology, TIR semantic coordinates, or affective coordinates.

## PhaseNav 36D contract

`web/phasenav36d.js` contains reusable browser primitives for exact 36-lane vectors: gauge locking, mean phase, order parameter, distance, phase superposition and Bloch projection. Dimension mismatch and non-finite lanes fail closed.

The browser representation is an interactive project layer. It does not by itself validate a scientific interpretation, and heavy atomic/molecular solvers remain in the Python implementation or conventional backend adapters.

## Epistemic boundary

Displayed records retain their repository status. A benchmark receipt proves the recorded execution under its stated conditions; visualization is not a new solver result. Semantic-card lineage is provenance and is not evidence of physical holonomy.
