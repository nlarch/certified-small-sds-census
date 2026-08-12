#!/usr/bin/env python3
"""Fixed-composition local search for the two frozen order-24 Open entries."""

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
from typing import List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sds.model import Instance, parse_name  # noqa: E402
from sds.validator_independent import validate as validate_independent  # noqa: E402
from sds.validator_reference import validate as validate_reference  # noqa: E402

INSTANCES = (
    parse_name("SDS(24,18,2,[2,12])"),
    parse_name("SDS(24,18,2,[2,2,6])"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digits(index: int, moduli: Sequence[int]) -> List[int]:
    result = [0] * len(moduli)
    for j in range(len(moduli) - 1, -1, -1):
        result[j] = index % moduli[j]
        index //= moduli[j]
    return result


def rank(coords: Sequence[int], moduli: Sequence[int]) -> int:
    result = 0
    for value, modulus in zip(coords, moduli):
        result = result * modulus + value
    return result


def operation_tables(instance: Instance) -> Tuple[List[List[int]], List[List[int]]]:
    rows = [digits(i, instance.group) for i in range(instance.v)]
    minus = [[0] * instance.v for _ in range(instance.v)]
    plus = [[0] * instance.v for _ in range(instance.v)]
    for shift in range(instance.v):
        for left in range(instance.v):
            minus[shift][left] = rank(
                [(rows[left][j] - rows[shift][j]) % instance.group[j] for j in range(len(instance.group))],
                instance.group,
            )
            plus[shift][left] = rank(
                [(rows[left][j] + rows[shift][j]) % instance.group[j] for j in range(len(instance.group))],
                instance.group,
            )
    return minus, plus


def correlations(vector: Sequence[int], minus: Sequence[Sequence[int]]) -> List[int]:
    return [sum(vector[g] * vector[row[g]] for g in range(len(vector))) for row in minus]


def objective(instance: Instance, corr: Sequence[int]) -> int:
    return sum((value - instance.lam) ** 2 for value in corr[1:])


def swapped_correlations(
    vector: Sequence[int],
    corr: Sequence[int],
    p: int,
    q: int,
    minus: Sequence[Sequence[int]],
    plus: Sequence[Sequence[int]],
) -> List[int]:
    old_p, old_q = vector[p], vector[q]

    def new_value(position: int) -> int:
        if position == p:
            return old_q
        if position == q:
            return old_p
        return vector[position]

    result = list(corr)
    for shift in range(len(vector)):
        affected = {p, q, plus[shift][p], plus[shift][q]}
        old_total = sum(vector[g] * vector[minus[shift][g]] for g in affected)
        new_total = sum(new_value(g) * new_value(minus[shift][g]) for g in affected)
        result[shift] += new_total - old_total
    return result


def one_restart(instance: Instance, seed: int, steps: int) -> dict:
    rng = random.Random(seed)
    # Sum +8 and support 18 force thirteen +1, five -1, six zero.
    vector = [1] * 13 + [-1] * 5 + [0] * 6
    rng.shuffle(vector)
    minus, plus = operation_tables(instance)
    corr = correlations(vector, minus)
    score = objective(instance, corr)
    best_score = score
    best_vector = tuple(vector)
    accepted = 0
    for step in range(steps):
        p = rng.randrange(instance.v)
        q = rng.randrange(instance.v - 1)
        if q >= p:
            q += 1
        if vector[p] == vector[q]:
            continue
        proposal = swapped_correlations(vector, corr, p, q, minus, plus)
        proposal_score = objective(instance, proposal)
        fraction = step / max(1, steps - 1)
        temperature = 8.0 * (0.01 / 8.0) ** fraction
        delta = proposal_score - score
        if delta <= 0 or rng.random() < math.exp(-delta / temperature):
            vector[p], vector[q] = vector[q], vector[p]
            corr = proposal
            score = proposal_score
            accepted += 1
            if score < best_score:
                best_score = score
                best_vector = tuple(vector)
                if score == 0:
                    break
    return {
        "seed": seed,
        "steps_budget": steps,
        "best_objective": best_score,
        "best_vector": best_vector,
        "accepted_moves": accepted,
    }


def search_instance(instance: Instance, restarts: int, steps: int) -> dict:
    started = time.perf_counter()
    runs = []
    witness: Optional[Tuple[int, ...]] = None
    for seed in range(restarts):
        run = one_restart(instance, seed, steps)
        runs.append(run)
        if run["best_objective"] == 0:
            witness = tuple(run["best_vector"])
            break
    validation = None
    if witness is not None:
        validation = {
            "coefficient_vector": witness,
            "reference": validate_reference(instance, witness),
            "independent": validate_independent(instance, witness),
        }
        assert validation["reference"]["valid"]
        assert validation["independent"]["valid"]
    best = min(runs, key=lambda run: run["best_objective"])
    return {
        "instance": instance.name,
        "result": "EXISTS" if witness is not None else "NO_CONSTRUCTION_FOUND",
        "restarts_completed": len(runs),
        "steps_per_restart": steps,
        "best_objective": best["best_objective"],
        "best_vector": best["best_vector"],
        "runs": runs,
        "validation": validation,
        "runtime_seconds": time.perf_counter() - started,
        "evidence_warning": None if witness is not None else "Heuristic failure is not nonexistence evidence.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--restarts", type=int, default=32)
    parser.add_argument("--steps", type=int, default=5000)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "artifacts" / "runs" / "v24_local_search.json",
    )
    args = parser.parse_args()
    dataset = ROOT / "sources" / "signed-difference-sets" / "sds.json"
    report = {
        "schema": "v24-fixed-composition-local-search-v1",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": f"python3 scripts/search_v24_local.py --restarts {args.restarts} --steps {args.steps} --output artifacts/runs/v24_local_search.json",
        "algorithm": "deterministically seeded simulated annealing over swaps preserving 13 positive, 5 negative, and 6 zero coefficients",
        "instances": [search_instance(instance, args.restarts, args.steps) for instance in INSTANCES],
        "input": {"path": str(dataset.relative_to(ROOT)), "sha256": sha256(dataset)},
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
