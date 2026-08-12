#!/usr/bin/env python3
"""Deterministic fixed-composition local search for the order-25 targets."""

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

INSTANCES = tuple(
    parse_name(name)
    for name in (
        "SDS(25,12,1,[5,5])",
        "SDS(25,16,2,[5,5])",
        "SDS(25,24,5,[5,5])",
    )
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tables(instance):
    coords = [(i // 5, i % 5) for i in range(25)]
    minus = [[0] * 25 for _ in range(25)]
    plus = [[0] * 25 for _ in range(25)]
    for h, (ha, hb) in enumerate(coords):
        for g, (ga, gb) in enumerate(coords):
            minus[h][g] = ((ga - ha) % 5) * 5 + (gb - hb) % 5
            plus[h][g] = ((ga + ha) % 5) * 5 + (gb + hb) % 5
    return minus, plus


def correlations(vector, minus):
    return [sum(vector[g] * vector[row[g]] for g in range(25)) for row in minus]


def score(instance, corr):
    return sum((value - instance.lam) ** 2 for value in corr[1:])


def proposal_correlations(vector, corr, p, q, minus, plus):
    old_p, old_q = vector[p], vector[q]

    def new_value(position):
        return old_q if position == p else old_p if position == q else vector[position]

    result = list(corr)
    for shift in range(25):
        affected = {p, q, plus[shift][p], plus[shift][q]}
        old = sum(vector[g] * vector[minus[shift][g]] for g in affected)
        new = sum(new_value(g) * new_value(minus[shift][g]) for g in affected)
        result[shift] += new - old
    return result


def composition(instance):
    augmentation_square = instance.k + instance.lam * (instance.v - 1)
    augmentation = math.isqrt(augmentation_square)
    assert augmentation * augmentation == augmentation_square
    return (instance.k + augmentation) // 2, (instance.k - augmentation) // 2, instance.v - instance.k


def restart(instance, seed, steps, minus, plus):
    rng = random.Random(seed)
    positive, negative, zero = composition(instance)
    vector = [1] * positive + [-1] * negative + [0] * zero
    rng.shuffle(vector)
    corr = correlations(vector, minus)
    current = score(instance, corr)
    best = current
    best_vector = tuple(vector)
    accepted = 0
    for step in range(steps):
        p = rng.randrange(25)
        q = rng.randrange(24)
        if q >= p:
            q += 1
        if vector[p] == vector[q]:
            continue
        candidate_corr = proposal_correlations(vector, corr, p, q, minus, plus)
        candidate = score(instance, candidate_corr)
        fraction = step / max(1, steps - 1)
        temperature = 10.0 * (0.01 / 10.0) ** fraction
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
    return {
        "seed": seed,
        "best_objective": best,
        "best_vector": best_vector,
        "accepted_moves": accepted,
        "steps_budget": steps,
    }


def search(instance, restarts, steps):
    started = time.perf_counter()
    minus, plus = tables(instance)
    runs = []
    witness = None
    for seed in range(restarts):
        run = restart(instance, seed, steps, minus, plus)
        runs.append(run)
        if run["best_objective"] == 0:
            witness = tuple(run["best_vector"])
            break
    validation = None
    if witness:
        validation = {
            "coefficient_vector": witness,
            "reference": validate_reference(instance, witness),
            "independent": validate_independent(instance, witness),
        }
        assert validation["reference"]["valid"] and validation["independent"]["valid"]
    best_run = min(runs, key=lambda item: item["best_objective"])
    return {
        "instance": instance.name,
        "result": "EXISTS" if witness else "NO_CONSTRUCTION_FOUND",
        "composition_positive_negative_zero": composition(instance),
        "restarts_completed": len(runs),
        "steps_per_restart": steps,
        "best_objective": best_run["best_objective"],
        "best_vector": best_run["best_vector"],
        "runs": runs,
        "validation": validation,
        "runtime_seconds": time.perf_counter() - started,
        "evidence_warning": None if witness else "Heuristic failure is not nonexistence evidence.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--restarts", type=int, default=64)
    parser.add_argument("--steps", type=int, default=5000)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "artifacts" / "runs" / "v25_local_search.json",
    )
    args = parser.parse_args()
    dataset = ROOT / "sources" / "signed-difference-sets" / "sds.json"
    report = {
        "schema": "v25-fixed-composition-local-search-v1",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": f"python3 scripts/search_v25_local.py --restarts {args.restarts} --steps {args.steps} --output artifacts/runs/v25_local_search.json",
        "instances": [search(instance, args.restarts, args.steps) for instance in INSTANCES],
        "input": {"path": str(dataset.relative_to(ROOT)), "sha256": sha256(dataset)},
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
