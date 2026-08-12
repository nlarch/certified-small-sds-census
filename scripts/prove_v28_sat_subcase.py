#!/usr/bin/env python3
"""Generate and independently check one complete order-28 Walsh/SAT subcase."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sds.model import parse_name  # noqa: E402
from sds.sat_encoding import encode  # noqa: E402

NAMES = (
    "SDS(28,13,4,[2,14])",
    "SDS(28,19,10,[2,14])",
    "SDS(28,27,2,[2,14])",
)
CHECKER = ROOT / "tools" / "drat-trim-src" / "drat-trim"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def patterns(instance):
    principal = int((instance.k + instance.lam * 27) ** 0.5)
    nonprincipal = int((instance.k - instance.lam) ** 0.5)
    quotient = tuple(itertools.product((0, 1), repeat=2))
    result = []
    for signs in itertools.product((-nonprincipal, nonprincipal), repeat=3):
        spectrum = (principal,) + signs
        values = []
        for cell in quotient:
            numerator = sum(
                value * (-1 if sum(a * b for a, b in zip(character, cell)) % 2 else 1)
                for character, value in zip(quotient, spectrum)
            )
            if numerator % 4:
                break
            values.append(numerator // 4)
        else:
            if all(-7 <= value <= 7 for value in values):
                result.append(tuple(values))
    assert len(result) == 4
    return tuple(result)


def cells():
    result = [[], [], [], []]
    for index in range(28):
        first, second = divmod(index, 14)
        result[2 * first + second % 2].append(index)
    assert all(len(cell) == 7 for cell in result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-index", type=int, choices=range(3), required=True)
    parser.add_argument("--pattern-index", type=int, choices=range(4), required=True)
    args = parser.parse_args()
    instance = parse_name(NAMES[args.case_index])
    pattern = patterns(instance)[args.pattern_index]
    encoded = encode(instance, "totalizer")
    top = encoded.cnf.nv
    for cell, required_sum in zip(cells(), pattern):
        literals = [encoded.positive_variables[g] for g in cell] + [-encoded.negative_variables[g] for g in cell]
        constraint = CardEnc.equals(literals, required_sum + 7, top_id=top, encoding=EncType.totalizer)
        top = constraint.nv
        encoded.cnf.extend(constraint.clauses)
    directory = ROOT / "artifacts" / "sat" / "v28_subcases"
    directory.mkdir(parents=True, exist_ok=True)
    stem = directory / f"case_{args.case_index}_pattern_{args.pattern_index}"
    formula = stem.with_suffix(".cnf")
    proof = stem.with_suffix(".drat")
    checker_output = stem.with_suffix(".check.txt")
    report_path = stem.with_suffix(".json")
    encoded.cnf.to_file(str(formula), comments=[
        f"c instance {instance.name}",
        f"c complete real-character pattern {pattern}",
        "c totalizer encoding; full autocorrelation; global sign and translation normalized",
    ])
    started = time.perf_counter()
    with Solver(name="glucose4", bootstrap_with=encoded.cnf.clauses, with_proof=True) as solver:
        satisfiable = solver.solve()
        stats = solver.accum_stats()
        trace = None if satisfiable else solver.get_proof()
    solve_seconds = time.perf_counter() - started
    if satisfiable:
        raise SystemExit("unexpected SAT; use witness decoder before accepting")
    proof.write_text("\n".join(trace) + "\n")
    checked = subprocess.run(
        [str(CHECKER), str(formula), str(proof), "-f"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    checker_output.write_text(checked.stdout)
    verified = checked.returncode == 0 and "s VERIFIED" in checked.stdout
    if not verified:
        raise SystemExit("proof checker failure")
    report = {
        "schema": "v28-certified-sat-subcase-v1",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "instance": instance.name,
        "case_index": args.case_index,
        "pattern_index": args.pattern_index,
        "pattern": pattern,
        "all_patterns": patterns(instance),
        "result": "UNSAT",
        "solver": "Glucose4 via python-sat 1.9.dev13",
        "solve_seconds": solve_seconds,
        "solver_stats": stats,
        "formula": {"path": str(formula.relative_to(ROOT)), "sha256": sha256(formula), "variables": encoded.cnf.nv, "clauses": len(encoded.cnf.clauses)},
        "proof": {"path": str(proof.relative_to(ROOT)), "sha256": sha256(proof), "bytes": proof.stat().st_size, "format": "ASCII DRAT/DRUP"},
        "checker": {
            "verified": verified,
            "command": f"tools/drat-trim-src/drat-trim {formula.relative_to(ROOT)} {proof.relative_to(ROOT)} -f",
            "source_commit": subprocess.check_output(["git", "-C", str(CHECKER.parent), "rev-parse", "HEAD"], text=True).strip(),
            "binary_sha256": sha256(CHECKER),
            "output_path": str(checker_output.relative_to(ROOT)),
            "output_sha256": sha256(checker_output),
        },
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"instance": instance.name, "pattern": pattern, "solve_seconds": solve_seconds, "proof_bytes": proof.stat().st_size, "verified": verified}, indent=2))


if __name__ == "__main__":
    main()

