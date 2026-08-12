#!/usr/bin/env python3
"""Two-way order-5 character obstructions for the remaining C5 x C5 cases."""

from __future__ import annotations

import hashlib
import itertools
import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = (
    ("SDS(25,16,2,[5,5])", 16, 2, 8),
    ("SDS(25,24,5,[5,5])", 24, 5, 12),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def required_values(k, lam, principal_sum):
    n = k - lam
    numerator = principal_sum * principal_sum - n
    assert numerator % 5 == 0
    off_identity = numerator // 5
    identity = n + off_identity
    return n, identity, off_identity


def valid_fiber_sums(sequence, principal_sum, identity, off_identity):
    if sum(sequence) != principal_sum:
        return False
    correlation = [
        sum(sequence[j] * sequence[(j - shift) % 5] for j in range(5))
        for shift in range(5)
    ]
    return correlation[0] == identity and all(value == off_identity for value in correlation[1:])


def full_product_method(k, lam, principal_sum):
    started = time.perf_counter()
    _, identity, off_identity = required_values(k, lam, principal_sum)
    tested = 0
    principal_sum_candidates = 0
    solutions = []
    for sequence in itertools.product(range(-5, 6), repeat=5):
        tested += 1
        if sum(sequence) != principal_sum:
            continue
        principal_sum_candidates += 1
        if valid_fiber_sums(sequence, principal_sum, identity, off_identity):
            solutions.append(sequence)
    return {
        "name": "full_bounded_five_tuple_product",
        "bounded_tuples_tested": tested,
        "principal_sum_candidates": principal_sum_candidates,
        "solutions": solutions,
        "runtime_seconds": time.perf_counter() - started,
    }


def derived_coordinate_method(k, lam, principal_sum):
    """Independently derive the fifth cell sum from the first four."""
    started = time.perf_counter()
    _, identity, off_identity = required_values(k, lam, principal_sum)
    prefixes_tested = 0
    bounded_completed = 0
    square_sum_candidates = 0
    solutions = []
    for prefix in itertools.product(range(-5, 6), repeat=4):
        prefixes_tested += 1
        last = principal_sum - sum(prefix)
        if not -5 <= last <= 5:
            continue
        bounded_completed += 1
        sequence = prefix + (last,)
        if sum(value * value for value in sequence) != identity:
            continue
        square_sum_candidates += 1
        if all(
            sum(sequence[j] * sequence[(j - shift) % 5] for j in range(5)) == off_identity
            for shift in (1, 2, 3, 4)
        ):
            solutions.append(sequence)
    return {
        "name": "four_tuple_with_derived_fifth_coordinate",
        "prefixes_tested": prefixes_tested,
        "bounded_completed_tuples": bounded_completed,
        "identity_square_sum_candidates": square_sum_candidates,
        "solutions": solutions,
        "runtime_seconds": time.perf_counter() - started,
    }


def analyze(name, k, lam, principal_sum):
    n, identity, off_identity = required_values(k, lam, principal_sum)
    a = full_product_method(k, lam, principal_sum)
    b = derived_coordinate_method(k, lam, principal_sum)
    assert a["bounded_tuples_tested"] == 11**5 == 161051
    assert b["prefixes_tested"] == 11**4 == 14641
    assert set(map(tuple, a["solutions"])) == set(map(tuple, b["solutions"]))
    assert not a["solutions"]
    return {
        "instance": name,
        "result": "NONEXISTENT_BY_EXHAUSTIVE_CHARACTER_OBSTRUCTION",
        "principal_character_sum_normalized": principal_sum,
        "nonprincipal_character_norm": n,
        "required_fiber_autocorrelation": [identity] + [off_identity] * 4,
        "method_a": a,
        "method_b": b,
    }


def positive_control():
    k, lam, principal_sum = 12, 1, 6
    a = full_product_method(k, lam, principal_sum)
    b = derived_coordinate_method(k, lam, principal_sum)
    assert set(map(tuple, a["solutions"])) == set(map(tuple, b["solutions"]))
    witness = json.loads(
        (ROOT / "artifacts" / "witnesses" / "sds_25_12_1_c5xc5.json").read_text()
    )
    vector = witness["coefficient_vector"]
    row_sums = tuple(sum(vector[5 * row : 5 * row + 5]) for row in range(5))
    assert row_sums in set(map(tuple, a["solutions"]))
    return {
        "instance": "SDS(25,12,1,[5,5])",
        "allowed_fiber_sum_count": len(a["solutions"]),
        "allowed_fiber_sums": a["solutions"],
        "discovered_witness_row_sums": row_sums,
        "witness_row_sums_accepted": True,
    }


def main():
    started_at = datetime.now(timezone.utc).isoformat()
    results = [analyze(*case) for case in CASES]
    dataset = ROOT / "sources" / "signed-difference-sets" / "sds.json"
    report = {
        "schema": "v25-c5xc5-character-obstructions-v1",
        "started_at_utc": started_at,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python3 scripts/prove_v25_character_obstructions.py",
        "mathematical_argument": [
            "Fix any nonprincipal character chi of C5 x C5 and aggregate coefficients into its five fibers, obtaining integer sums s_0,...,s_4 in [-5,5].",
            "Applying chi to D D^-1=(k-lambda)e+lambda G gives |sum s_j*zeta^j|^2=n=k-lambda for a primitive fifth root zeta.",
            "If c_h=sum_j s_j*s_(j-h), then sum_h c_h*zeta^h=n. Since the degree-four polynomial sum_h c_h*x^h-n vanishes at zeta, it is an integer multiple of Phi_5(x)=1+x+x^2+x^3+x^4.",
            "Thus c_1=...=c_4=t and c_0=n+t. Evaluating at x=1 gives principal_sum^2=n+5t, fixing the entire required length-five autocorrelation.",
            "Method A exhausts every one of the 11^5 bounded integer fiber-sum tuples. Method B independently exhausts 11^4 prefixes and derives the fifth coordinate from the principal sum.",
            "Both enumerations find no feasible fiber sums for either target, so even one required nonprincipal character cannot exist; hence neither exact signed difference set exists."
        ],
        "results": results,
        "positive_control": positive_control(),
        "input": {"path": str(dataset.relative_to(ROOT)), "sha256": sha256(dataset)},
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "deterministic_enumeration": True,
        "seed": None,
    }
    output = ROOT / "artifacts" / "runs" / "v25_c5xc5_character_obstructions.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "output": str(output.relative_to(ROOT)),
        "sha256": sha256(output),
        "results": [(item["instance"], item["result"]) for item in results],
        "positive_control_allowed_count": report["positive_control"]["allowed_fiber_sum_count"],
        "positive_control_row_sums": report["positive_control"]["discovered_witness_row_sums"],
    }, indent=2))


if __name__ == "__main__":
    main()
