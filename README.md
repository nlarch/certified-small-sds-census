# Certified Census of Small Signed Difference Sets

This workspace resolves the 68 entries of group order at most 36 marked
`Open` in La Jolla Signed Difference Set Repository commit
`e3bf810c5ee6826cf5030f983f6adf23b0ffd20e`.

The checked-out upstream repository is intentionally ignored by the outer Git
repository. Recreate it with:

```sh
mkdir -p sources
git clone https://github.com/dmgordo/signed-difference-sets.git \
  sources/signed-difference-sets
git -C sources/signed-difference-sets checkout --detach \
  e3bf810c5ee6826cf5030f983f6adf23b0ffd20e
```

Reproduce the current evidence:

```sh
python3 scripts/build_snapshot.py
python3 -m unittest discover -s tests -v
python3 scripts/run_order9_exhaustion.py
python3 scripts/run_v20_17_8_exhaustion.py
python3 scripts/run_v18_15_2_exhaustion.py
python3 scripts/build_census.py
```

See `RESEARCH_LEDGER.md` for the exact completeness arguments, runtimes,
hashes, validation state, failed hypotheses, and next experiment. The current
68-row status artifact is `artifacts/census/current_census.json`.

Checkpoint 2026-08-12: 38 of 68 frozen entries are resolved (12 explicit
constructions and 26 certified nonexistence results); 30 remain unresolved.
