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

## 2026-08-12 — Translation-reduced and full exhaustion of `SDS(20,11,2,[2,10])`

- **Target entry:** `SDS(20,11,2,[2,10])` over `C_2 x C_10`.
- **Completeness accounting:** the 343,982,080-vector support domain reduces
  by the mandatory augmentation sum `+7` to 9,237,800 normalized vectors
  (nine positive, two negative, nine zero). Translation preserves the full
  equation, and translating either negative element to the identity yields a
  representative among `19*C(18,9) = 923,780`; duplicates are harmless.
- **Method A:** explicit tuple-group autocorrelation with one negative fixed at
  identity; all 923,780 representatives checked in 5.655 s.
- **Method B:** independent `C_2 x C_10` two-row bitset rotation, with no
  translation restriction; all 9,237,800 normalized assignments checked in
  20.001 s.
- **Observed result:** both complete searches found zero solutions. Global sign
  bijects the omitted sum `-7` half. Therefore the exact named entry is
  **nonexistent by transparent exhaustive enumeration**.
- **Reproducibility:** a second full run reproduced every deterministic field.
  Exact-phrase and alternate-notation web searches found no prior resolution;
  this is novelty support only.
- **Failed run:** the first full-audit attempt stopped on Python 3.9 lacking
  `int.bit_count`; it produced no evidence. A fixed 10-bit lookup popcount was
  installed and both methods were rerun from the beginning.
- **Artifacts / SHA-256:**
  - `artifacts/runs/v20_11_2_c2xc10_search.json` —
    `74d3833e8dba74049d4d376fab8f267e03a7dff31a9085fb87c06938114a3bcd`
  - `scripts/run_v20_11_2_search.py` —
    `552bc2b83456af13913ac96321479a824d191b4b81738b4e5afed32ddd72fa5d`
- **Strongest skeptical objection:** fixing a negative at identity might miss a
  translation class. The direct full search, with no translation fixing,
  independently checked all 9,237,800 normalized vectors and found none.
- **Failure classification:** one environment-compatibility error, corrected;
  no mathematical or evidence-boundary failure.
- **Decision / reason:** accept nonexistence for the frozen entry.
- **Exact next experiment:** run deterministic and seeded construction search
  on both remaining order-24 entries before selecting a proof encoding. Their
  character-reduced exhaustive spaces are 1,153,218,528 each, so raw traversal
  is not the cheapest first truth test.

## 2026-08-12 — Order-24 method pivot and exact CNF validation

- **Targets:** `SDS(24,18,2,[2,12])` and `SDS(24,18,2,[2,2,6])`.
- **Heuristic signal:** 32 deterministic annealing restarts of 5,000
  fixed-composition swaps per group found no construction. Best squared
  correlation residuals were 12 for `C_2 x C_12` and 30 for
  `C_2 x C_2 x C_6`. This is explicitly **not** nonexistence evidence.
  Artifact `artifacts/runs/v24_local_search.json`, SHA-256
  `ccf3c638df3719bf665a068f05eb7da0f7a8ac081f4f9b70383b5285ce6da9e4`.
- **CNF encoding:** exclusive positive/negative variables; exact positive and
  negative counts; full-equivalence Tseitin variables for every signed product;
  exact cardinality form
  `sum(same-sign)+sum(not cross-sign)=lambda+2v` for every nonidentity shift;
  global sign normalized; a negative at identity fixed by proved translation
  invariance.
- **Encoding cross-check:** sequential-counter and totalizer encodings both
  reproduce SAT for recorded positives `SDS(5,4,-1,[5])` and
  `SDS(9,8,-1,[3,3])`, and UNSAT for the independently exhausted cyclic and
  noncyclic order-9 negatives. All SAT models pass both external validators;
  all emitted DIMACS files parse independently. Artifact
  `artifacts/runs/sat_baselines.json`, SHA-256
  `6c97044021ab557bc2d81343b6a2c4e6984df282def025772c1ad58d97451d11`.
