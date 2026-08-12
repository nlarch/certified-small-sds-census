#!/usr/bin/env python3
"""Extract and independently revalidate the discovered order-25 witness."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sds.model import parse_name  # noqa: E402
from sds.validator_independent import validate as validate_independent  # noqa: E402
from sds.validator_reference import validate as validate_reference  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    run_path = ROOT / "artifacts" / "runs" / "v25_local_search.json"
    run = json.loads(run_path.read_text())
    entry = next(item for item in run["instances"] if item["instance"] == "SDS(25,12,1,[5,5])")
    vector = tuple(entry["validation"]["coefficient_vector"])
    instance = parse_name(entry["instance"])
    reference = validate_reference(instance, vector)
    independent = validate_independent(instance, vector)
    assert reference["valid"] and independent["valid"]
    positive = [[index // 5, index % 5] for index, value in enumerate(vector) if value == 1]
    negative = [[index // 5, index % 5] for index, value in enumerate(vector) if value == -1]
    output = ROOT / "artifacts" / "witnesses" / "sds_25_12_1_c5xc5.json"
    document = {
        "schema": "signed-difference-set-witness-v1",
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "instance": instance.name,
        "group": "C_5 x C_5",
        "coefficient_order": "lexicographic coordinates (0,0),(0,1),...,(4,4); second coordinate varies fastest",
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
            "seed": entry["runs"][-1]["seed"],
            "restarts_completed": entry["restarts_completed"],
            "steps_per_restart": entry["steps_per_restart"],
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "output": str(output.relative_to(ROOT)),
        "sha256": sha256(output),
        "reference_valid": reference["valid"],
        "independent_valid": independent["valid"],
        "positive_set": positive,
        "negative_set": negative,
    }, indent=2))


if __name__ == "__main__":
    main()
