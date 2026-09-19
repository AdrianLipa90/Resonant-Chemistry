# Molecular State Relaxation v0.14A3 — ArBr2 weak-linear execution replay

Status: **PREREGISTERED / NOT EXECUTED**

## Scope

v0.14A3 is an execution-envelope replay of exactly one unresolved v0.14A2 execution unit:

- formula: `ArBr2`
- seed: `ArBr2_weak_linear`
- seed identity SHA-256: `05c956d722e890dc3f0a5845c3e058681bf602c77560ace58a575d2df6c06101`
- parent v0.14A2 receipt: `benchmarks/v0_14a2_seed_receipts/ArBr2_weak_linear.json`
- parent receipt Git blob SHA-1: `b4476a0b7896950010987d7aed640b6495052a9f`
- parent execution status: `EXECUTION_TIMEOUT_UNKNOWN`
- parent scientific boundary: `UNKNOWN_EXECUTION_NOT_CHEMICAL_FAIL`

The frozen first-attempt receipt remains preserved as v0.14A2 evidence.

## Frozen scientific input

The replay reuses exactly:

- `benchmarks/v0_14a2_frozen_input/Br2.json`
- raw JSON SHA-256: `6c322bbc7ea31cfb51e4d195fcaeea32747e09447cd1dd56a8aab4771af19602`
- `r_YY = 2.2842324866344543 Å`
- method policy SHA-256: `9b58d32d361bd2c2248c10859b12785aa9aa0244e18b5504f6cbb79d2abe366d`

No change is admitted to seed identity, geometry, molecular method, basis, grid, SCF policy, optimizer policy, charge/spin policy, or rescue policy.

## Only admitted delta

The only preregistered difference is the execution time budget:

- v0.14A2 first-attempt timeout: `2400 s`
- v0.14A3 replay timeout: `7200 s`
- delta class: `TIME_BUDGET_ONLY`

The threefold time envelope is intended to distinguish an execution-budget timeout from a completed backend result while keeping the scientific inputs fixed.

## Execution isolation

Workflow:

`.github/workflows/molecular-state-relaxation-v0.14a3-weak-linear-replay.yml`

Trigger policy:

- manual `workflow_dispatch` only;
- no push trigger;
- no automatic execution from branch updates.

Before computation the workflow verifies the preregistration, frozen Br2 byte hash, parent receipt Git-blob hash, seed identity, method-policy hash, prior UNKNOWN status, and the no-change/no-rescue constraints.

The replay output is written only to:

`benchmarks/v0_14a3_replay_receipts/`

and uploaded as an Actions artifact. The workflow does not overwrite `benchmarks/v0_14a2_seed_receipts/` and does not commit generated replay results into the repository.

## Lineage and promotion boundary

A replay result is additional execution evidence linked to the v0.14A2 first attempt. It does not replace that receipt.

A non-UNKNOWN replay result does not automatically change the scientific checkpoint. Any checkpoint change requires a separate lineage audit that verifies:

1. the frozen input hash;
2. the frozen seed identity;
3. the frozen method-policy hash;
4. that the only execution-policy delta was the timeout budget;
5. preservation of the original v0.14A2 receipt;
6. a resolved execution unit with no remaining UNKNOWN status in the admitted formula ledger.

Until that audit is completed, the checkpoint remains **8/9 formulae and 40/45 starts**.

No Hessian admission, ground-state ranking, or geometry-only topology promotion is performed by v0.14A3.
