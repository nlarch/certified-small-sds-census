#!/usr/bin/env python3
"""Recheck every accepted CNF/DRAT pair with a freshly supplied checker."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CHECKER_COMMIT = "2e3b2dc0ecf938addbd779d42877b6ed69d9a985"
EXPECTED_SOURCE_SHA256 = "d834b649f437e091597f5347f259b9f681087f89ca0844d0cee250a1a1a0c2ee"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def walk(value):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def proof_nodes() -> list[dict]:
    census = json.loads((ROOT / "artifacts/census/current_census.json").read_text())
    evidence_paths = sorted({entry["evidence_path"] for entry in census["entries"]})
    nodes = []
    seen = set()
    for relative in evidence_paths:
        document = json.loads((ROOT / relative).read_text())
        for node in walk(document):
            if not isinstance(node, dict):
                continue
            if not all(key in node for key in ("formula", "proof", "checker")):
                continue
            if not isinstance(node["formula"], dict) or "path" not in node["formula"]:
                continue
            key = (node["formula"]["path"], node["proof"]["path"])
            if key not in seen:
                nodes.append(node)
                seen.add(key)
    nodes.sort(key=lambda node: node["formula"]["path"])
    if len(nodes) != 57:
        raise RuntimeError(f"expected 57 proof pairs, discovered {len(nodes)}")
    return nodes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checker", type=Path, required=True)
    parser.add_argument("--checker-source", type=Path, required=True)
    parser.add_argument("--checker-commit", default=EXPECTED_CHECKER_COMMIT)
    parser.add_argument("--environment-label", default="unspecified")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    if args.checker_commit != EXPECTED_CHECKER_COMMIT:
        raise RuntimeError("checker commit differs from the frozen proof metadata")
    source_hash = sha256(args.checker_source)
    if source_hash != EXPECTED_SOURCE_SHA256:
        raise RuntimeError(f"checker source hash mismatch: {source_hash}")

    checker_hash = sha256(args.checker)
    nodes = proof_nodes()
    started = datetime.now(timezone.utc)
    audit_started = time.monotonic()
    results = []

    print(f"AUDIT_START_UTC={started.isoformat()}", flush=True)
    print(f"ENVIRONMENT={args.environment_label}", flush=True)
    print(f"PLATFORM={platform.platform()}", flush=True)
    print(f"PYTHON={platform.python_version()}", flush=True)
    print(f"CHECKER_COMMIT={args.checker_commit}", flush=True)
    print(f"CHECKER_SOURCE_SHA256={source_hash}", flush=True)
    print(f"CHECKER_BINARY_SHA256={checker_hash}", flush=True)
    print(f"PROOF_PAIR_COUNT={len(nodes)}", flush=True)

    for index, node in enumerate(nodes, start=1):
        formula = ROOT / node["formula"]["path"]
        proof = ROOT / node["proof"]["path"]
        formula_hash = sha256(formula)
        proof_hash = sha256(proof)
        if formula_hash != node["formula"]["sha256"]:
            raise RuntimeError(f"formula hash mismatch: {formula}")
        if proof_hash != node["proof"]["sha256"]:
            raise RuntimeError(f"proof hash mismatch: {proof}")

        command = [str(args.checker), str(formula), str(proof), "-f"]
        print(f"\n===== PROOF {index:02d}/57 =====", flush=True)
        print(f"FORMULA={formula.relative_to(ROOT)}", flush=True)
        print(f"FORMULA_SHA256={formula_hash}", flush=True)
        print(f"PROOF={proof.relative_to(ROOT)}", flush=True)
        print(f"PROOF_SHA256={proof_hash}", flush=True)
        print("COMMAND=" + " ".join(command), flush=True)
        item_started = time.monotonic()
        completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        elapsed = time.monotonic() - item_started
        print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n", flush=True)
        verified = completed.returncode == 0 and "s VERIFIED" in completed.stdout
        print(f"RETURN_CODE={completed.returncode}", flush=True)
        print(f"ELAPSED_SECONDS={elapsed:.6f}", flush=True)
        print(f"VERIFIED={str(verified).lower()}", flush=True)
        results.append(
            {
                "formula_path": str(formula.relative_to(ROOT)),
                "formula_sha256": formula_hash,
                "proof_path": str(proof.relative_to(ROOT)),
                "proof_sha256": proof_hash,
                "checker_output_sha256": hashlib.sha256(completed.stdout.encode()).hexdigest(),
                "return_code": completed.returncode,
                "elapsed_seconds": round(elapsed, 6),
                "verified": verified,
            }
        )
        if not verified:
            raise RuntimeError(f"DRAT verification failed for {formula}")

    finished = datetime.now(timezone.utc)
    report = {
        "schema": "clean-environment-drat-audit-v1",
        "status": "PASS",
        "started_at_utc": started.isoformat(),
        "completed_at_utc": finished.isoformat(),
        "elapsed_seconds": round(time.monotonic() - audit_started, 6),
        "environment": {
            "label": args.environment_label,
            "platform": platform.platform(),
            "python": platform.python_version(),
            "uid": os.getuid(),
        },
        "checker": {
            "source_commit": args.checker_commit,
            "source_sha256": source_hash,
            "binary_sha256": checker_hash,
        },
        "proof_pair_count": len(results),
        "verified_count": sum(item["verified"] for item in results),
        "results": results,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("\n===== AUDIT SUMMARY =====", flush=True)
    print(json.dumps({key: value for key, value in report.items() if key != "results"}, indent=2), flush=True)


if __name__ == "__main__":
    main()
