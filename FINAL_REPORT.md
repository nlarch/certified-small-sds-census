# Final Decision Report — Certified Census of Small Signed Difference Sets

Date: 2026-08-12  
Frozen baseline: La Jolla repository commit
`e3bf810c5ee6826cf5030f983f6adf23b0ffd20e`  
Scope: every entry marked `Open` with group order `v <= 36`

## Decision

The frozen target contains exactly 68 named entries. Every entry is resolved:

| Order | Targets | EXIST | NONEXISTENT |
|---:|---:|---:|---:|
| 9 | 1 | 0 | 1 |
| 18 | 1 | 0 | 1 |
| 20 | 2 | 0 | 2 |
| 24 | 2 | 0 | 2 |
| 25 | 3 | 1 | 2 |
| 27 | 21 | 5 | 16 |
| 28 | 5 | 0 | 5 |
| 32 | 21 | 8 | 13 |
| 36 | 12 | 2 | 10 |
| **Total** | **68** | **16** | **52** |

The exact entry-level decisions, evidence paths, schemas, and hashes are in
`artifacts/census/current_census.json`. No timeout, search miss, or unchecked
solver answer is counted.

## Evidence composition

| Accepted result type | Entries |
|---|---:|
| Explicit construction, two full validators | 16 |
| Checked SAT/DRAT proofs | 13 |
| Direct exhaustive enumeration | 4 |
| Exhaustive character obstruction | 9 |
| Exhaustive quotient/character reduction | 14 |
| Real-character square obstruction | 12 |

The 13 SAT-based decisions comprise 57 complete CNF/DRAT subcases. Each
subcase records formula, proof, checker output, tool commit, and SHA-256
hashes. The fast audit confirms that every referenced file is intact and that
every checker output contains `s VERIFIED`.

All 16 existence results are also frozen as standalone witness files. Both
validators recompute the support, coefficient sum, and all `v`
autocorrelations in full unsymmetrized coordinates.

## Ten novelty-supported decisions

The external screen found no earlier exact resolution for these entries:

| Entry | Decision |
|---|---|
| `SDS(32,20,4,[2,16])` | EXIST |
| `SDS(32,20,4,[2,2,2,2,2])` | EXIST |
| `SDS(32,20,4,[2,2,2,4])` | EXIST |
| `SDS(32,20,4,[2,2,8])` | EXIST |
| `SDS(32,20,4,[2,4,4])` | EXIST |
| `SDS(32,20,4,[4,8])` | EXIST |
| `SDS(32,20,4,[32])` | NONEXISTENT |
| `SDS(36,29,4,[2,18])` | NONEXISTENT |
| `SDS(36,29,4,[3,12])` | NONEXISTENT |
| `SDS(36,29,4,[6,6])` | NONEXISTENT |

For the six positive entries, the decisive adversarial check is the explicit
full-coordinate vector accepted by two independent validators. For cyclic
`SDS(32,20,4,[32])`, the independent verifier reconstructs the complete
`C8 -> C16 -> C32` quotient ladder and all final refinements. For the three
order-36 negatives, two are independently exhausted in combined quotients;
the `C6 x C6` case additionally has a checked DRAT proof for its unique
normalized quotient orbit.

## Prior exact work and independent replication

The novelty screen discovered the public `farev/Matematica` project after the
computational census had been completed. Its relevant results first appeared
in commits dated 2026-08-09, three days before this report. Combining its
exhaustive `values.csv` decisions and character-theory closure table covers
58 of the 68 frozen entries. There are zero decision disagreements:

- 10 independently agreeing existence decisions;
- 48 independently agreeing nonexistence decisions.

Accordingly, these 58 are reported as independent replications, not as novel
discoveries. The remaining ten are only *novelty-supported*: exact web and
GitHub searches, the unchanged upstream branches/issues, the foundational
paper, the He–Chen–Ge follow-up source, and citation-index checks found no
earlier exact resolution. This is evidence, not proof, of novelty.

## Reproducibility and integrity

Canonical hashes:

- Census: `11cd6bed9b7dcc1c23c66257f0765f2827c8aaefaf944ae4977bf6073cf08d9f`
- Novelty screen: `15b30ebad2a53005a914eb7640f766aee455d6bea30e9ced2a174de785615745`
- Final v=27 quotient exhaustion: `442c3d80c64a9481615037f8134dfb5e3d45db121ace7b9f405be082403b8b55`
- Final v=32 quotient exhaustion: `2870150476387abadaf39792d254455a85cd2321a85011c6b2719a756001b1ab`
- Combined v=36 quotient exhaustion: `416ca62582a54b9d3b398436b36ccfbd239db1c48b113ed385329110c98b99e5`

Run:

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/audit_final_census.py
python3 scripts/verify_v27_remaining_quotients.py
python3 scripts/verify_v32_remaining_quotients.py
python3 scripts/verify_v36_29_4_combined_quotients.py
```

The accepted evidence occupies about 1.1 GB, chiefly proof traces. All
compute was local; paid-compute cost was zero. No public push, publication,
maintainer contact, or expert outreach was performed.

## Scope limits

This is a complete classification only for the 68 entries that were `Open`
in the named frozen commit and satisfy `v <= 36`. It is not a classification
of all signed difference sets, all groups of those orders, later database
states, or equivalence classes beyond the exact named entries.