- **Failures affecting allocation:** optional `pypblib` installation failed
  because C++ standard-library headers were unavailable; the unweighted
  reformulation made it unnecessary. Two unpartitioned CaDiCaL order-24 runs
  terminated without artifacts. Bounded Glucose4 runs reached 100,000
  conflicts without a decision (29.0 s sequential, 12.1 s totalizer). The
  first DIMACS writer omitted `c` prefixes on comments; those malformed files
  were discarded and every formula regenerated and parsed. Default backward
  DRAT checking exceeded memory; forward mode (`drat-trim -f`) verified the
  same proofs at lower memory.
- **Decision:** retain totalizer + Glucose4 + forward DRAT checking, strengthened
  by exhaustive real-character subcases. Do not accept any raw UNSAT.

## 2026-08-12 — Walsh nonexistence proof for `SDS(24,18,2,[2,2,6])`

- **Target entry:** exact group `C_2 x C_2 x C_6`.
- **Reduction:** the real-character quotient is `G/2G = C_2^3`, with eight
  cosets of size three. The principal character is normalized to `+8`; all
  seven nonprincipal real characters must be `+4` or `-4` because
  `|chi(D)|^2=k-lambda=16`.
- **Method A:** exhausted all `2^7=128` spectra and inverse-Walsh transformed
  them. None even has integral cell sums (each numerator is `4 mod 8`), hence
  none can describe coefficients aggregated over group cosets.
- **Method B:** independently exhausted all `7^8=5,764,801` integer cell-sum
  tuples in `[-3,3]^8`; 154,645 have principal sum 8, and none has all seven
  nonprincipal Walsh magnitudes 4.
- **Observed result:** **nonexistent by an exhaustive character obstruction**.
  No SAT solver or symmetry quotient is needed for this entry. A repeat run
  reproduced all deterministic fields.
- **Artifact / SHA-256:** `artifacts/runs/v24_18_2_c2c2c6_walsh_proof.json` —
  `60d39d359a0213fa7dd447cedc25fb16683485890513e9a5bb0f5d97c1e6aad2`;
  proof script —
  `a86bc152de86b148f7813dcca5ab20d79bd9a5d2fb03c3847f2362b626b8f439`.
- **Novelty/adversarial status:** exact-parameter and alternate group-notation
  searches found no prior resolution; novelty-supported, not proven novel.
- **Strongest skeptical objection:** inverse-transform indexing could be wrong.
  Method B transforms in the opposite direction over all bounded integer cell
  sums and reaches the same empty feasible set.
- **Decision:** accept the frozen named entry as resolved.

## 2026-08-12 — Checked SAT nonexistence proof for `SDS(24,18,2,[2,12])`

- **Target entry:** exact group `C_2 x C_12`.
- **Complete Fourier split:** `G/2G = C_2^2`. Principal character `+8` and
  three independent real-character signs `+/-4` yield exactly eight inverse
  Walsh cell-sum patterns: four permutations of `(-1,3,3,3)` and four of
  `(5,1,1,1)`.
- **Exact solver evidence:** one totalizer CNF per pattern, each containing the
  full coefficient domain, exact composition, full 23 nonidentity
  autocorrelations, translation fix, and exact parity-cell sums. Glucose4
  returned UNSAT for all eight. Solver times were 24.140, 5.539, 6.351, 7.204,
  5.552, 6.079, 6.124, and 0.096 seconds.
- **Independent proof checking:** every ASCII DRAT/DRUP certificate passes
  `drat-trim -f` at source commit
  `2e3b2dc0ecf938addbd779d42877b6ed69d9a985` (the exact commit is also stored
  in every subcase report). Seven proofs are 10–28 MB; the final pattern is
  refuted by propagation and has a one-byte empty-clause proof.
