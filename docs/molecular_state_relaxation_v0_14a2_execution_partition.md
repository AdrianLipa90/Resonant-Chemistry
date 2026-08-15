# Molecular state relaxation v0.14A2 — per-seed execution partition

## Epistemic status

**IMPLEMENTED EXECUTION PARTITION / NO NEW CHEMICAL MODEL / EXECUTION PENDING**

v0.14A2 changes only how the already frozen v0.14A1 ArBr2 calculation is executed and receipted. It does not change the molecular method, grid policy, geometry seeds, convergence thresholds, candidate state ensemble, scientific labels, or rescue policy.

The scientific state entering this gate remains:

- v0.14A1: 8/9 formulae persisted;
- 40/45 frozen starts persisted;
- ArBr2: `MISSING_EXECUTION_NOT_CHEMICAL_FAIL`;
- Hessian admission: `NOT_RUN`;
- ground-state ranking: `NOT_VALIDATED`;
- geometry-only topology assignment: `NOT_PROMOTED`.

## Motivation

The v0.14A1 workflow placed all five starts for one formula in a single job. Two ArBr2 executions reached that five-relaxation step but were cancelled before a formula receipt was persisted. That is an execution/provenance failure mode, not a chemical result.

v0.14A2 removes the monolithic execution unit:

`one frozen seed -> one process boundary -> one receipt`

The five receipts are then mechanically aggregated back into the same formula-level receipt schema used by v0.14A1.

## PhaseNav-native command surface

The reusable surface is installed as the `phase` command from the Resonant-Chemistry package:

```text
phase chem seed-manifest ...
phase chem relax ...
phase chem aggregate ...
```

The execution contract is:

```text
chem.relax.seed
  -> gate.method.frozen
  -> gate.seed.identity
  -> phase36.encode
  -> backend.adapter
  -> gate.no_rescue
  -> seed.receipt
  -> formula.aggregate
```

The conventional numerical backend remains PySCF 2.14.0 + geomeTRIC 1.1.1 under B97M-V/VV10 + def2-TZVPD. It is an isolated backend adapter, not the project architecture.

## Frozen method gate

The canonical JSON representation of `reschem.molecular_state_relaxation.METHOD_POLICY` must have SHA-256:

```text
9b58d32d361bd2c2248c10859b12785aa9aa0244e18b5504f6cbb79d2abe366d
```

A mismatch is a hard execution-gate failure. v0.14A2 must not silently follow a changed method policy.

## Frozen ArBr2 seeds

After the common Br2 dimer prepass supplies `r_YY`, the existing v0.14A1 generator must produce exactly:

1. `ArBr2_activated_s1p0`
2. `ArBr2_activated_s1p3`
3. `ArBr2_activated_s1p6`
4. `ArBr2_weak_linear`
5. `ArBr2_weak_t`

No candidate-specific geometry rescue, SCF rescue, alternate grid, alternate basis, or changed optimizer threshold is permitted.

## 36D execution address

Each seed receives a deterministic 36-component PhaseNav execution address derived from the frozen method-policy hash and the canonical seed-identity hash.

This vector is explicitly:

`MODEL_DEFINED_EXECUTION_ADDRESS_NOT_PHYSICAL_OBSERVABLE`

It is provenance/routing metadata. It is **not** a measured molecular phase space, not physical holonomy, not a bond descriptor, and not evidence for a topology assignment.

## Timeout semantics

The backend runs in a child process with a parent-side timeout. If the timeout is reached, the parent terminates that one execution unit and writes:

`EXECUTION_TIMEOUT_UNKNOWN`

with scientific interpretation:

`UNKNOWN_EXECUTION_NOT_CHEMICAL_FAIL`

There is no retry with altered settings. A workflow-level timeout is longer than the internal seed timeout so the structured receipt has time to be written and uploaded.

## Aggregation contract

Aggregation is allowed only when all five expected seed receipts are present and each passes:

- receipt schema check;
- formula identity check;
- frozen method-policy hash check;
- deterministic seed-identity hash check;
- uniqueness check.

The aggregator preserves the v0.14A formula receipt schema:

`RESCHEM_MOLECULAR_FORMULA_RELAXATION_V0_14A`

and adds `execution_partition = v0.14A2_PER_SEED` plus seed-receipt hashes.

If all five execution units return non-unknown backend receipts, formula status is `FORMULA_RELAXATION_SCREEN_COMPLETE`. If one or more execution units time out or disappear at the process boundary, formula status is `FORMULA_EXECUTION_PARTITION_COMPLETE_WITH_UNKNOWN_SEEDS`; that state does not complete the 45/45 scientific screen.

## Semantic-card invariant

v0.14A2 is represented in the semantic layer from implementation time, not retrofitted later. The model card and five ArBr2 execution-unit cards remain unassigned on TIR semantic axes and affective mappings unless explicit provenance is later supplied.

The repository CI must reject drift between:

- v0.14A2 implementation;
- the five deterministic ArBr2 seed identities;
- semantic execution-unit cards;
- the current semantic coverage ledger.

## Promotion condition

Only a durable five-seed ArBr2 formula receipt with no unresolved execution-unit timeout can close the missing 5 starts and permit the v0.14A1 screen to become 9/9 formulae and 45/45 starts.

Only after that state is persisted and audited may v0.14B Hessian/local-minimum admission be frozen. No v0.14B design is promoted by this document alone.
