"""PhaseNav-native execution partition for the frozen v0.14A1 molecular screen.

The command surface is intentionally thin:
    phase chem relax ...
    phase chem aggregate ...

It does not redefine chemistry. It gates one frozen v0.14A1 seed, encodes a
deterministic 36D execution address, calls the isolated conventional
PySCF/geomeTRIC backend adapter, and emits a provenance receipt.

The 36D vector is MODEL_DEFINED execution metadata, not a physical observable
and not evidence of physical holonomy.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
from queue import Empty
import time
from typing import Iterable, Mapping

from .molecular_state_relaxation import (
    METHOD_POLICY,
    MolecularSeed,
    add_relative_energies,
    run_pyscf_relaxation,
    xy2_seed_geometries,
)

PHASE36_DIMENSION = 36
PHASE36_DOMAIN = "RESCHEM_PHASE36_EXECUTION_ADDRESS_V0_14A2"
SEED_RECEIPT_SCHEMA = "RESCHEM_PHASENAV_CHEM_RELAX_SEED_V0_14A2"
FORMULA_RECEIPT_SCHEMA = "RESCHEM_MOLECULAR_FORMULA_RELAXATION_V0_14A"
FROZEN_METHOD_POLICY_SHA256 = "9b58d32d361bd2c2248c10859b12785aa9aa0244e18b5504f6cbb79d2abe366d"
PREREG_SOURCE = "benchmarks/MOLECULAR_STATE_RELAXATION_PREREG_V0_14A.json"
A2_DOC = "docs/molecular_state_relaxation_v0_14a2_execution_partition.md"

UNKNOWN_EXECUTION_STATUSES = {
    "EXECUTION_TIMEOUT_UNKNOWN",
    "BACKEND_PROCESS_EXIT_UNKNOWN",
}


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def current_method_policy_sha256() -> str:
    return sha256_json(METHOD_POLICY)


def assert_frozen_method_gate() -> str:
    digest = current_method_policy_sha256()
    if digest != FROZEN_METHOD_POLICY_SHA256:
        raise RuntimeError(
            "FROZEN_METHOD_GATE_FAIL: METHOD_POLICY drift "
            f"{digest} != {FROZEN_METHOD_POLICY_SHA256}"
        )
    return digest


def seed_identity_sha256(seed: MolecularSeed) -> str:
    return sha256_json(seed.to_dict())


def phase36_encode(seed: MolecularSeed, method_sha256: str | None = None) -> dict:
    """Return a deterministic 36D execution address.

    This is a software/provenance coordinate only. It must never be interpreted
    as a measured molecular phase-space observable.
    """
    method_hash = method_sha256 or assert_frozen_method_gate()
    seed_hash = seed_identity_sha256(seed)
    payload = f"{PHASE36_DOMAIN}|{method_hash}|{seed_hash}".encode("utf-8")
    digest = hashlib.sha512(payload).digest()
    vector = [((byte - 127.5) / 127.5) for byte in digest[:PHASE36_DIMENSION]]
    return {
        "dimension": PHASE36_DIMENSION,
        "domain": PHASE36_DOMAIN,
        "status": "MODEL_DEFINED_EXECUTION_ADDRESS_NOT_PHYSICAL_OBSERVABLE",
        "method_policy_sha256": method_hash,
        "seed_identity_sha256": seed_hash,
        "vector": vector,
    }


def _seed_from_dict(data: Mapping[str, object]) -> MolecularSeed:
    return MolecularSeed(
        seed_id=str(data["seed_id"]),
        formula=str(data["formula"]),
        state_kind=str(data["state_kind"]),
        atoms=tuple(str(x) for x in data["atoms"]),
        coordinates_angstrom=tuple(
            tuple(float(v) for v in row)
            for row in data["coordinates_angstrom"]
        ),
        source_rule=str(data["source_rule"]),
    )


def select_frozen_seed(
    centre: str,
    ligand: str,
    r_yy_angstrom: float,
    seed_id: str,
) -> MolecularSeed:
    seeds = xy2_seed_geometries(centre, ligand, float(r_yy_angstrom))
    matches = [seed for seed in seeds if seed.seed_id == seed_id]
    if len(matches) != 1:
        available = [seed.seed_id for seed in seeds]
        raise ValueError(f"unknown frozen seed {seed_id!r}; available={available}")
    return matches[0]


def frozen_seed_manifest(centre: str, ligand: str, r_yy_angstrom: float) -> dict:
    method_hash = assert_frozen_method_gate()
    seeds = xy2_seed_geometries(centre, ligand, float(r_yy_angstrom))
    return {
        "schema": "RESCHEM_PHASENAV_CHEM_SEED_MANIFEST_V0_14A2",
        "formula": f"{centre}{ligand}2",
        "centre": centre,
        "ligand": ligand,
        "optimized_r_YY_angstrom": float(r_yy_angstrom),
        "method_policy_sha256": method_hash,
        "seed_count": len(seeds),
        "seeds": [
            {
                "seed_id": seed.seed_id,
                "seed_identity_sha256": seed_identity_sha256(seed),
                "state_kind": seed.state_kind,
                "phase36": phase36_encode(seed, method_hash),
            }
            for seed in seeds
        ],
        "nonclaims": [
            "phase36 execution address is model-defined provenance metadata",
            "no physical holonomy is inferred from the execution address",
            "seed manifest does not perform a molecular relaxation",
        ],
    }


def _backend_worker(seed_data: dict, queue) -> None:
    try:
        result = run_pyscf_relaxation(_seed_from_dict(seed_data))
        queue.put({"kind": "RESULT", "payload": result})
    except BaseException as exc:
        queue.put(
            {
                "kind": "WORKER_EXCEPTION",
                "payload": {
                    "status": "RELAXATION_EXCEPTION",
                    "exception_type": type(exc).__name__,
                    "exception_message": str(exc),
                },
            }
        )


def execute_backend_with_timeout(seed: MolecularSeed, timeout_seconds: float) -> dict:
    """Execute one backend call with a parent-side timeout receipt.

    No retry and no altered SCF/geometry settings are allowed.
    """
    timeout = float(timeout_seconds)
    if timeout <= 0:
        raise ValueError("timeout_seconds must be positive")

    ctx = mp.get_context("spawn")
    queue = ctx.Queue(maxsize=1)
    proc = ctx.Process(target=_backend_worker, args=(seed.to_dict(), queue))
    started = time.perf_counter()
    proc.start()
    proc.join(timeout)
    elapsed = time.perf_counter() - started

    if proc.is_alive():
        proc.terminate()
        proc.join(10)
        if proc.is_alive() and hasattr(proc, "kill"):
            proc.kill()
            proc.join(10)
        return {
            "seed": seed.to_dict(),
            "method_policy": dict(METHOD_POLICY),
            "status": "EXECUTION_TIMEOUT_UNKNOWN",
            "timeout_seconds": timeout,
            "wall_seconds": elapsed,
            "no_rescue": True,
            "scientific_interpretation": "UNKNOWN_EXECUTION_NOT_CHEMICAL_FAIL",
        }

    try:
        message = queue.get_nowait()
    except Empty:
        return {
            "seed": seed.to_dict(),
            "method_policy": dict(METHOD_POLICY),
            "status": "BACKEND_PROCESS_EXIT_UNKNOWN",
            "process_exit_code": proc.exitcode,
            "wall_seconds": elapsed,
            "no_rescue": True,
            "scientific_interpretation": "UNKNOWN_EXECUTION_NOT_CHEMICAL_FAIL",
        }

    result = dict(message["payload"])
    result["wall_seconds"] = elapsed
    result["no_rescue"] = True
    result["worker_message_kind"] = message["kind"]
    return result


def build_seed_receipt(
    centre: str,
    ligand: str,
    r_yy_angstrom: float,
    seed_id: str,
    timeout_seconds: float,
) -> dict:
    method_hash = assert_frozen_method_gate()
    seed = select_frozen_seed(centre, ligand, r_yy_angstrom, seed_id)
    phase36 = phase36_encode(seed, method_hash)
    result = execute_backend_with_timeout(seed, timeout_seconds)
    execution_status = result.get("status", "UNKNOWN")
    return {
        "schema": SEED_RECEIPT_SCHEMA,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "command": "phase chem relax",
        "execution_partition": "v0.14A2_PER_SEED",
        "preregister_source": PREREG_SOURCE,
        "documentation": A2_DOC,
        "formula": seed.formula,
        "centre": centre,
        "ligand": ligand,
        "optimized_r_YY_angstrom": float(r_yy_angstrom),
        "seed_id": seed.seed_id,
        "seed_identity_sha256": seed_identity_sha256(seed),
        "method_policy_sha256": method_hash,
        "gates": {
            "method_frozen": "PASS",
            "seed_identity": "PASS",
            "no_rescue": "PASS",
            "phase36_dimension": "PASS",
        },
        "phase36": phase36,
        "backend_adapter": {
            "kind": "CONVENTIONAL_NUMERICAL_BACKEND_ADAPTER",
            "implementation": "reschem.molecular_state_relaxation.run_pyscf_relaxation",
            "policy": dict(METHOD_POLICY),
        },
        "execution_status": execution_status,
        "backend_result": result,
        "epistemic_status": {
            "execution": (
                "UNKNOWN_EXECUTION_NOT_CHEMICAL_FAIL"
                if execution_status in UNKNOWN_EXECUTION_STATUSES
                else "EXECUTION_RECEIPT_AVAILABLE"
            ),
            "hessian_admission": "NOT_RUN",
            "ground_state_ranking": "NOT_VALIDATED",
            "geometry_only_topology_assignment": "NOT_PROMOTED",
        },
    }


def _load_dimer_r_yy(path: Path, ligand: str) -> float:
    payload = json.loads(path.read_text(encoding="utf-8"))
    expected_formula = f"{ligand}2"
    if payload.get("formula") != expected_formula:
        raise ValueError(
            f"dimer formula mismatch: {payload.get('formula')} != {expected_formula}"
        )
    r_yy = payload.get("optimized_r_YY_angstrom")
    if payload.get("status") != "DIMER_PREPASS_AVAILABLE" or r_yy is None:
        raise ValueError("DIMER_PREPASS_UNAVAILABLE")
    return float(r_yy)


def aggregate_seed_receipts(
    centre: str,
    ligand: str,
    r_yy_angstrom: float,
    receipts: Iterable[Mapping[str, object]],
) -> dict:
    method_hash = assert_frozen_method_gate()
    expected_seeds = xy2_seed_geometries(centre, ligand, float(r_yy_angstrom))
    expected_ids = [seed.seed_id for seed in expected_seeds]
    expected_hashes = {seed.seed_id: seed_identity_sha256(seed) for seed in expected_seeds}

    rows = list(receipts)
    by_id: dict[str, Mapping[str, object]] = {}
    for receipt in rows:
        if receipt.get("schema") != SEED_RECEIPT_SCHEMA:
            raise ValueError(f"unexpected seed receipt schema: {receipt.get('schema')}")
        if receipt.get("formula") != f"{centre}{ligand}2":
            raise ValueError(f"formula mismatch in seed receipt: {receipt.get('formula')}")
        if receipt.get("method_policy_sha256") != method_hash:
            raise ValueError(f"method policy drift in seed receipt: {receipt.get('seed_id')}")
        seed_id = str(receipt.get("seed_id"))
        if seed_id in by_id:
            raise ValueError(f"duplicate seed receipt: {seed_id}")
        if seed_id not in expected_hashes:
            raise ValueError(f"unexpected seed receipt: {seed_id}")
        if receipt.get("seed_identity_sha256") != expected_hashes[seed_id]:
            raise ValueError(f"seed identity drift: {seed_id}")
        by_id[seed_id] = receipt

    missing = [seed_id for seed_id in expected_ids if seed_id not in by_id]
    if missing:
        raise ValueError(f"missing seed receipts: {missing}")

    backend_results = [
        dict(by_id[seed_id]["backend_result"])
        for seed_id in expected_ids
    ]
    results = add_relative_energies(backend_results)
    success_count = sum(
        row.get("status") == "RELAXATION_RETURNED_FINAL_SCF_CONVERGED_NO_HESSIAN"
        for row in results
    )
    unknown_ids = [
        expected_ids[i]
        for i, row in enumerate(results)
        if row.get("status") in UNKNOWN_EXECUTION_STATUSES
    ]
    status = (
        "FORMULA_RELAXATION_SCREEN_COMPLETE"
        if not unknown_ids
        else "FORMULA_EXECUTION_PARTITION_COMPLETE_WITH_UNKNOWN_SEEDS"
    )

    return {
        "schema": FORMULA_RECEIPT_SCHEMA,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "preregister_source": PREREG_SOURCE,
        "execution_partition": "v0.14A2_PER_SEED",
        "formula": f"{centre}{ligand}2",
        "centre": centre,
        "ligand": ligand,
        "status": status,
        "optimized_r_YY_angstrom": float(r_yy_angstrom),
        "start_count": len(results),
        "attempted_start_count": len(results),
        "successful_relaxation_count": success_count,
        "unknown_execution_seed_ids": unknown_ids,
        "method_policy_sha256": method_hash,
        "seed_receipt_sha256": {
            seed_id: sha256_json(by_id[seed_id]) for seed_id in expected_ids
        },
        "relaxations": results,
        "nonclaims": [
            "relative electronic energies are screening results only",
            "no Hessian/local-minimum admission is performed",
            "geometry is not converted automatically into a 3c4e/VDW topology label",
            "execution timeout is UNKNOWN execution and is never chemical failure",
            "v0.14A2 changes execution partition only; method and frozen seeds are unchanged",
        ],
    }


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _load_seed_receipts(directory: Path) -> list[dict]:
    receipts = []
    for path in sorted(directory.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("schema") == SEED_RECEIPT_SCHEMA:
            receipts.append(payload)
    return receipts


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="phase")
    top = parser.add_subparsers(dest="surface", required=True)
    chem = top.add_parser("chem")
    commands = chem.add_subparsers(dest="chem_command", required=True)

    manifest = commands.add_parser("seed-manifest")
    manifest.add_argument("--centre", choices=("Ne", "Ar", "Kr"), required=True)
    manifest.add_argument("--ligand", choices=("F", "Cl", "Br"), required=True)
    manifest.add_argument("--dimer-json", type=Path, required=True)
    manifest.add_argument("--output", type=Path)

    relax = commands.add_parser("relax")
    relax.add_argument("--centre", choices=("Ne", "Ar", "Kr"), required=True)
    relax.add_argument("--ligand", choices=("F", "Cl", "Br"), required=True)
    relax.add_argument("--seed", required=True)
    relax.add_argument("--dimer-json", type=Path, required=True)
    relax.add_argument("--timeout-seconds", type=float, default=2400.0)
    relax.add_argument("--output-dir", type=Path, required=True)

    aggregate = commands.add_parser("aggregate")
    aggregate.add_argument("--centre", choices=("Ne", "Ar", "Kr"), required=True)
    aggregate.add_argument("--ligand", choices=("F", "Cl", "Br"), required=True)
    aggregate.add_argument("--dimer-json", type=Path, required=True)
    aggregate.add_argument("--seed-dir", type=Path, required=True)
    aggregate.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.surface != "chem":
        raise SystemExit("unsupported PhaseNav surface")

    r_yy = _load_dimer_r_yy(args.dimer_json, args.ligand)

    if args.chem_command == "seed-manifest":
        payload = frozen_seed_manifest(args.centre, args.ligand, r_yy)
        if args.output:
            _write_json(args.output, payload)
        print(json.dumps(payload, indent=2))
        return 0

    if args.chem_command == "relax":
        payload = build_seed_receipt(
            args.centre,
            args.ligand,
            r_yy,
            args.seed,
            args.timeout_seconds,
        )
        output = args.output_dir / f"{args.seed}.json"
        _write_json(output, payload)
        print(
            json.dumps(
                {
                    "output": str(output),
                    "seed": args.seed,
                    "execution_status": payload["execution_status"],
                },
                indent=2,
            )
        )
        return 0

    if args.chem_command == "aggregate":
        receipts = _load_seed_receipts(args.seed_dir)
        payload = aggregate_seed_receipts(
            args.centre,
            args.ligand,
            r_yy,
            receipts,
        )
        _write_json(args.output, payload)
        print(
            json.dumps(
                {
                    "output": str(args.output),
                    "formula": payload["formula"],
                    "status": payload["status"],
                    "start_count": payload["start_count"],
                    "successful_relaxation_count": payload["successful_relaxation_count"],
                    "unknown_execution_seed_ids": payload["unknown_execution_seed_ids"],
                },
                indent=2,
            )
        )
        return 0

    raise SystemExit("unknown chem command")


if __name__ == "__main__":
    raise SystemExit(main())