- **Observed result:** **nonexistent by eight checked SAT proofs**. The split is
  exhaustive by direct enumeration of all `2^3` real-character signs.
- **Aggregate artifact / SHA-256:**
  `artifacts/runs/v24_18_2_c2xc12_certified_sat.json` —
  `ef13ffcf111842c540cfc4e67e8746b9adf79e262e3772ff28f16df9620ba905`.
  Formula, proof, checker-output paths and hashes are recorded per subcase in
  `artifacts/sat/v24_c2c12_subcases/` (130 MB total).
- **Encoding source hashes:** `src/sds/sat_encoding.py` —
  `c447e4397ad0148e22cf6767cc80546dc860b880a06d4080d59b5532dc5ebbfe`;
  subcase runner —
  `3f41c843b994b026b4b2cbff3455385785cb416281c5f38ba099922ae14abdcf`;
  aggregate checker —
  `3f44385bf99f89c0d007fbcdb931e455df303b1a5b7444326729e3a3e4ec7a3f`.
- **Novelty/adversarial status:** exact-parameter and alternate group-notation
  searches returned no prior resolution. Strongest objection—an incomplete
  Fourier case split—is defeated by explicitly deriving and certifying all
  eight sign patterns.
- **Decision:** accept the frozen named entry as resolved. All six frozen Open
  entries of order at most 24 are now certified nonexistent.
- **Exact next experiment:** apply the validated SAT/witness pipeline and
  composition-preserving local search to the three `C_5 x C_5` order-25
  targets, prioritizing positive witness discovery before proof generation.

## 2026-08-12 — Complete resolution of all three order-25 targets

- **Existence:** deterministic fixed-composition annealing found
  `SDS(25,12,1,[5,5])` on seed 52 (53 restarts completed). Explicit
  lexicographic vector:
  `[0,0,1,1,1, 0,0,0,0,1, 0,-1,1,-1,0, -1,1,1,1,0, 0,1,0,0,0]`.
  Thus
  `P={(0,2),(0,3),(0,4),(1,4),(2,2),(3,1),(3,2),(3,3),(4,1)}` and
  `N={(2,1),(2,3),(3,0)}` in `C_5 x C_5`. Both validators report support 12,
  coefficient sum 6, and autocorrelation `[12,1,...,1]` at all 25 elements.
- **Witness artifacts:** discovery run
  `artifacts/runs/v25_local_search.json` —
  `ecfe96efe393dfd714014286b6b0463259327f12eb32956a2799d8f3bb98a05f`;
  standalone witness `artifacts/witnesses/sds_25_12_1_c5xc5.json` —
  `1be9efec80639574ddc8b36511ac38b85a47219287e24404cfeac8de287f9d46`.
- **Nonexistence:** for a nonprincipal order-five character, five fiber sums
  `s_j in [-5,5]` must have cyclic autocorrelation fixed by divisibility of
  `sum c_h x^h-n` by `Phi_5`. Full `11^5` enumeration and an independent
  `11^4`-prefix/derived-coordinate enumeration both give no fiber sums for
  `(25,16,2)` or `(25,24,5)`. The valid `(25,12,1)` control has exactly 20
  fiber patterns and includes the new witness's row sums `(3,1,-1,2,1)`.
- **Nonexistence artifact:**
  `artifacts/runs/v25_c5xc5_character_obstructions.json` —
  `eb549fd130542df2bb72409d5e889f2666d33caebef5b8acae2aee485d3d3cbb`;
  script —
  `5707c211d8936918166650b5d2912a070e0d397c2632d8052aeb1d46c036952e`.
- **Failures / pivots:** a script syntax error produced no artifact and was
  fixed before rerun. Glucose4 was interrupted after two minutes and Kissat
  after 90 seconds on the unpartitioned `(25,16,2)` CNF; neither run is
  evidence. The order-five character representation then resolved both cases
  in under one second.
