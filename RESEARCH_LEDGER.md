# Certified Census of Small Signed Difference Sets — Research Ledger

Canonical baseline: La Jolla Signed Difference Set Repository commit
`e3bf810c5ee6826cf5030f983f6adf23b0ffd20e` (frozen April 24, 2026).

## 2026-08-12 — Frozen snapshot, validators, and order-9 exhaustion

- **Target entry:** `SDS(9,8,1,[3,3])`; supporting baselines
  `SDS(5,4,-1,[5])`, `SDS(9,8,-1,[3,3])`, and the repository-negative
  `SDS(9,8,1,[9])`.
- **Hypothesis / truth test:** Exhaust every coefficient vector permitted by
  the support and trivial-character equations. Independently audit the
  global-sign quotient by enumerating both signs without that quotient.
- **Frozen target reconstruction:** all 70,543 JSON keys parse; exactly 68
  records have status `Open` and order at most 36, matching the prespecified
  count. Exactly six have order at most 24.
- **Group convention:** the repository parser reads the bracketed list and
  passes it to Sage `AdditiveAbelianGroup`; `[3,3]` is therefore
  `C_3 x C_3`, with componentwise addition.
- **Configuration / provenance:** macOS 26.3 arm64; Apple Python 3.9.6; Git
  2.51.0; deterministic enumeration, no seed; no paid compute. Full source
  provenance is in `artifacts/snapshot/snapshot_manifest.json`.
- **Search accounting:** the unreduced support-8 domain has
  `9*2^8 = 2304` vectors. The trivial character forces
  `(sum a_g)^2 = 8 + 1*(9-1) = 16`. The sum `+4` side has one zero, six
  positives, and two negatives: `9*C(8,2) = 252`. Global sign bijects it
  with the `-4` side. Method A enumerated all 252 normalized vectors by zero
  and negative-pair positions. Method B traversed all `3^9 = 19683` ternary
  vectors and independently validated all 504 vectors with support 8 and
  absolute sum 4.
- **Observed result:** zero solutions in both `C_3 x C_3` searches.
  Therefore `SDS(9,8,1,[3,3])` is **nonexistent by transparent exhaustive
  enumeration**. The same engines also reproduce zero solutions for the
  frozen repository-negative cyclic case `SDS(9,8,1,[9])`.
- **Independent validation:** the reference validator uses explicit tuples,
  dictionary lookup, and componentwise group operations. The independent
  validator uses integer indices, mixed-radix decoding/ranking, and a
  separately constructed correlation table. Both accept the recorded cyclic
  and noncyclic positive witnesses. Unit tests: 3/3 pass. A second complete
  run reproduced all deterministic payloads.
- **Runtime:** 0.064 s for the open `C_3 x C_3` case and 0.051 s for the
  cyclic negative baseline in the recorded run; 0.23 s wall time for the
  whole command.
- **Artifacts / SHA-256:**
  - `artifacts/snapshot/snapshot_manifest.json` —
    `6ccf82b51f961b75d375d4982645eabb01887af5dc562abf18224779b07880ef`
  - `artifacts/snapshot/targets_open_v36.json` —
    `600df49a002e732d4e1af8d019198afc289e1323497e14f536c4df9c04307aa5`
  - `artifacts/runs/order9_exhaustion.json` —
    `f0b1a06720a512e2e60723d578f773842e65c78a8e0bea032970c81d3279a63e`
  - `scripts/run_order9_exhaustion.py` —
    `2445b532425a317c7ca633b0c5c7ee90e51ddfc55b5a58e4ef6825d659f8e4f7`
  - `src/sds/validator_reference.py` —
    `dacc4ec1e46da7fa35fb90b1b72ab7859c108f5d75447e6a7c3c1b82134b5acc`
  - `src/sds/validator_independent.py` —
    `3ce4c075b58fb539b57506e9ac1091ed27387fdcb98a3b938aadb7bcde263bdb`
- **Novelty/adversarial status:** mathematical result is valid; exact-phrase,
  alternate-notation, repository history/branch/issue/fork, foundational
  paper, and follow-up-paper screens found no earlier exact resolution.
  This supports novelty but does not prove absence of prior art. Details are
  in `artifacts/research/viability_and_order9_novelty.json`.
- **Strongest skeptical objection:** the 252-vector search might omit the
  negative augmentation sign. Decisive test: Method B enumerated all 504
  vectors with both signs and again found none.
- **Failure classification:** none for the pilot. No solver or unproved
  symmetry assumption was used.
- **Decision / reason:** accept the order-9 entry at contribution level 4
  (valid exhaustive result with novelty support), pending third-party
  replication for level 5.
- **Exact next experiment:** exhaust `SDS(20,17,8,[2,10])`, the cheapest of
  the remaining five order-at-most-24 entries by the same character count:
  155,040 normalized / 310,080 unquotiented assignments. Preserve both search
  paths and run both final validators on any witness.

