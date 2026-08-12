#!/usr/bin/env python3
"""Verify a lightweight Certified Small SDS release package."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from sds.model import parse_name  # noqa: E402
from sds.validator_independent import validate as independent_validate  # noqa: E402
from sds.validator_reference import validate as reference_validate  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_manifest() -> int:
    lines = (ROOT / "SHA256SUMS").read_text().splitlines()
    expected = {}
    for line in lines:
        digest, relative = line.split("  ", 1)
        expected[relative] = digest
    for relative, digest in expected.items():
        path = ROOT / relative
        if not path.is_file() or sha256(path) != digest:
            raise RuntimeError(f"manifest mismatch: {relative}")
    actual = {
        str(path.relative_to(ROOT))
        for path in ROOT.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS"
    }
    if actual != set(expected):
        raise RuntimeError("manifest file set differs from package payload")
    return len(expected)


def verify_witnesses() -> int:
    witnesses = sorted((ROOT / "artifacts" / "witnesses").glob("*.json"))
    if len(witnesses) != 16:
        raise RuntimeError(f"expected 16 witnesses, found {len(witnesses)}")
    for path in witnesses:
        document = json.loads(path.read_text())
        instance = parse_name(document["instance"])
        vector = tuple(document["coefficient_vector"])
        reference = reference_validate(instance, vector)
        independent = independent_validate(instance, vector)
        if not (reference["valid"] and independent["valid"]):
            raise RuntimeError(f"witness validation failed: {path.name}")
        if reference["autocorrelation"] != independent["autocorrelation"]:
            raise RuntimeError(f"validator disagreement: {path.name}")
    return len(witnesses)


def run_quotient_checks() -> None:
    scripts = [
        "verify_v27_remaining_quotients.py",
        "verify_v32_remaining_quotients.py",
        "verify_v36_29_4_combined_quotients.py",
    ]
    for name in scripts:
        subprocess.run([sys.executable, str(ROOT / "scripts" / name)], cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-quotients", action="store_true")
    args = parser.parse_args()
    file_count = verify_manifest()
    witness_count = verify_witnesses()
    if args.full_quotients:
        run_quotient_checks()
    print(json.dumps({
        "status": "PASS",
        "manifest_files_verified": file_count,
        "witnesses_dual_validated": witness_count,
        "full_quotients_recomputed": args.full_quotients,
    }, indent=2))


if __name__ == "__main__":
    main()