- **Novelty/adversarial screen:** exact parameter/group queries, alternative
  `C_5 x C_5` notation, frozen/upstream repository comparison, and the two
  signed-difference-set papers found no prior exact resolutions. This supports
  novelty only. The strongest objection to the obstruction—an overstrong
  cyclotomic coefficient identity—is answered by the accepted positive
  control and the independently derived enumeration.
- **Decision:** all three order-25 frozen entries are resolved: one existence,
  two nonexistence.

## 2026-08-12 — Order-27 character exclusions and five constructions

- **Six nonexistence results:** every target group `C_3^3` and `C_3 x C_9`
  has an order-three character with three size-nine fibers. The cyclotomic
  correlation condition has no bounded integer fiber-sum triple for parameters
  `(27,12,2)`, `(27,23,1)`, or `(27,23,13)`. Full `19^3` and independent
  derived-coordinate `19^2` enumerations agree. This resolves both named
  groups for each parameter triple. Seven surviving parameter controls each
  have six feasible triples.
- **Character artifact:** `artifacts/runs/v27_order3_character_obstructions.json`
  — `714116e45772cc179718410a8f85a968fda94eeb761bcb4e0eb6cbf5f8a15831`;
  script — `114db72585767ce543affffb4a15c2632ac092661f96ed6984f858d161ff4654`.
- **Five existence results:** the exact-objective local engine found and both
  validators accepted `SDS(27,10,1,[3,3,3])`, `SDS(27,10,1,[3,9])`,
  `SDS(27,14,5,[3,3,3])`, `SDS(27,14,5,[3,9])`, and
  `SDS(27,17,8,[3,3,3])`. The first three appeared in the first restart; the
  `C_3 x C_9` `(27,14,5)` witness appeared in restart 11.
- **Witness provenance:** discovery run
  `artifacts/runs/v27_unresolved_local_search.json` —
  `b95119d79f9b03392741215184adc07452f35a595e4fd6f90efc7de3d3b1a0e7`.
  Standalone witness hashes, in the same order as above, are
  `0e95ade30225bfe8dc64ec360d9913f56003259b528b68f80e698ed1c2511e71`,
  `5bf59924eadfbbaec7717ff5778ef1ee928679eeeb534471559d45af16616d27`,
  `160382a0fd26a75f7c6125751434152b64cc8a3ad9e1e0b3eb143e402d7c28a9`,
  `b0e1e8c828b30613634e6c4bfe711e47f7c376bd72bcfdeadb7c5649ba4ecb76`,
  and `1832ff68cb00c3f5218dd41553106cb07c002c2805191d277be97aa75db903f2`.
- **Order-nine escalation signal:** exhaustive C scan of all `7^9=40,353,607`
  possible size-three fiber sums for each unresolved `C_3 x C_9` parameter
  leaves 36–450 cyclotomic survivors; it is useful pruning but resolves no
  entry. Kernel runtime 1.51 s; source
  `experiments/v27_order9_fiber_scan.c`.
- **Novelty/adversarial screen:** exact names, grouped parameter searches,
  alternate group notation, repository history, and relevant papers produced
  no prior exact match. Each witness is checked in full coordinates, so the
  most direct skeptical objection—confusing `C_3^3`, `C_3 x C_9`, and `C_27`—
  is excluded.
- **Remaining order-27:** ten entries remain (including the cyclic cases); none is
  classified from residuals or timeouts.

## 2026-08-12 — General real-character theorem (12 new resolutions)

- **Theorem:** any even invariant factor supplies the integer-valued
  nonprincipal character `chi(x)=(-1)^x`. Applying it to the defining equation
  forces the integer square `chi(D)^2=k-lambda`. A nonsquare `k-lambda` proves
  nonexistence for the exact named group.
- **Derived scope:** 13 frozen targets fail, including the already exhausted
  order-18 case. The theorem newly resolves two order-28 entries with
  `k-lambda=8`, all seven `(32,19,2)` groups with `k-lambda=17`, and all three
  `(36,30,2)` groups with `k-lambda=28`.