### Reproduction commands

```sh
python3 scripts/build_snapshot.py
python3 -m unittest discover -s tests -v
python3 scripts/run_order9_exhaustion.py \
  --output artifacts/runs/order9_exhaustion.json
shasum -a 256 artifacts/snapshot/*.json artifacts/runs/order9_exhaustion.json
```

## 2026-08-12 — Exact exhaustion of `SDS(20,17,8,[2,10])`

- **Target entry:** `SDS(20,17,8,[2,10])` over `C_2 x C_10`.
- **Hypothesis / truth test:** trivial-character reduction followed by two
  exhaustive searches with different enumeration order and correlation
  representation.
- **Completeness accounting:** unreduced support domain
  `C(20,17)*2^17 = 149,422,080`. The augmentation equation forces coefficient
  sum `+13` or `-13`. On the positive side there are three zeros and two
  negatives, hence `C(20,3)*C(17,2) = 155,040` vectors. Global sign covers the
  other side.
- **Method A:** tuple-group weighted-defect search from the all-ones vector;
  checked all 155,040 normalized assignments in 2.665 s. With defects of
  weights 1 (zeros) and 2 (negatives), `C_a(h)=20-14+C_b(h)`, so every
  nonidentity defect correlation had to equal 2.
- **Method B:** independent mixed-radix subtraction table, reverse nesting
  (negative pair before zero triple), and direct full autocorrelation; checked
  all 155,040 positive-sum and all 155,040 negative-sum vectors in 1.703 s.
- **Observed result:** zero solutions in both paths. Therefore the exact named
  entry is **nonexistent by transparent exhaustive enumeration**.
- **Validation status:** valid result (contribution level 4 after exact-phrase
  and alternate-notation searches returned no prior resolution). A second
  complete run reproduced every deterministic field.
- **Artifacts / SHA-256:**
  - `artifacts/runs/v20_17_8_c2xc10_exhaustion.json` —
    `ca398c2a61f6cedb07595b333c19d4eb02b2e25428de455683446c80123dca83`
  - `scripts/run_v20_17_8_exhaustion.py` —
    `57889ff80aac371b61e5f830b3591ea2ef3c62c76aa1b412a15fe61c99f4a074`
- **Strongest skeptical objection:** the defect algebra could mask an indexing
  error. The decisive test was Method B's direct, unquotiented autocorrelation
  check of all 310,080 vectors; it does not use the defect identity.
- **Failure classification:** none. No solver, timeout, or unproved group
  automorphism was used.
- **Decision / reason:** accept nonexistence for the frozen entry.
- **Exact next experiment:** exhaust `SDS(18,15,2,[3,6])`; 1,113,840
  normalized and 2,227,680 unquotiented assignments after the same mandatory
  augmentation constraint.

## 2026-08-12 — Exact exhaustion of `SDS(18,15,2,[3,6])`

- **Target entry:** `SDS(18,15,2,[3,6])` over `C_3 x C_6`.
- **Completeness accounting:** the support-15 domain has 26,738,688 vectors.
  The augmentation equation forces sum `+7` or `-7`. The positive side has
  three zeros and four negatives, giving `C(18,3)*C(15,4) = 1,113,840`.
- **Method A:** a precomputed tuple-group difference table and weighted-defect
  enumeration checked every normalized vector in 5.498 s. The exact defect
  condition was `C_b(h)=6` at every nonidentity element.
- **Method B:** a separately built mixed-radix subtraction table and reverse
  enumeration order directly checked all 2,227,680 vectors of both
  augmentation signs in 8.508 s.
- **Observed result:** zero solutions in both paths. Therefore the exact entry
  is **nonexistent by transparent exhaustive enumeration**.
- **Validation / reproducibility:** a second full run reproduced every
  deterministic field. Exact-phrase and alternate-notation searches found no
  prior resolution; this is novelty support, not proof of novelty.
- **Artifacts / SHA-256:**
  - `artifacts/runs/v18_15_2_c3xc6_exhaustion.json` —
    `649a411c9a893b3b0d4fe58ce8da6a533b7481626aeb807d4abe7e3fbb61744a`
  - `scripts/run_v18_15_2_exhaustion.py` —
    `1849a4ea39cdf5c6a916712b43948a493d1f447dbfde07bb98c9f6903c2356a0`
- **Strongest skeptical objection:** the weighted-defect transform could be
  implemented incorrectly. Method B does not use it and directly recomputes
  the defining correlation for both signs.
- **Failure classification:** none; no timeout, solver, or unproved group
  automorphism.
- **Decision / reason:** accept nonexistence for the frozen named entry.
- **Exact next experiment:** build the evolving 68-row census, then attack
  `SDS(20,11,2,[2,10])`. Its character-reduced 9,237,800 normalized vectors
  make it the next cheapest remaining order-at-most-24 case; add reusable
  Fourier/orbit filters before full traversal.
