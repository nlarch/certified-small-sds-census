#!/usr/bin/env python3
"""Exact SAT witness search for the two unresolved order-25 targets."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from pysat.solvers import Solver

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sds.model import parse_name  # noqa: E402
from sds.sat_encoding import decode, encode  # noqa: E402
from sds.validator_independent import validate as validate_independent  # noqa: E402
from sds.validator_reference import validate as validate_reference  # noqa: E402

NAMES = (
    "SDS(25,16,2,[5,5])",
    "SDS(25,24,5,[5,5])",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-index", type=int, choices=(0, 1), required=True)
    parser.add_argument("--solver", choices=("glucose4", "kissat404", "maplechrono"), default="glucose4")
    args = parser.parse_args()
    instance = parse_name(NAMES[args.case_index])
    started_at = datetime.now(timezone.utc).isoformat()
    build_started = time.perf_counter()
    encoded = encode(instance, "totalizer")
    build_seconds = time.perf_counter() - build_started
    formula_dir = ROOT / "artifacts" / "sat" / "v25"
    formula_dir.mkdir(parents=True, exist_ok=True)
    slug = f"v25_{instance.k}_{instance.lam}_c5xc5_totalizer"
    formula_path = formula_dir / f"{slug}.cnf"
    encoded.cnf.to_file(
        str(formula_path),
        comments=[
            f"c instance {instance.name}",
            "c exact totalizer encoding; global sign normalized; negative at identity fixed by translation",
            "c full equivalence for all product auxiliaries and every nonidentity autocorrelation equation",
        ],
    )
    solve_started = time.perf_counter()
    with Solver(name=args.solver, bootstrap_with=encoded.cnf.clauses) as solver:
        satisfiable = solver.solve()
        stats = solver.accum_stats()
        model = solver.get_model() if satisfiable else None
    solve_seconds = time.perf_counter() - solve_started
    validation = None
    if model is not None:
        vector = decode(encoded, model)
        validation = {
            "coefficient_vector": vector,
            "reference": validate_reference(instance, vector),
            "independent": validate_independent(instance, vector),
        }
        assert validation["reference"]["valid"] and validation["independent"]["valid"]
    result = "EXISTS" if satisfiable else "UNSAT_UNCERTIFIED"
    report = {
        "schema": "v25-exact-sat-search-v1",
        "started_at_utc": started_at,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "instance": instance.name,
        "result": result,
        "solver": f"{args.solver} via python-sat 1.9.dev13",
        "encoding": encoded.metadata,
        "formula": {"path": str(formula_path.relative_to(ROOT)), "sha256": sha256(formula_path)},
        "build_seconds": build_seconds,
        "solve_seconds": solve_seconds,
        "solver_stats": stats,
        "validation": validation,
        "warning": None if satisfiable else "UNSAT is not accepted without an independently checked proof.",
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
    }
    output = ROOT / "artifacts" / "runs" / f"{slug}_{args.solver}.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "output": str(output.relative_to(ROOT)),
        "instance": instance.name,
        "result": result,
        "solve_seconds": solve_seconds,
        "formula_sha256": report["formula"]["sha256"],
        "coefficient_vector": None if validation is None else validation["coefficient_vector"],
    }, indent=2))


if __name__ == "__main__":
    main()