- **Artifact:** `artifacts/runs/real_character_square_obstructions.json` —
  `1aaac87ac8ed488894ccdedbffdb782bb8b680b0c299770b9fa03dc355965537`;
  script — `7c78b62c3c7f71f0cfdbca867a070389dea893d81188b6b68a3e95bd21452ea3`.
  Repeated derivation reproduces the exact 13-name list.
- **Novelty screen:** exact order-28, order-32, and order-36 parameter/group
  queries returned no prior exact resolutions. The argument itself is a direct
  character consequence, independent of solver behavior.

## 2026-08-12 — Portfolio construction sweep through orders 28, 32, and 36

- **Order 28:** 32x4,000-step deterministic restarts found no construction for
  the three surviving cases (best residuals 8, 8, and 64). Signal only.
- **Order 32:** five new validated constructions:
  `SDS(32,20,4,[2,2,2,2,2])`, `SDS(32,20,4,[2,2,2,4])`,
  `SDS(32,20,4,[2,2,8])`, `SDS(32,20,4,[2,4,4])`, and
  `SDS(32,28,12,[2,4,4])`. Discovery run
  `artifacts/runs/v32_unresolved_local_search.json` —
  `bd2066ba728127e6b8ca725f0618f12a6e658fb4e166dcf194830e18211b3024`.
  Standalone witness hashes are respectively
  `7b4fdd2a34ca1e61376a53169e7475bccecd69aa909d967b5d44011e4eabd101`,
  `d099f73f04a3233d8802183e714edfa3cbdc396c252f02dd3dc45dba99910334`,
  `7b6c903b5b6c7c788615ec9a3ea2b67eb8ff41e538e23085c97b842219144799`,
  `b6b9de3b1bd7f821e1d79ffcd03fc92e9931f245429825d1f01e53342e896dc1`,
  and `c99d1a823145ccbdc68216dc2149b2f96711a5a6564b76de4ecf8251946bd113`.
- **Order 36:** new validated construction `SDS(36,11,2,[6,6])` with
  `P={(0,0),(0,1),(0,3),(1,1),(2,4),(3,3),(4,1),(4,2),(4,3),(5,5)}` and
  `N={(2,5)}`. Discovery run
  `artifacts/runs/v36_unresolved_local_search.json` —
  `206898b65b41eb8c1aa435e17ec4938ed3092270082a354764ff6b0c2afa6e6c`;
  witness — `24c261a45c89c45d3b813436d025f43b81c3beb07fd80b7c51c6bfcac6904cce`.
- **Validation:** every listed construction has separate tuple/dictionary and
  mixed-radix validator reports with full unsymmetrized autocorrelation.
- **Novelty screen:** exact-name searches for all six new order-32/order-36
  witnesses returned no results; upstream remains at the frozen commit. This
  supports novelty, not universal absence of prior art.
- **Current decision:** census stands at 38 resolved / 30 unresolved. Change
  representation for remaining cases; do not spend another identical local
  batch without adding character partitions, exact SAT, or a new operator.
- **Exact next experiment:** derive and inject complete real-character Walsh
  cell patterns for the remaining even-order groups, then benchmark SAT on one
  near-miss from each of orders 28, 32, and 36. In parallel, use the order-nine
  fiber survivors to partition the unresolved `C_3 x C_9` cases.

## 2026-08-12 — Certified SAT and quotient escalation (38 → 57 resolved)

- **Order 28:** complete Walsh-pattern splitting produced 12 exact CNFs for
  the remaining three `C_2 x C_14` entries. All traces passed forward DRAT
  checking. Aggregate `artifacts/runs/v28_certified_sat.json` —
  `b9af8d377839153863ace8d55a83ea728c86761630c43dd6dd2dd3f5a3aa9169`
  at generation time (the census records the final file hash).
