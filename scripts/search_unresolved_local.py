#!/usr/bin/env python3
"""Deterministic fixed-composition local search over unresolved census entries."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sds.model import parse_name  # noqa: E402
from sds.validator_independent import validate as validate_independent  # noqa: E402
from sds.validator_reference import validate as validate_reference  # noqa: E402


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digits(index, moduli):
    row = [0] * len(moduli)
    for j in range(len(moduli) - 1, -1, -1):
        row[j] = index % moduli[j]
        index //= moduli[j]
    return row


def rank(row, moduli):
    value = 0
    for digit, modulus in zip(row, moduli):
        value = value * modulus + digit
    return value


def tables(instance):
    coords = [digits(i, instance.group) for i in range(instance.v)]
    minus = [[0] * instance.v for _ in range(instance.v)]
    plus = [[0] * instance.v for _ in range(instance.v)]
    for h in range(instance.v):
        for g in range(instance.v):
            minus[h][g] = rank(
                [(coords[g][j] - coords[h][j]) % instance.group[j] for j in range(len(instance.group))],
                instance.group,
            )
            plus[h][g] = rank(
                [(coords[g][j] + coords[h][j]) % instance.group[j] for j in range(len(instance.group))],
                instance.group,
            )
    return minus, plus


def composition(instance):
    square = instance.k + instance.lam * (instance.v - 1)
    augmentation = math.isqrt(square)
    assert augmentation * augmentation == square
    return (instance.k + augmentation) // 2, (instance.k - augmentation) // 2, instance.v - instance.k


def correlations(vector, minus):
    return [sum(vector[g] * vector[row[g]] for g in range(len(vector))) for row in minus]


def objective(instance, corr):
    return sum((value - instance.lam) ** 2 for value in corr[1:])


def proposed_correlations(vector, corr, p, q, minus, plus):
    old_p, old_q = vector[p], vector[q]

    def new_value(position):
        return old_q if position == p else old_p if position == q else vector[position]

    result = list(corr)
    for shift in range(len(vector)):
        affected = {p, q, plus[shift][p], plus[shift][q]}
        old = sum(vector[g] * vector[minus[shift][g]] for g in affected)
        new = sum(new_value(g) * new_value(minus[shift][g]) for g in affected)
        result[shift] += new - old
    return result


def restart(instance, seed, steps, minus, plus):
    rng = random.Random(seed)
    positive, negative, zero = composition(instance)
    vector = [1] * positive + [-1] * negative + [0] * zero
    rng.shuffle(vector)
    corr = correlations(vector, minus)
    current = objective(instance, corr)
    best = current
    best_vector = tuple(vector)
    accepted = 0
    for step in range(steps):
        p = rng.randrange(instance.v)
        q = rng.randrange(instance.v - 1)
        if q >= p:
            q += 1
        if vector[p] == vector[q]:
            continue
        candidate_corr = proposed_correlations(vector, corr, p, q, minus, plus)
        candidate = objective(instance, candidate_corr)
        fraction = step / max(1, steps - 1)
        temperature = 12.0 * (0.01 / 12.0) ** fraction
        delta = candidate - current
        if delta <= 0 or rng.random() < math.exp(-delta / temperature):
            vector[p], vector[q] = vector[q], vector[p]
            corr = candidate_corr
            current = candidate
            accepted += 1
            if current < best:
                best = current
                best_vector = tuple(vector)
                if best == 0:
                    break
    return {"seed": seed, "best_objective": best, "best_vector": best_vector, "accepted_moves": accepted}


def search(instance, restarts, steps, seed_offset):
    started = time.perf_counter()
    minus, plus = tables(instance)
    runs = []
    witness = None
    for local_seed in range(restarts):
        run = restart(instance, seed_offset + local_seed, steps, minus, plus)
        runs.append(run)
        if run["best_objective"] == 0:
            witness = tuple(run["best_vector"])
            break
    best_run = min(runs, key=lambda item: item["best_objective"])
    validation = None
    if witness:
        validation = {
            "coefficient_vector": witness,
            "reference": validate_reference(instance, witness),
            "independent": validate_independent(instance, witness),
        }
        assert validation["reference"]["valid"] and validation["independent"]["valid"]
    return {
        "instance": instance.name,
        "result": "EXISTS" if witness else "NO_CONSTRUCTION_FOUND",
        "composition_positive_negative_zero": composition(instance),
        "restarts_completed": len(runs),
        "steps_per_restart": steps,
        "seed_offset": seed_offset,
        "best_objective": best_run["best_objective"],
        "best_vector": best_run["best_vector"],
        "runs": runs,
        "validation": validation,
        "runtime_seconds": time.perf_counter() - started,
        "evidence_warning": None if witness else "Heuristic failure is not nonexistence evidence.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--v", type=int, required=True)
    parser.add_argument("--restarts", type=int, default=16)
    parser.add_argument("--steps", type=int, default=3000)
    args = parser.parse_args()
    census_path = ROOT / "artifacts" / "census" / "current_census.json"
    census = json.loads(census_path.read_text())
    names = [
        row["name"] for row in census["entries"]
        if row["v"] == args.v and row["project_status"] == "UNRESOLVED"
    ]
    report = {
        "schema": "unresolved-fixed-composition-local-search-v1",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": f"python3 scripts/search_unresolved_local.py --v {args.v} --restarts {args.restarts} --steps {args.steps}",
        "v": args.v,
        "instances": [
            search(parse_name(name), args.restarts, args.steps, 100000 * args.v + 1000 * index)
            for index, name in enumerate(names)
        ],
        "input": {"path": str(census_path.relative_to(ROOT)), "sha256": sha256(census_path)},
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    output = ROOT / "artifacts" / "runs" / f"v{args.v}_unresolved_local_search.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "output": str(output.relative_to(ROOT)),
        "sha256": sha256(output),
        "results": [
            [item["instance"], item["result"], item["best_objective"], item["restarts_completed"]]
            for item in report["instances"]
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
