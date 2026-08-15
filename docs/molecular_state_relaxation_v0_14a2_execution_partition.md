# Molecular state relaxation v0.14A2 — per-seed execution partition

## Epistemic status

**IMPLEMENTED EXECUTION PARTITION / NO NEW CHEMICAL MODEL / CANONICAL EXECUTION PENDING**

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

## Exact v0.14A1 input provenance

v0.14A2 must **not re-optimize the Br2 dimer prepass**. Repeating the same numerical optimization produced sub-picometre floating-point variation in `r_YY`; although chemically negligible, that changes the canonical seed bytes and therefore violates the promise that A2 executes the exact frozen v0.14A1 starts.

The only admitted Br2 seed-scale source is the first-attempt v0.14A1 artifact:

```text
workflow run:      31795895258
source head:       db756f5aa8598a24004f056aeb09b18034a08e5b
artifact id:       9217426658
artifact name:     molecular-dimer-v0.14a-Br
artifact digest:   sha256:98379b5527657df1cd782c37f84f580a6405711e9ad730271615760abd5751e4
Br2.json sha256:   6c322bbc7ea31cfb51e4d195fcaeea32747e09447cd1dd56a8aab4771af19602
frozen r_YY:       2.2842324866344543 Angstrom
reuse policy:      EXACT_BYTES_NO_REOPTIMIZATION
```

The A2 workflow downloads that immutable historical artifact, verifies the raw `Br2.json` hash before seed generation, copies the exact bytes into the execution artifact, and records `CANONICAL_SOURCE.json` beside them.

Two earlier A2 workflow attempts are retained as execution diagnostics only. The first failed before chemistry because of an artifact extraction-path error. The second fixed that plumbing error but regenerated the Br2 prepass and therefore produced slightly different seed hashes; its numerical output, if any, is **NONCANONICAL_EXECUTION_DIAGNOSTIC_PREPASS_RECOMPUTED** and must not close the v0.14A1 missing-execution gate.

## Frozen ArBr2 seeds

The exact historical Br2 receipt must generate these five v0.14A1 seed identities:

| seed | canonical seed SHA-256 |
|---|---|
| `ArBr2_activated_s1p0` | `f4a3399a565ac2688ed568edb839c036d981006ef3a1d5ee57c9ce99edaca629` |
| `ArBr2_activated_s1p3` | `be90ec4a53bff85348b0ebfc45515e3e25a3ec96d5e52169720c0d46a8873127` |
| `ArBr2_activated_s1p6` | `bd5478a6059cdabe85c1732853177473bd2b3d78bb516a318ff416f958a0a30b` |
| `ArBr2_weak_linear` | `05c956d722e890dc3f0a5845c3e058681bf602c77560ace58a575d2df6c06101` |
| `ArBr2_weak_t` | `866f804d66d2c865c1275b4d0c6f71e90d783b85cb9e831562fb668a244f1cfa` |

The workflow treats any mismatch as `FROZEN_INPUT/SEED_IDENTITY_GATE_FAIL` before the molecular backend runs.

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

v0.14A2 is represented in the semantic layer from implementation time, not retrofitted later. The model card records the exact historical input artifact and raw hash; each of the five ArBr2 execution-unit cards records its canonical seed SHA-256. The cards remain unassigned on TIR semantic axes and affective mappings unless explicit provenance is later supplied.

The repository CI must reject drift between:

- v0.14A2 implementation;
- exact first-attempt v0.14A1 Br2 input bytes;
- the five deterministic ArBr2 seed identities;
- semantic execution-unit cards;
- the current semantic coverage ledger.

## Promotion condition

Only a durable five-seed ArBr2 formula receipt generated from the exact frozen input above, with no unresolved execution-unit timeout, can close the missing 5 starts and permit the v0.14A1 screen to become 9/9 formulae and 45/45 starts.

Only after that state is persisted and audited may v0.14B Hessian/local-minimum admission be frozen. No v0.14B design is promoted by this document alone.