- **Additional constructions:** exact SAT found and both validators accepted
  `SDS(32,20,4,[4,8])`, `SDS(32,28,12,[4,8])`, and
  `SDS(36,11,2,[3,12])`. Standalone witness hashes are respectively
  `d22db64868c4632dde42cf06c2f8ad4f36378cec7a8b62f77fa39f022f362540`,
  `b3d6206389fd754c1e796f57bcc29652fbeec87ceb4a47e47281fad60adaf72b`,
  and `6026d2446cd20368ab91bb2b8c3dad327fe374b639f74a77230680586598f268`.
- **Order 27 SAT:** 24 symmetry-complete exact subcases resolved cyclic
  `(17,8)` and all three `(25,16)` entries as nonexistent. Aggregate
  `artifacts/runs/v27_certified_sat.json` —
  `5a98b9a9b38b9adc6ea5c0bf5508576a2beb698a077a492d6c5c540b50eb4ad3`.
- **Order 32 dense character exhaustions:** full-rank Walsh enumeration
  resolved `(28,12,[2,2,2,4])`; rank-three enumeration checked 2,207,744
  vectors and resolved `(28,12,[2,2,8])`. The latter was rerun; all
  deterministic fields agreed (timestamps/runtimes excluded).
- **Order 36 `(29,20)`:** combined parity and order-three quotients reduce
  `C_3 x C_12` to two normalized orbits, `C_2 x C_18` to two, and `C_6^2`
  to four. All eight traces independently verify. Aggregates:
  `v36_29_20_c3x12_certified_sat.json` —
  `4586bd67a05e966c9b2dd83d2510f68d7caf4dd0fd7a3444cb6080c97b8af024`;
  `v36_29_20_even_certified_sat.json` —
  `be5aa592b54ee2e5946568ecbc578a4e256b2b404c78e104e787791a7043be83`.
- **Order 36 `(29,4)`:** exhaustive combined quotients have 144 and 420
  bounded survivors before full quotient autocorrelation, respectively, for
  `C_2 x C_18` and `C_3 x C_12`; both leave zero solutions and pass a separate
  mixed-radix verifier. `C_6^2` has one affine `C_3^2` quotient orbit and its
  exact CNF has a checked 23.4 MB DRAT trace. Artifacts:
  `v36_29_4_combined_quotient_exhaustion.json` —
  `416ca62582a54b9d3b398436b36ccfbd239db1c48b113ed385329110c98b99e5`;
  `v36_29_4_c6x6_certified_sat.json` —
  `013e11fd7bb8e7312d1e9d594d58d569a023b17915b4a4af146c779ef6485c98`.
- **Failure classification:** raw rank-one SAT attempts that reached conflict
  caps remained `NO_DECISION`. Adding independent quotient marginals changed
  the representation and converted five v=36 instances into small checked
  branches. No raw `UNSAT` was promoted.

## 2026-08-12 — Complete order-27 quotient classification (57 → 63 resolved)

- **Projection:** quotienting either group through a kernel of order three
  produces a `C_3^2` cell-sum vector with identity correlation `k+2lambda`
  and nonidentity correlation `3lambda`.
- **Results:** `(22,9)` has no quotient vector. Each of `(17,4)` and `(22,3)`
  has 144 quotient vectors: one `AGL(2,3)` orbit for `C_3^3`, or 16 complete
  translation orbits for `C_3 x C_9`. Exact refinement of all representatives
  checked 6,246,072 ternary assignments and found zero full solutions.
- **Evidence:** `artifacts/runs/v27_remaining_quotient_exhaustion.json` —
  `442c3d80c64a9481615037f8134dfb5e3d45db121ace7b9f405be082403b8b55`.
  `scripts/verify_v27_remaining_quotients.py` independently rebuilds the
  quotient vectors by multiset composition, reconstructs every orbit cover,
  uses separate mixed-radix correlation, and repeated all refinements: six
  PASS results.
