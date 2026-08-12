# Certified Census of Small Signed Difference Sets

This workspace resolves all 68 entries of group order at most 36 marked
`Open` in La Jolla Signed Difference Set Repository commit
`e3bf810c5ee6826cf5030f983f6adf23b0ffd20e`.

Final outcome: **16 EXIST and 52 NONEXISTENT; 0 unresolved**. The canonical
68-row machine-readable result is
`artifacts/census/current_census.json` (SHA-256
`11cd6bed9b7dcc1c23c66257f0765f2827c8aaefaf944ae4977bf6073cf08d9f`).
The human-readable synthesis is `FINAL_REPORT.md`.

## Evidence boundary

- Each existence result has an explicit coefficient vector in
  `artifacts/witnesses/` and passes both the tuple/dictionary reference
  validator and the structurally separate mixed-radix validator.
- Solver-based nonexistence uses exact CNF plus DRAT traces checked by an
  independently built `drat-trim`; 57 proof subcases are preserved.
- Other negative results use transparent character or quotient exhaustions,
  with separate verification programs for the final v=27, v=32, and v=36
  reductions.
- Raw `UNSAT`, timeouts, and failed searches remain non-evidence and are not
  consumed by `scripts/build_census.py`.

## Fast final audit

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/audit_final_census.py
python3 scripts/verify_v27_remaining_quotients.py
python3 scripts/verify_v32_remaining_quotients.py
python3 scripts/verify_v36_29_4_combined_quotients.py
```

The audit checks all 68 top-level evidence hashes, reruns both validators on
all 16 standalone witnesses, audits every stored formula/proof/checker hash,
requires `s VERIFIED` in all checker outputs, and checks the dated novelty
classification.

## Rebuild the frozen inputs

The upstream and prior-art repositories are intentionally ignored by the
outer Git repository:

```sh
mkdir -p sources
git clone https://github.com/dmgordo/signed-difference-sets.git \
  sources/signed-difference-sets
git -C sources/signed-difference-sets checkout --detach \
  e3bf810c5ee6826cf5030f983f6adf23b0ffd20e

git clone https://github.com/farev/Matematica.git \
  sources/novelty-farev-matematica
git -C sources/novelty-farev-matematica checkout --detach \
  a6a0805686e97f4a05bd7d9870d6e1648186afaf
```

Rebuild the manifests:

```sh
python3 scripts/build_snapshot.py
python3 scripts/build_census.py
python3 scripts/build_novelty_screen.py
```

Proof-generation scripts require `python-sat==1.9.dev13`. The checker source
commit and binary hash are embedded in every applicable subcase record.

## Novelty framing

The dated screen found an exact public predecessor at `farev/Matematica`,
with relevant commits on 2026-08-09. It independently agrees on 58 entries.
Those are classified as independently replicated, not novel. Ten entries are
novelty-supported because no earlier exact resolution was found after the
documented repository, literature, exact-parameter, alternate-notation, and
equivalence checks. Search is not proof of novelty.

The full entry-by-entry screen is
`artifacts/novelty/novelty_screen_2026-08-12.json`.

See `RESEARCH_LEDGER.md` for experiment history, failures, completeness
arguments, commands, runtimes, hashes, and decisions.
