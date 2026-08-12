#!/usr/bin/env python3
"""Freeze and dual-validate the quotient-ladder witness in C2 x C16."""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sds.model import parse_name  # noqa: E402
from sds.validator_independent import validate as independent_validate  # noqa: E402
from sds.validator_reference import validate as reference_validate  # noqa: E402

INSTANCE = parse_name("SDS(32,20,4,[2,16])")
VECTOR = (
    0, 0, -1, -1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1,
    1, 1, -1, 1, 1, 0, 0, 1, 1, 1, 1, -1, 1, 0, 0, 1,
)
RUN = ROOT / "artifacts" / "runs" / "v32_20_4_c2x16_quotient_witness.json"
WITNESS = ROOT / "artifacts" / "witnesses" / "sds_32_20_4_2_16.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def coordinates(index):
    return [index // 16, index % 16]


def main() -> None:
    reference = reference_validate(INSTANCE, VECTOR)
    independent = independent_validate(INSTANCE, VECTOR)
    assert reference["valid"] and independent["valid"]
    run = {
        "schema": "v32-c2x16-quotient-witness-v1",
        "command": "python3 scripts/record_v32_20_4_c2x16_witness.py",
        "instance": INSTANCE.name,
        "result": "EXISTS",
        "method": "C2 x C4 -> C2 x C8 quotient refinement followed by full coefficient refinement",
        "best_vector": VECTOR,
        "validation": {"reference": reference, "independent": independent},
    }
    RUN.write_text(json.dumps(run, indent=2, sort_keys=True) + "\n")
    witness = {
        "schema": "signed-difference-set-witness-v1",
        "frozen_date": "2026-08-12",
        "instance": INSTANCE.name,
        "group_invariant_factors": [2, 16],
        "coefficient_order": "lexicographic direct-product coordinates; last coordinate varies fastest",
        "coefficient_vector": VECTOR,
        "positive_set": [coordinates(index) for index, value in enumerate(VECTOR) if value == 1],
        "negative_set": [coordinates(index) for index, value in enumerate(VECTOR) if value == -1],
        "support": sum(value != 0 for value in VECTOR),
        "coefficient_sum": sum(VECTOR),
        "reference_validation": reference,
        "independent_validation": independent,
        "discovery": {"run_path": str(RUN.relative_to(ROOT)), "run_sha256": sha256(RUN)},
    }
    WITNESS.write_text(json.dumps(witness, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"run": str(RUN.relative_to(ROOT)), "run_sha256": sha256(RUN), "witness": str(WITNESS.relative_to(ROOT)), "witness_sha256": sha256(WITNESS)}, indent=2))


if __name__ == "__main__":
    main()