- **Decision:** all six remaining v=27 entries are certified nonexistent.

## 2026-08-12 — Complete order-32 frontier (63 → 68 resolved)

- **Cyclic quotient ladder:** exhaustive `C8 → C16 → C32` refinement leaves
  zero full solutions for both `(20,4)` and `(28,12)`. The sparse case checks
  12 normalized-parent C16 survivors and 248,832 final refinements; the dense
  case checks four survivors and 1,024 refinements.
- **Product quotient ladder:** for `SDS(32,28,12,[2,16])`, all eight
  translation-normalized `C_2 x C_4` quotient orbits refine to 38 surviving
  `C_2 x C_8` vectors; all 21,080 final refinements fail.
- **Elementary group:** writing `f=1-1_Z-2*1_N` forces four zeros and four
  negatives. `AGL(5,2)` has exactly two four-point-set types (affine plane or
  affine-independent). Each representative has 20,475 disjoint negative
  supports; Walsh checking leaves zero solutions.
- **Construction:** a quotient refinement produced
  `SDS(32,20,4,[2,16])`; both validators accept it. Witness
  `artifacts/witnesses/sds_32_20_4_2_16.json` —
  `4ac02b48513f14385bffd574a2b531d46223375baf7cdc3e398be7f70a433eff`.
- **Symmetry bug caught before acceptance:** an intermediate implementation
  attempted to quotient a normalized-parent second-stage solution set by the
  full translation group. The assertion that the orbit remained in that
  slice failed. The extra quotient was removed; every second-stage survivor
  is now refined explicitly. This increased work while restoring a direct
  coverage proof.
- **Evidence:** `artifacts/runs/v32_remaining_quotient_exhaustion.json` —
  `2870150476387abadaf39792d254455a85cd2321a85011c6b2719a756001b1ab`.
  `scripts/verify_v32_remaining_quotients.py` uses multiset enumeration,
  separate mixed-radix autocorrelation, explicit orbit reconstruction, and
  repeats every final refinement: four PASS results.

## 2026-08-12 — Final audit and corrected novelty classification

- **Census:** `artifacts/census/current_census.json` —
  `11cd6bed9b7dcc1c23c66257f0765f2827c8aaefaf944ae4977bf6073cf08d9f`;
  68/68 resolved, 16 EXIST, 52 NONEXISTENT.
- **Integrity:** all 68 evidence hashes match; all 16 standalone witnesses
  pass both validators; 57 CNF/proof/checker subcases have intact hashes and
  checker outputs containing `s VERIFIED`; validator tests pass 3/3.
- **Late prior-art discovery:** global GitHub code search found
  `farev/Matematica`, with exact SDS results first committed on 2026-08-09.
  Its exhaustive decisions plus character closure table cover 58 target
  entries. Entry-by-entry comparison has zero disagreements (10 existence,
  48 nonexistence). These 58 are therefore independent replications, not
  novelty claims.
- **Novelty-supported remainder:** the prior project does not resolve the
  seven `(32,20,4)` entries or the three `(36,29,4)` entries. Exact parameter,
  alternate group notation, global GitHub code, unchanged upstream
  branch/issues, arXiv-source, and citation-index screens found no earlier
  exact resolution. Six are constructions and four are certified negatives.
  This supports novelty but cannot prove universal absence of prior work.
- **Artifact:** `artifacts/novelty/novelty_screen_2026-08-12.json` —
  `15b30ebad2a53005a914eb7640f766aee455d6bea30e9ced2a174de785615745`.
- **Resources:** local CPU only; paid-compute cost €0. Accepted artifacts use
  approximately 1.1 GB, chiefly DRAT traces. No outreach, push, publication,
  or external mutation occurred.
- **Terminal decision:** the primary objective is complete under the frozen
  68-entry counting convention and evidence boundary.
