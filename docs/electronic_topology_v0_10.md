# Electronic-topology admission gate v0.10

## Why v0.10 exists

v0.9 deliberately generates a broad structural `XY2` atlas.  Post-freeze
lookup immediately exposed the next falsification boundary: **the same
stoichiometry does not imply the same electronic topology**.

KrF2 has a long-established three-centre bonding description, whereas primary
experimental literature explicitly characterizes KrCl2 van der Waals isomers.
Therefore formula matching, linearity, or even the existence of a stationary
point cannot by itself validate `SYMMETRIC_THREE_CENTRE_FOUR_ELECTRON`.

## No single magic descriptor

v0.10 intentionally does not define a fitted Mayer/Wiberg threshold, a single
QTAIM bond-critical-point rule, or a visual canonical-MO test.

This restraint is literature-driven:

- Landis and Weinhold (`landis_weinhold_2013_long_bonding`) show that canonical
  MO pictures and ordinary QTAIM BCP criteria can be misleading for proposed
  3c/4e long-bonded systems such as NeF2;
- Oliveira, Kraka, and Machado (`oliveira_kraka_machado_2019_3c4e`) compare
  hypervalent and noncovalent structures using a broad set of high-level
  descriptors: energies, electron densities, Mayer bond orders, local
  stretching force constants, and related bond-strength measures;
- Liao and Zhang (`liao_zhang_1998_noble_gas_halides`) demonstrate strong
  ligand and environment dependence across noble-gas halides.

The central bibliography is updated in the same iteration as this gate.

## Frozen diagnostic families

### 1. `ORBITAL_SUBSPACE`

A localized or explicitly projected electronic-subspace analysis.  The admitted
record must identify the electronic-structure method, basis/ECP policy, the
subspace/localization definition, and preserve the raw occupation or
delocalization summary.

A visual canonical-MO diagram alone is insufficient.

### 2. `REAL_SPACE_FORCE`

Electron-density topology and/or local force/bond-strength information.  The
record must preserve the density method and raw topology/force summary.

One QTAIM BCP, or the absence of one, is insufficient by itself.

### 3. `FRAGMENTATION_ISOMER_ENERGY`

A common-method energetic comparison among the activated candidate,
preregistered dissociation products, and competing weak-complex/isomer
structures.  Local-minimum status and environment must be recorded.

Stoichiometry alone is insufficient.

## Family verdicts

Each family returns exactly one of:

- `SUPPORT_3C4E`
- `SUPPORT_VDW`
- `INCONCLUSIVE`
- `NOT_RUN`

The raw upstream analysis is not replaced by this categorical record.

## Aggregation rule

The preregistered validation rule is deliberately conservative:

- `CONSISTENT_3C4E_MULTI_DIAGNOSTIC`: at least two distinct families support
  3c4e, zero informative families support VDW, and the species is an established
  local minimum under the admitted physical control;
- `CONSISTENT_VDW_MULTI_DIAGNOSTIC`: the symmetric rule for VDW;
- `MIXED_CONFLICTING_EVIDENCE`: at least one informative family on each side;
- `UNKNOWN_INSUFFICIENT_INDEPENDENT_EVIDENCE`: fewer than two agreeing
  informative families;
- `UNKNOWN_LOCAL_MINIMUM_NOT_ESTABLISHED`: electronic diagnostics agree but
  physical local-minimum status is unavailable;
- `REJECTED_NOT_LOCAL_MINIMUM`: the physical control does not yield a local
  minimum, so no stable topology label is assigned.

The **2-of-3 rule is a validation contract, not a chemical constant**.  Its
purpose is to prevent a single representation-dependent diagnostic from
silently becoming the definition of a chemical bond.

## Preknown exclusions

The following cases were already opened before the v0.10 aggregator was frozen
and therefore cannot enter a blind topology score:

- KrF2 -- motivating 3c case;
- KrCl2 -- post-v0.9 van der Waals counterexample;
- ArF2 -- post-v0.9 environment-dependent theoretical literature opened;
- NeF2 -- post-v0.9 theoretical literature opened;
- ArCl2 -- weak-complex literature was encountered before the freeze.

The still-frozen topology targets are:

`NeCl2`, `NeBr2`, `ArBr2`, `KrBr2`.

v0.9 predicts `3C4E` structurally for all four.  v0.10 may falsify any or all of
those topology labels without changing the v0.9 generator.

## Epistemic status

`IMPLEMENTED_VALIDATION_CONTRACT / TESTS_IMPLEMENTED / BRANCH_CI_NOT_RUN /
NO_PHYSICAL_HELDOUT_TOPOLOGY_SCORE_YET / CANON_NOT_PROMOTED`
