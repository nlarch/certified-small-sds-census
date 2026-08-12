#!/usr/bin/env python3
"""Extract every validated EXISTS node from a local-search run."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sds.model import elements, parse_name  # noqa: E402
from sds.validator_independent import validate as validate_independent  # noqa: E402
from sds.validator_reference import validate as validate_reference  # noqa: E402


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def slug(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    run_path = args.run if args.run.is_absolute() else ROOT / args.run
    run = json.loads(run_path.read_text())
    outputs = []
    for entry in run["instances"]:
        if entry["result"] != "EXISTS":
            continue
        instance = parse_name(entry["instance"])
        vector = tuple(entry["validation"]["coefficient_vector"])
        reference = validate_reference(instance, vector)
        independent = validate_independent(instance, vector)
        assert reference["valid"] and independent["valid"]
        elts = elements(instance.group)
        positive = [list(elts[index]) for index, value in enumerate(vector) if value == 1]
        negative = [list(elts[index]) for index, value in enumerate(vector) if value == -1]
        witness = {
            "schema": "signed-difference-set-witness-v1",
            "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
            "instance": instance.name,
            "group_invariant_factors": instance.group,
            "coefficient_order": "lexicographic direct-product coordinates; last coordinate varies fastest",
            "coefficient_vector": vector,
            "positive_set": positive,
            "negative_set": negative,
            "support": len(positive) + len(negative),
            "coefficient_sum": sum(vector),
            "reference_validation": reference,
            "independent_validation": independent,
            "discovery": {
                "run_path": str(run_path.relative_to(ROOT)),
                "run_sha256": sha256(run_path),
                "seed_offset": entry.get("seed_offset"),
                "restarts_completed": entry["restarts_completed"],
                "steps_per_restart": entry["steps_per_restart"],
            },
        }
        output = ROOT / "artifacts" / "witnesses" / f"{slug(instance.name)}.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(witness, indent=2, sort_keys=True) + "\n")
        outputs.append({
            "instance": instance.name,
            "output": str(output.relative_to(ROOT)),
            "sha256": sha256(output),
            "positive_set": positive,
            "negative_set": negative,
        })
    print(json.dumps({"source_run": str(run_path.relative_to(ROOT)), "witnesses": outputs}, indent=2))


if __name__ == "__main__":
    main()
