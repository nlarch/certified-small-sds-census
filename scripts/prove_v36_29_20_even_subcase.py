#!/usr/bin/env python3
"""Proof-producing quotient subcases for the remaining even v=36 groups."""

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

GROUPS = {"c2x18": (2, 18), "c6x6": (6, 6)}
ORDER3_TYPES = ((7, 10, 10), (11, 8, 8))
REAL_PATTERN = (9, 6, 6, 6)
CHECKER = ROOT / "tools" / "drat-trim-src" / "drat-trim"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_signed_sum(encoded, cell, required_sum, top):
    literals = [encoded.positive_variables[g] for g in cell]
    literals += [-encoded.negative_variables[g] for g in cell]
    constraint = CardEnc.equals(
        literals, required_sum + len(cell), top_id=top, encoding=EncType.totalizer
    )
    encoded.cnf.extend(constraint.clauses)
    return constraint.nv


def patterns_and_cells(tag, orbit_index):
    if tag == "c2x18":
        if orbit_index not in range(2):
            raise ValueError("c2x18 has orbit indices 0 and 1")
        order3_patterns = (ORDER3_TYPES[orbit_index],)
        real_cells = [[] for _ in range(4)]
        order3_cells = [[[] for _ in range(3)]]
        for g in range(36):
            first, second = divmod(g, 18)
            real_cells[2 * first + second % 2].append(g)
            order3_cells[0][second % 3].append(g)
        return order3_patterns, real_cells, order3_cells

    combinations = tuple(itertools.product(ORDER3_TYPES, repeat=2))
    if orbit_index not in range(4):
        raise ValueError("c6x6 has orbit indices 0 through 3")
    order3_patterns = combinations[orbit_index]
    real_cells = [[] for _ in range(4)]
    order3_cells = [[[] for _ in range(3)] for _ in range(2)]
    for g in range(36):
        first, second = divmod(g, 6)
        real_cells[2 * (first % 2) + second % 2].append(g)
        order3_cells[0][first % 3].append(g)
        order3_cells[1][second % 3].append(g)
    return order3_patterns, real_cells, order3_cells


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--group", choices=GROUPS, required=True)
    parser.add_argument("--orbit-index", type=int, required=True)
    args = parser.parse_args()
    group = GROUPS[args.group]
    instance = parse_name(f"SDS(36,29,20,[{','.join(map(str, group))}])")
    order3_patterns, real_cells, order3_cells = patterns_and_cells(
        args.group, args.orbit_index
    )

    encoded = encode(instance, "totalizer")
    translation_clause = [encoded.negative_variables[0]]
    assert encoded.cnf.clauses.count(translation_clause) == 1
    encoded.cnf.clauses.remove(translation_clause)
    top = encoded.cnf.nv
    for cell, required_sum in zip(real_cells, REAL_PATTERN):
        top = add_signed_sum(encoded, cell, required_sum, top)
    for cells, pattern in zip(order3_cells, order3_patterns):
        for cell, required_sum in zip(cells, pattern):
            top = add_signed_sum(encoded, cell, required_sum, top)

    directory = ROOT / "artifacts" / "sat" / "v36_29_20_even_subcases"
    directory.mkdir(parents=True, exist_ok=True)
    stem = directory / f"{args.group}_orbit_{args.orbit_index}"
    formula = stem.with_suffix(".cnf")
    proof = stem.with_suffix(".drat")
    checker_output = stem.with_suffix(".check.txt")
    report = stem.with_suffix(".json")
    encoded.cnf.to_file(
        str(formula),
        comments=[
            f"c instance {instance.name}",
            f"c real quotient pattern {REAL_PATTERN}",
            f"c order-three patterns {order3_patterns}",
            "c translations normalized by CRT quotient coordinates",
            "c exact totalizer full-autocorrelation encoding",
        ],
    )

    started = time.perf_counter()
    with Solver(name="glucose4", bootstrap_with=encoded.cnf.clauses, with_proof=True) as solver:
        answer = solver.solve()
        stats = solver.accum_stats()
        trace = None if answer else solver.get_proof()
    solve_seconds = time.perf_counter() - started
    if answer:
        raise SystemExit("unexpected SAT result")
    proof.write_text("\n".join(trace) + "\n")
    checked = subprocess.run(
        [str(CHECKER), str(formula), str(proof), "-f"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    checker_output.write_text(checked.stdout)
    verified = checked.returncode == 0 and "s VERIFIED" in checked.stdout
    if not verified:
        raise SystemExit("independent DRAT check failed")

    document = {
        "schema": "v36-29-20-even-subcase-v1",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "instance": instance.name,
        "group_tag": args.group,
        "orbit_index": args.orbit_index,
        "real_pattern": REAL_PATTERN,
        "order3_patterns": order3_patterns,
        "translation_fixed_negative_identity": False,
        "translation_normalized_by_quotient_patterns": True,
        "result": "UNSAT",
        "solve_seconds": solve_seconds,
        "solver_stats": stats,
        "formula": {
            "path": str(formula.relative_to(ROOT)),
            "sha256": sha256(formula),
            "variables": encoded.cnf.nv,
            "clauses": len(encoded.cnf.clauses),
        },
        "proof": {
            "path": str(proof.relative_to(ROOT)),
            "sha256": sha256(proof),
            "bytes": proof.stat().st_size,
        },
        "checker": {
            "verified": verified,
            "source_commit": subprocess.check_output(
                ["git", "-C", str(CHECKER.parent), "rev-parse", "HEAD"], text=True
            ).strip(),
            "binary_sha256": sha256(CHECKER),
            "output_path": str(checker_output.relative_to(ROOT)),
            "output_sha256": sha256(checker_output),
        },
    }
    report.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "group": args.group,
                "orbit": args.orbit_index,
                "seconds": solve_seconds,
                "proof_bytes": proof.stat().st_size,
                "verified": verified,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
