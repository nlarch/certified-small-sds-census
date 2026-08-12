#!/usr/bin/env python3
"""Two-way Walsh obstruction for SDS(24,18,2,[2,2,6])."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTANCE = "SDS(24,18,2,[2,2,6])"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dot_mod2(left, right):
    return sum(a * b for a, b in zip(left, right)) % 2


def method_a():
    """Enumerate the seven nonprincipal character signs and invert Walsh."""
    started = time.perf_counter()
    quotient = tuple(itertools.product((0, 1), repeat=3))
    nonprincipal = quotient[1:]
    tested = 0
    integral_inverses = 0
    bounded_inverses = []
    for signs in itertools.product((-4, 4), repeat=7):
        tested += 1
        spectrum = {(0, 0, 0): 8}
        spectrum.update(dict(zip(nonprincipal, signs)))
        cell_sums = []
        for cell in quotient:
            numerator = sum(
                spectrum[character] * (-1 if dot_mod2(character, cell) else 1)
                for character in quotient
            )
            if numerator % 8:
                break
            cell_sums.append(numerator // 8)
        else:
            integral_inverses += 1
            if all(-3 <= value <= 3 for value in cell_sums):
                bounded_inverses.append(tuple(cell_sums))
    return {
        "name": "character_signs_to_inverse_walsh",
        "sign_patterns_tested": tested,
        "integral_inverse_patterns": integral_inverses,
        "bounded_inverse_patterns": bounded_inverses,
        "runtime_seconds": time.perf_counter() - started,
    }


def method_b():
    """Independently enumerate bounded cell sums and transform forward."""
    started = time.perf_counter()
    quotient = tuple(itertools.product((0, 1), repeat=3))
    total_tuples = 0
    principal_sum_eight = 0
    feasible_spectra = []
    for cell_sums in itertools.product(range(-3, 4), repeat=8):
        total_tuples += 1
        if sum(cell_sums) != 8:
            continue
        principal_sum_eight += 1
        transform = []
        for character in quotient[1:]:
            transform.append(
                sum(
                    cell_sums[index] * (-1 if dot_mod2(character, cell) else 1)
                    for index, cell in enumerate(quotient)
                )
            )
        if all(abs(value) == 4 for value in transform):
            feasible_spectra.append({"cell_sums": cell_sums, "nonprincipal_transform": transform})
    return {
        "name": "bounded_cell_sums_to_forward_walsh",
        "bounded_tuples_tested": total_tuples,
        "principal_sum_eight_tuples": principal_sum_eight,
        "feasible_spectra": feasible_spectra,
        "runtime_seconds": time.perf_counter() - started,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "artifacts" / "runs" / "v24_18_2_c2c2c6_walsh_proof.json",
    )
    args = parser.parse_args()
    started_at = datetime.now(timezone.utc).isoformat()
    a = method_a()
    b = method_b()
    assert a["sign_patterns_tested"] == 2**7 == 128
    assert not a["bounded_inverse_patterns"]
    assert b["bounded_tuples_tested"] == 7**8 == 5764801
    assert not b["feasible_spectra"]
    dataset = ROOT / "sources" / "signed-difference-sets" / "sds.json"
    report = {
        "schema": "v24-c2c2c6-walsh-nonexistence-v1",
        "started_at_utc": started_at,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python3 scripts/prove_v24_c2c2c6_nonexistence.py --output artifacts/runs/v24_18_2_c2c2c6_walsh_proof.json",
        "instance": INSTANCE,
        "result": "NONEXISTENT_BY_EXHAUSTIVE_CHARACTER_OBSTRUCTION",
        "mathematical_argument": [
            "The real-character quotient of C2 x C2 x C6 is G/2G congruent to C2^3; its eight cosets each contain three group elements.",
            "For any signed (24,18,2) set, applying a nonprincipal real character to D D^-1 = 16e + 2G gives chi(D)^2=16, hence chi(D) is +4 or -4.",
            "Global sign permits the principal character sum to be fixed at +8 because its square is 18+2*23=64.",
            "Writing the eight coset coefficient sums as integers s_x, each lies in [-3,3]. Their Walsh transform has principal value 8 and seven nonprincipal values in {+4,-4}.",
            "Method A exhausts all 2^7 possible nonprincipal signs and inverse-transforms them; no inverse has all coordinates in [-3,3].",
            "Method B independently exhausts all 7^8 bounded integer cell-sum tuples, filters principal sum 8, and forward-transforms; none has all seven nonprincipal magnitudes 4.",
            "Therefore no coefficient vector can satisfy the character consequences of the defining equation, so the exact named signed difference set does not exist."
        ],
        "method_a": a,
        "method_b": b,
        "input": {"path": str(dataset.relative_to(ROOT)), "sha256": sha256(dataset)},
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "deterministic_enumeration": True,
        "seed": None
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
