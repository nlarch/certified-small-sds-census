#!/usr/bin/env python3
"""Export the six signed (32,20,4) witnesses in Gordon's JSON format."""

from __future__ import annotations

import hashlib
import json
import sys
from itertools import product
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sds.model import parse_name  # noqa: E402
from sds.validator_independent import validate as independent_validate  # noqa: E402
from sds.validator_reference import validate as reference_validate  # noqa: E402


WITNESS_NAMES = (
    "sds_32_20_4_2_16.json",
    "sds_32_20_4_2_2_2_2_2.json",
    "sds_32_20_4_2_2_2_4.json",
    "sds_32_20_4_2_2_8.json",
    "sds_32_20_4_2_4_4.json",
    "sds_32_20_4_4_8.json",
)
OUTPUT = ROOT / "release" / "gordon_v32_20_4_noncyclic_entries.json"
COMMENT = (
    "Masselot (2026), Two Small-Order Classification Theorems for Signed "
    "Difference Sets; independently verified by Arevalo. "
    "https://github.com/NicolasMasselot/certified-small-sds-census"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconstruct_vector(
    factors: tuple[int, ...],
    positive: list[list[int]],
    negative: list[list[int]],
) -> tuple[int, ...]:
    elements = tuple(product(*(range(modulus) for modulus in factors)))
    index = {element: position for position, element in enumerate(elements)}
    vector = [0] * len(elements)
    for point in positive:
        vector[index[tuple(point)]] = 1
    for point in negative:
        position = index[tuple(point)]
        if vector[position] != 0:
            raise ValueError(f"positive and negative sets overlap at {point}")
        vector[position] = -1
    return tuple(vector)


def main() -> None:
    exported: dict[str, dict[str, object]] = {}
    validation = []

    for filename in WITNESS_NAMES:
        path = ROOT / "artifacts" / "witnesses" / filename
        witness = json.loads(path.read_text())
        instance = parse_name(witness["instance"])
        factors = tuple(witness["group_invariant_factors"])
        positive = witness["positive_set"]
        negative = witness["negative_set"]
        vector = reconstruct_vector(factors, positive, negative)

        if vector != tuple(witness["coefficient_vector"]):
            raise ValueError(f"coordinate conversion disagrees with {path}")
        reference = reference_validate(instance, vector)
        independent = independent_validate(instance, vector)
        if not reference["valid"] or not independent["valid"]:
            raise ValueError(f"validation failed for {path}")

        exported[instance.name] = {
            "status": "Yes",
            "comment": COMMENT,
            "sets": [[positive, negative]],
        }
        validation.append(
            {
                "instance": instance.name,
                "source": str(path.relative_to(ROOT)),
                "source_sha256": sha256(path),
                "positive": len(positive),
                "negative": len(negative),
                "reference_valid": reference["valid"],
                "independent_valid": independent["valid"],
            }
        )

    OUTPUT.write_text(json.dumps(exported, indent=2, ensure_ascii=False) + "\n")
    print(
        json.dumps(
            {
                "output": str(OUTPUT.relative_to(ROOT)),
                "sha256": sha256(OUTPUT),
                "entries": len(exported),
                "validation": validation,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
