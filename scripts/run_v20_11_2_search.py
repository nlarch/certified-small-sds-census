#!/usr/bin/env python3
"""Exact symmetry-reduced search plus full audit for SDS(20,11,2,[2,10])."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sds.model import elements, parse_name  # noqa: E402
from sds.validator_independent import validate as validate_independent  # noqa: E402
from sds.validator_reference import validate as validate_reference  # noqa: E402

INSTANCE = parse_name("SDS(20,11,2,[2,10])")
ALL_MASK = (1 << 20) - 1
POPCOUNT_10 = tuple(bin(value).count("1") for value in range(1 << 10))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def masks_of_weight(n: int, weight: int) -> List[int]:
    return [sum(1 << position for position in chosen) for chosen in itertools.combinations(range(n), weight)]


def tuple_subtraction_table() -> List[List[int]]:
    elts = elements(INSTANCE.group)
    rank = {element: i for i, element in enumerate(elts)}
    return [
        [
            rank[
                tuple(
                    (elts[left][j] - elts[shift][j]) % INSTANCE.group[j]
                    for j in range(len(INSTANCE.group))
                )
            ]
            for left in range(INSTANCE.v)
        ]
        for shift in range(INSTANCE.v)
    ]


def vector_from_masks(positive_mask: int, negative_mask: int) -> Tuple[int, ...]:
    return tuple(
        1 if positive_mask & (1 << i) else -1 if negative_mask & (1 << i) else 0
        for i in range(INSTANCE.v)
    )


def direct_tuple_check(vector: Sequence[int], subtraction: Sequence[Sequence[int]]) -> bool:
    # Cheap involutions first; every shift is still checked on acceptance.
    order = (10, 5) + tuple(i for i in range(1, INSTANCE.v) if i not in (5, 10))
    for shift in order:
        if sum(vector[left] * vector[subtraction[shift][left]] for left in range(INSTANCE.v)) != INSTANCE.lam:
            return False
    return sum(value * value for value in vector) == INSTANCE.k


def method_a(positive_masks: Sequence[int]) -> dict:
    """Fix one negative at identity using translation, then search all representatives."""
    started = time.perf_counter()
    subtraction = tuple_subtraction_table()
    tested = 0
    for other_negative in range(1, INSTANCE.v):
        negative_mask = 1 | (1 << other_negative)
        for positive_mask in positive_masks:
            if positive_mask & negative_mask:
                continue
            tested += 1
            vector = vector_from_masks(positive_mask, negative_mask)
            if direct_tuple_check(vector, subtraction):
                return {
                    "name": "translation_reduced_tuple_search",
                    "assignments_tested": tested,
                    "complete": False,
                    "witness": vector,
                    "runtime_seconds": time.perf_counter() - started,
                }
    return {
        "name": "translation_reduced_tuple_search",
        "assignments_tested": tested,
        "complete": True,
        "witness": None,
        "runtime_seconds": time.perf_counter() - started,
    }


def rotate10(row: int, amount: int) -> int:
    amount %= 10
    if amount == 0:
        return row
    return ((row << amount) | (row >> (10 - amount))) & 0x3FF


def shifted_mask(mask: int, first_shift: int, second_shift: int) -> int:
    row0 = mask & 0x3FF
    row1 = (mask >> 10) & 0x3FF
    if first_shift:
        row0, row1 = row1, row0
    return rotate10(row0, second_shift) | (rotate10(row1, second_shift) << 10)


def popcount20(mask: int) -> int:
    return POPCOUNT_10[mask & 0x3FF] + POPCOUNT_10[(mask >> 10) & 0x3FF]


SHIFT_ORDER = ((1, 0), (0, 5)) + tuple(
    (a, b) for a in range(2) for b in range(10) if (a, b) not in ((0, 0), (1, 0), (0, 5))
)


def bitset_check(positive: int, negative: int) -> bool:
    for first_shift, second_shift in SHIFT_ORDER:
        shifted_positive = shifted_mask(positive, first_shift, second_shift)
        shifted_negative = shifted_mask(negative, first_shift, second_shift)
        correlation = (
            popcount20(positive & shifted_positive)
            + popcount20(negative & shifted_negative)
            - popcount20(positive & shifted_negative)
            - popcount20(negative & shifted_positive)
        )
        if correlation != INSTANCE.lam:
            return False
    return True


def method_b(positive_masks: Sequence[int]) -> dict:
    """Audit the translation quotient with every negative pair and a bitset engine."""
    started = time.perf_counter()
    tested = 0
    for positive_mask in positive_masks:
        complement_positions = [i for i in range(INSTANCE.v) if not positive_mask & (1 << i)]
        for negatives in itertools.combinations(complement_positions, 2):
            negative_mask = (1 << negatives[0]) | (1 << negatives[1])
            tested += 1
            if bitset_check(positive_mask, negative_mask):
                return {
                    "name": "full_untranslated_c2xc10_bitset_search",
                    "assignments_tested": tested,
                    "complete": False,
                    "witness": vector_from_masks(positive_mask, negative_mask),
                    "runtime_seconds": time.perf_counter() - started,
                }
    return {
        "name": "full_untranslated_c2xc10_bitset_search",
        "assignments_tested": tested,
        "complete": True,
        "witness": None,
        "runtime_seconds": time.perf_counter() - started,
    }


def validation_report(vector: Optional[Sequence[int]]) -> Optional[dict]:
    if vector is None:
        return None
    return {
        "coefficient_vector": list(vector),
        "reference": validate_reference(INSTANCE, vector),
        "independent": validate_independent(INSTANCE, vector),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "artifacts" / "runs" / "v20_11_2_c2xc10_search.json",
    )
    args = parser.parse_args()
    started = datetime.now(timezone.utc).isoformat()
    positive_masks = masks_of_weight(20, 9)
    assert len(positive_masks) == math.comb(20, 9) == 167960
    a = method_a(positive_masks)
    b = method_b(positive_masks)
    reduced_total = 19 * math.comb(18, 9)
    full_total = math.comb(20, 2) * math.comb(18, 9)
    if a["witness"] is None:
        assert a["complete"] and a["assignments_tested"] == reduced_total == 923780
    if b["witness"] is None:
        assert b["complete"] and b["assignments_tested"] == full_total == 9237800
    assert (a["witness"] is None) == (b["witness"] is None)
    validations = {"method_a": validation_report(a["witness"]), "method_b": validation_report(b["witness"])}
    for report in validations.values():
        if report is not None:
            assert report["reference"]["valid"] and report["independent"]["valid"]
    dataset = ROOT / "sources" / "signed-difference-sets" / "sds.json"
    result = "NONEXISTENT_BY_EXHAUSTION" if a["witness"] is None else "EXISTS"
    report = {
        "schema": "v20-11-2-c2xc10-search-v1",
        "started_at_utc": started,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python3 scripts/run_v20_11_2_search.py --output artifacts/runs/v20_11_2_c2xc10_search.json",
        "instance": INSTANCE.name,
        "result": result,
        "method_a": a,
        "method_b": b,
        "validations": validations,
        "completeness_argument": [
            "The unreduced support-11 domain has C(20,11)*2^11=343982080 vectors.",
            "The trivial character gives (sum a_g)^2=11+2*(20-1)=49, so global sign permits normalization to sum +7.",
            "The normalized vector has nine +1, two -1, and nine zeros: C(20,2)*C(18,9)=9237800 assignments.",
            "Translation preserves the defining equation. Translating either negative element to the identity gives a representative counted by 19*C(18,9)=923780; duplicates do not affect completeness.",
            "Method B independently audits the translation quotient by checking all 9237800 normalized assignments with no translation restriction.",
            "Global sign is a bijection to the sum -7 assignments and preserves every autocorrelation."
        ],
        "deterministic_enumeration": True,
        "seed": None,
        "input": {"path": str(dataset.relative_to(ROOT)), "sha256": sha256(dataset)},
        "environment": {"python": platform.python_version(), "platform": platform.platform()}
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
