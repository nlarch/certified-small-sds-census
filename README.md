# Certified Census of Small Signed Difference Sets

## Main theorems

**Theorem 1 (order 32 classification).** A signed `(32,20,4)`
difference set exists in an abelian group of order 32 if and only if the group
is noncyclic. Explicit, independently validated constructions are supplied for

```text
C2 x C16, C4 x C8, C2 x C2 x C8, C2 x C4 x C4,
C2 x C2 x C2 x C4, and C2 x C2 x C2 x C2 x C2.
```

For `C32`, a complete `C8 -> C16 -> C32` quotient refinement exhausts all
possibilities and finds none.

**Theorem 2 (the previously open noncyclic order 36 cases).** None of

```text
C2 x C18, C3 x C12, and C6 x C6
```

admits a signed `(36,29,4)` difference set. The first two cases are excluded
by complete quotient enumerations. For `C6 x C6`, quotient reductions leave
one normalized orbit, whose exact CNF formula is proved unsatisfiable by a
DRAT certificate checked independently with `drat-trim`.

The frozen repository already recorded the cyclic `C36` case as
nonexistent. Consequently, the theorem established here together with that
earlier result closes `(36,29,4)` for every abelian group of order 36.

These are the two principal mathematical results. The complete 68-entry
census described below is the broader verification project in which they were
obtained.

The accompanying English note is available as
[`paper/two_small_order_classifications.md`](paper/two_small_order_classifications.md)
and as a visually checked 10-page
[`PDF`](output/pdf/two_small_order_classifications.pdf).

## What is this project about?

This is a computer-assisted mathematics project about arranging `+1`, `-1`,
and `0` values on a finite symmetric space so that the arrangement has exactly
the same correlation in every nontrivial direction.

These arrangements are called **signed difference sets**. They are studied in
combinatorics and connect to objects used in coding theory, signal processing,
and experimental design. The central question is simple to state:

> For a given finite group and a given set of numerical parameters, does such
> a perfectly balanced signed arrangement exist?

Before this project, the frozen La Jolla Signed Difference Set Repository
listed 68 small cases as `Open`, meaning that the database recorded neither a
construction nor a proof of impossibility. This workspace determines the
answer to every one of those cases with group order at most 36.

## What is a signed difference set?

Start with a finite group `G` containing `v` positions. For a beginner, it is
enough to picture `G` as a cycle or a multidimensional wrap-around grid. Give
each position a coefficient chosen from:

- `+1`: a positive selected position;
- `-1`: a negative selected position;
- `0`: an unused position.

Exactly `k` positions must be nonzero. Now shift the entire pattern by each
possible group element and compare the shifted pattern with the original one.
The sum of the products of aligned coefficients is its periodic
**autocorrelation**.

A signed `(v,k,lambda)` difference set must have:

- autocorrelation `k` when it is not shifted; and
- the same autocorrelation `lambda` for every nonzero shift.

In group-ring notation, the condition is

```text
D D^(-1) = (k - lambda)e + lambda G.
```

The computational validators do not assume that a promising-looking pattern
works: they explicitly check all coefficients, count the `k` selected
positions, and recompute the correlation for every shift.

## How to read an entry name

An entry such as

```text
SDS(32,20,4,[2,16])
```

asks for a signed difference set with:

- `v = 32` total group positions;
- `k = 20` nonzero coefficients;
- `lambda = 4` correlation at every nonidentity shift; and
- group `C2 x C16`, written `[2,16]` using invariant factors.

The group description matters. For example, `[32]` is one cycle of length 32,
whereas `[2,16]` is a product of two cycles. Two groups can have the same
number of elements and the same `(v,k,lambda)` parameters but different
existence answers.

## What does “resolved” mean here?

Each database entry receives one of two answers:

- **EXIST:** an explicit coefficient vector is provided and two independently
  implemented validators confirm every required correlation;
- **NONEXISTENT:** a complete exhaustive argument or a formal solver proof
  rules out every possible coefficient vector.

A failed search is not treated as a proof of nonexistence. Timeouts, heuristic
search misses, and unchecked solver answers are preserved as experimental
records but excluded from the final census.

## Result

This workspace resolves all 68 entries of group order at most 36 marked
`Open` in La Jolla Signed Difference Set Repository commit
`e3bf810c5ee6826cf5030f983f6adf23b0ffd20e`.

Final outcome: **16 EXIST and 52 NONEXISTENT; 0 unresolved**. The canonical
68-row machine-readable result is
[`artifacts/census/current_census.json`](artifacts/census/current_census.json)
(SHA-256
`11cd6bed9b7dcc1c23c66257f0765f2827c8aaefaf944ae4977bf6073cf08d9f`).
The human-readable synthesis is [`FINAL_REPORT.md`](FINAL_REPORT.md).

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

The complete clean-environment DRAT rerun is recorded in
[`artifacts/audit/drat_clean_environment_2026-08-12.json`](artifacts/audit/drat_clean_environment_2026-08-12.json)
with its unabridged journal beside it. A freshly compiled checker verified all
57 proof pairs in a pinned Debian container.

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

## Licensing, citation, and AI disclosure

Project software is available under the MIT License. The paper,
project-authored documentation, and project-authored research data are CC BY
4.0; third-party material retains its original license. See [`LICENSE`](LICENSE)
and [`CITATION.cff`](CITATION.cff).

OpenAI Codex was used extensively for computational research, software
engineering, artifact organization, and drafting. No model output was accepted
as mathematical evidence. The precise scope and verification boundary are
recorded in [`AI_USE.md`](AI_USE.md).
