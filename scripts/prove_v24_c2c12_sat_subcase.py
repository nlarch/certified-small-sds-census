#!/usr/bin/env python3
"""Generate, solve, and independently check one Fourier-complete SAT subcase."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
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
from sds.sat_encoding import decode, encode  # noqa: E402
from sds.validator_independent import validate as validate_independent  # noqa: E402
from sds.validator_reference import validate as validate_reference  # noqa: E402

INSTANCE = parse_name("SDS(24,18,2,[2,12])")
CHECKER = ROOT / "tools" / "drat-trim-src" / "drat-trim"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def walsh_patterns():
    quotient = tuple(itertools.product((0, 1), repeat=2))
    patterns = []
    for signs in itertools.product((-4, 4), repeat=3):
        spectrum = (8,) + signs
        inverse = []
        for cell in quotient:
            numerator = 0
            for character, value in zip(quotient, spectrum):
                parity = sum(a * b for a, b in zip(character, cell)) % 2
                numerator += value * (-1 if parity else 1)
            assert numerator % 4 == 0
            inverse.append(numerator // 4)
        if all(-6 <= value <= 6 for value in inverse):
            patterns.append(tuple(inverse))
    assert len(patterns) == len(set(patterns)) == 8
    return tuple(patterns)


def parity_cells():
    # Mixed-radix index for [2,12] is 12*a+b.
    cells = [[], [], [], []]
    for index in range(24):
        first, second = divmod(index, 12)
        cells[2 * first + (second % 2)].append(index)
    assert all(len(cell) == 6 for cell in cells)
    return cells


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pattern-index", type=int, required=True, choices=range(8))
    args = parser.parse_args()
    started_at = datetime.now(timezone.utc).isoformat()
    pattern = walsh_patterns()[args.pattern_index]
    encoded = encode(INSTANCE, "totalizer")
    top = encoded.cnf.nv
    for cell, required_sum in zip(parity_cells(), pattern):
        # sum(p)-sum(n)=s iff sum(p)+sum(not n)=s+6.
        literals = [encoded.positive_variables[g] for g in cell] + [
            -encoded.negative_variables[g] for g in cell
        ]
        constraint = CardEnc.equals(
            literals,
            bound=required_sum + 6,
            top_id=top,
            encoding=EncType.totalizer,
        )
        top = constraint.nv
        encoded.cnf.extend(constraint.clauses)

    artifact_dir = ROOT / "artifacts" / "sat" / "v24_c2c12_subcases"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    stem = artifact_dir / f"pattern_{args.pattern_index}"
    formula_path = stem.with_suffix(".cnf")
    proof_path = stem.with_suffix(".drat")
    checker_path = stem.with_suffix(".check.txt")
    report_path = stem.with_suffix(".json")
    encoded.cnf.to_file(
        str(formula_path),
        comments=[
            f"c instance {INSTANCE.name}",
            f"c real-character parity-cell pattern index {args.pattern_index}: {pattern}",
            "c base encoding: totalizer, global sign normalized, one negative fixed at identity by translation",
            "c cell constraint: sum(p)+sum(not n)=cell_sum+6",
        ],
    )

    solve_started = time.perf_counter()
    with Solver(name="glucose4", bootstrap_with=encoded.cnf.clauses, with_proof=True) as solver:
        satisfiable = solver.solve()
        stats = solver.accum_stats()
        model = solver.get_model() if satisfiable else None
        proof = None if satisfiable else solver.get_proof()
    solve_seconds = time.perf_counter() - solve_started

    validation = None
    checker = None
    if satisfiable:
        vector = decode(encoded, model)
        validation = {
            "coefficient_vector": vector,
            "reference": validate_reference(INSTANCE, vector),
            "independent": validate_independent(INSTANCE, vector),
        }
        assert validation["reference"]["valid"] and validation["independent"]["valid"]
    else:
        proof_path.write_text("\n".join(proof) + "\n")
        checked = subprocess.run(
            [str(CHECKER), str(formula_path), str(proof_path), "-f"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        checker_path.write_text(checked.stdout)
        checker = {
            "name": "drat-trim",
            "source_repository": "https://github.com/marijnheule/drat-trim",
            "source_commit": subprocess.check_output(
                ["git", "-C", str(CHECKER.parent), "rev-parse", "HEAD"], text=True
            ).strip(),
            "binary_path": str(CHECKER.relative_to(ROOT)),
            "binary_sha256": sha256(CHECKER),
            "command": f"{CHECKER.relative_to(ROOT)} {formula_path.relative_to(ROOT)} {proof_path.relative_to(ROOT)} -f",
            "mode": "forward verification (lower memory)",
            "exit_code": checked.returncode,
            "verified": checked.returncode == 0 and "s VERIFIED" in checked.stdout,
            "output_path": str(checker_path.relative_to(ROOT)),
            "output_sha256": sha256(checker_path),
        }
        if not checker["verified"]:
            raise SystemExit("DRAT proof did not pass independent checking")

    report = {
        "schema": "v24-c2c12-certified-sat-subcase-v1",
        "started_at_utc": started_at,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "instance": INSTANCE.name,
        "pattern_index": args.pattern_index,
        "pattern": pattern,
        "all_eight_patterns": walsh_patterns(),
        "result": "SAT" if satisfiable else "UNSAT",
        "solver": "Glucose4 via python-sat 1.9.dev13",
        "solve_seconds": solve_seconds,
        "solver_stats": stats,
        "formula": {
            "path": str(formula_path.relative_to(ROOT)),
            "sha256": sha256(formula_path),
            "variables": encoded.cnf.nv,
            "clauses": len(encoded.cnf.clauses),
        },
        "proof": None if satisfiable else {
            "path": str(proof_path.relative_to(ROOT)),
            "sha256": sha256(proof_path),
            "bytes": proof_path.stat().st_size,
            "format": "ASCII DRAT/DRUP emitted by Glucose4",
        },
        "checker": checker,
        "validation": validation,
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "report": str(report_path.relative_to(ROOT)),
        "pattern": pattern,
        "result": report["result"],
        "solve_seconds": solve_seconds,
        "proof_bytes": None if satisfiable else proof_path.stat().st_size,
        "checker_verified": None if satisfiable else checker["verified"],
    }, indent=2))


if __name__ == "__main__":
    main()
