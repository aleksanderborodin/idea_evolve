# Pre-Concatenated Knowledge Dump


## All Ideas


### [active] fact_001

---
id: fact_001
type: fact
name: "Greedy Baseline Score"
confidence: 1.0
first_seen: generation_0
last_confirmed_gen: 6
verified: true
source: user-provided, confirmed by dozens of solutions across all generations
tags: [baseline, greedy]
---

The simple greedy algorithm (add smallest valid element) produces a Sidon set
of size 66 for N=10000. This is the starting baseline.

**Gen 6 confirmation**: DFS/backtracking (idea_005) proved sequential DFS IS greedy,
producing the identical 66-element set. Verified independently across all 6 generations.

**Gen 6 consistency fix**: confidence upgraded to 1.0, verified set to true.


### [active] fact_002

---
id: fact_002
type: fact
name: "Theoretical Upper Bound"
confidence: 0.95
first_seen: generation_0
last_confirmed_gen: 6
verified: true
source: Carter-Hunter-O'Bryant, confirmed by research agents gen 2-6
tags: [upper-bound, theory]
---

For a Sidon set (B2 sequence) in {0, ..., N}, the maximum size is at most
sqrt(N) + O(N^{1/4}). For N=10000, this gives an upper bound of approximately
**109 elements** (not ~100-102 as originally stated).

**Correction history:** Original fact said "~100-102" which was incorrect. The
sqrt(10000) = 100 term is only the leading order; the O(N^{1/4}) ~ 10 term
pushes the bound to ~109. Corrected in gen 2 consistency review.

**NOTE**: This file replaces the STALE version in facts/fact_002.md which still
says "~100-102". The facts/ version must be overwritten with this corrected content.


### [active] fact_004

---
id: fact_004
type: fact
name: "Violation Policy — Sentinel Scoring"
confidence: 1.0
first_seen: generation_0
last_confirmed_gen: 6
verified: true
source: evaluate.py + validate.py source code, metrics.yaml sentinel_value
tags: [scoring, validation, sentinel]
---

If a solution has ANY violations (repeated pairwise sums), the fitness score is
set to **0** (sentinel value from metrics.yaml). There is NO partial credit, NO
subset extraction, and NO tolerance for near-valid solutions. Only fully valid
Sidon sets receive a real fitness score equal to the set size.

**Correction history:** Original fact incorrectly stated "the validator extracts
the largest valid Sidon subset using a greedy algorithm." This was WRONG. The
system uses strict sentinel scoring as defined in metrics.yaml. Corrected in
gen 2 consistency review.

**NOTE**: This file replaces the STALE version in facts/fact_004.md which still
contains the incorrect subset extraction claim. The facts/ version must be
overwritten with this corrected content.


### [active] idea_011

---
id: idea_011
type: idea
name: "Erdos-Turan Extension with Local Search"
lifecycle: active
confidence: 0.35
first_seen: generation_2
last_updated: generation_6
last_confirmed_gen: 6
cluster: cluster_002
supported_by: [gen002_explore_1_sol03, gen002_explore_1_sol04, gen006_explore_1_sol02, gen006_explore_1_sol03, gen006_explore_1_sol04]
contradicted_by: []
related_ideas: [idea_009, idea_002, idea_022]
tags: [erdos-turan, local-search, extension, non-algebraic]
---

Combines Erdos-Turan construction (p=71) with greedy extension and 1-opt local search.
Best result: 75 elements (gen 2, confirmed gen 6).

**Gen 6 results (explore_1):**
- ET(71) + 1-opt + 2-opt + LNS: 75 (sol02)
- ET(71) + aggressive LNS (k=2-15): 75 (sol03)
- Randomized greedy + 1-opt restarts: 75 (sol04)
- 30+ restarts across all three solutions, all converge to exactly 75

The 75 ceiling is extremely robust. LNS with up to 15-element perturbations, 2-opt,
and diverse initial constructions all converge to the same local optimum. This is now
confirmed as a hard structural ceiling, not just a weak local minimum.

**Confidence reduced to 0.35** — superseded by algebraic constructions (105) with a
30-element gap. No further investment recommended unless combined with fundamentally
new ideas (e.g., SA from 75-element seed with longer time budget, or C implementation
for 2-opt).


### [active] idea_019

---
id: idea_019
type: idea
name: "CP-SAT / ILP Constraint Programming"
lifecycle: active
confidence: 0.4
first_seen: generation_4
last_updated: generation_6
last_confirmed_gen: 6
cluster: cluster_004
supported_by: [gen004_full_1_sol01, gen005_full_1_sol01]
contradicted_by: []
related_ideas: [idea_005, idea_008, idea_020, idea_022]
tags: [exact-method, constraint-programming, ilp, cp-sat]
---

Uses Google OR-Tools CP-SAT solver with k integer variables + AllDifferent on differences.
Proved Singer suboptimal for small N (q=7: 8→10 optimal, q=11: 12→13 optimal).

**Gen 5 results:** Three 600s CP-SAT phases for k=103 all UNKNOWN. Key insight: optimal
sets share almost no elements with Singer (3/8 overlap q=7, 1/12 overlap q=11).

**Gen 6 results (full_1) — significant new evidence:**
- k=106 with 105-mark hint, 1200s, 16 workers → UNKNOWN (no feasible solution found)
- k=104 verification (30s, 8 workers) → UNKNOWN (surprisingly, even with 105-element hint)
- k=106 with linearization_level=2, symmetry_level=2 (600s) → UNKNOWN
- Binary search on N: k=106 at N=10000, 10200, 10500, 11000, 12000, 15000 all UNKNOWN
- **VLNS (fix 85, solve for 21):** 9 trials all INFEASIBLE in <1s — likely formulation bug
  (abs-equality domain conflict in presolve, not genuine infeasibility)

**Gen 6 insights:**
1. k=106 difficulty is NOT primarily from tight N=10000 bound — still hard at N=15000
2. The AllDifferent formulation may be too hard for CP-SAT to make search progress
3. VLNS could work if formulation bug is fixed (domain [1,N] → [0,N] for cross-diffs)
4. 105-element hint doesn't help even for k=104 — hint propagation may be ineffective

**Confidence reduced to 0.4** — three generations of compute (gens 4-6) with zero progress.
Still the only viable path to 106+ but needs either much longer runs (4h+), fixed VLNS
formulation, or alternative solvers (Gurobi, SCIP).


### [active] idea_024

---
id: idea_024
type: idea
name: "VLNS — Very Large Neighborhood Search via CP-SAT"
lifecycle: active
confidence: 0.3
first_seen: generation_6
last_updated: generation_6
last_confirmed_gen: 6
cluster: cluster_004
supported_by: []
contradicted_by: []
related_ideas: [idea_019, idea_022, idea_020]
tags: [vlns, cp-sat, neighborhood-search, hybrid]
---

Fix most elements of the 105-mark set, use CP-SAT to find optimal replacements for the
remaining free elements. This decomposes the intractable k=106 problem into many smaller
sub-problems (e.g., fix 85 elements, solve for 21 free elements).

**Gen 6 results (full_1/sol03):** 9 trials with different removal patterns (random-15/20/25,
high-density-20, spread-20) all returned INFEASIBLE in <1 second.

**CRITICAL: Likely formulation bug, not genuine infeasibility.**
The `add_abs_equality(d, y[i] - fv)` creates a difference variable with domain [1, N]
(excluding fixed differences). During presolve, if y[i] = fv is still in the variable's
domain, the absolute difference is 0 — excluded by the [1,N] domain → INFEASIBLE.

**Fix needed:** Change cross-diff domain from [1,N] to [0,N] and add explicit `d >= 1`
constraint, or add `y[i] != fv` constraints before the abs constraint so they propagate
during presolve.

**Potential:** If the formulation bug is fixed, VLNS could efficiently search large
neighborhoods around the 105-mark set. Each sub-problem has only ~20 free variables
vs 106 for the full problem. Even finding alternative 105-element sets would be
valuable (different local optima may be extensible).

**Priority:** Fix formulation and retry with 50+ removal patterns before declaring this
approach dead.


### [active] idea_025

---
id: idea_025
type: idea
name: "Ruzsa-Lindström Construction as SA Seed"
lifecycle: active
confidence: 0.2
first_seen: generation_6
last_updated: generation_6
last_confirmed_gen: 6
cluster: cluster_001
supported_by: []
contradicted_by: []
related_ideas: [idea_004, idea_006, idea_010, idea_022]
tags: [algebraic, ruzsa, construction, seed, untested]
---

Ruzsa-Lindström construction: for prime p, use primitive root g mod p and define
S = {x*p + g^x mod p : x in {0,...,p-1}}. This produces a p-element Sidon set in
{0,...,p²-1}. For N=10000: p=97 gives 97 elements in {0,...,9408}, p=101 gives ~99
elements in {0,...,10200} (filter to ≤10000).

**Rationale:** This is algebraically distinct from Singer (projective plane) and
Bose-Chowla (affine plane). The gen 5 finding that optimal small-N sets share almost
no elements with Singer suggests that starting from a structurally different seed
might reach different basins of attraction under local search.

**Source:** Research_1 gen 6 (from training data). Not yet implemented or tested.
May correspond to "rl" type in Rokicki-Dogon database.

**Expected outcome:** p=97 gives ~97 elements (below Singer 102 and Bose-Chowla 105).
The value is not in the raw set size but in potentially reaching different local optima
under SA/LNS. If the swap landscape from Ruzsa seeds differs from Bose-Chowla seeds,
this could enable finding 106+ element sets.

**Priority:** Low — the raw construction score is below current best. Only worth testing
if combined with SA/perturbation to explore the non-algebraic solution space.


### [active] pattern_009

---
type: pattern
id: pattern_009
name: "Singer q=101 perturbation is provably futile for all k"
lifecycle: active
confidence: 0.9
first_seen: generation_3
last_updated: generation_4
evidence: [gen003_exploit_1_sol01, gen003_experimentator_1, gen004_experimentator_1]
related_ideas: [idea_012, idea_017, idea_008]
tags: [singer-101, perturbation, dead-end, proof]
---

Combined evidence from gen 2 (small k=1-5), gen 3 (large k=5-25, plus blocker analysis),
and gen 4 (corrected blocker count) proves that perturbation of the Singer q=101 set
cannot exceed 102 for any value of k:

- **k < 43**: The minimum blocker count is **43** (at c=9931). Removing fewer than 43
  elements cannot free even a single new candidate. (Corrected from gen 3's claim of 45;
  experimentator_1 gen 4 found the true minimum is 43.)
- **k = 5-25**: 4000+ random and strategic trials, all return <= 102 (exploit_1 gen 3).
- **k >= 43**: The base drops to <=59 elements. No greedy extension from 59 elements has
  ever reached 102, let alone 103.

**Gen 4 addition**: Experimentator_1 also showed that removing all 43 blockers of c=9931
leaves only 59 elements. Pair-trade analysis (3828 pairs) found net gain 0 universally.
2-element trades are structurally impossible for this set.

This closes the entire perturbation research direction for Singer q=101.


### [archived] idea_003

---
id: idea_003
type: idea
name: "Difference-Aware Construction"
lifecycle: archived
confidence: 0.2
first_seen: generation_0
last_updated: generation_6
last_confirmed_gen: 4
supported_by: [gen004_explore_2_sol01]
contradicted_by: []
related_ideas: [idea_005, idea_016, idea_015]
cluster: cluster_002
tags: [construction, difference-aware, heuristic, greedy-variant, archived]
---

Instead of checking violations after the fact, maintain the set of used differences explicitly. When choosing the next element to add, pick one that uses "rare" differences (large gaps in the difference spectrum). This leaves more room for future elements.

Used peripherally in several solutions and now centrally tested via idea_016 (min-blocking greedy). Gen 4 confirmed that the corrected min-blocking implementation achieves 69 elements — identical to the Fibonacci ordering ceiling (idea_015). The concept has practical value but does not break the non-algebraic greedy ceiling of ~69.

**Gen 6 consistency review**: Archived. Ceiling 69, 36 elements below frontier (105). 2 generations stale (last confirmed gen 4). No further value as a standalone idea. The cluster_002 (search-based methods) is exhausted.


### [archived] idea_015

---
id: idea_015
type: idea
name: "Fibonacci/Exponential Ordering Greedy"
lifecycle: archived
confidence: 0.2
first_seen: generation_3
last_updated: generation_6
last_confirmed_gen: 3
cluster: cluster_002
supported_by: [gen003_explore_2_sol05]
contradicted_by: []
related_ideas: [idea_001, idea_003, idea_016, idea_021]
tags: [greedy, ordering, fibonacci, exhausted, archived]
---

Uses Fibonacci-like sequences to determine candidate ordering for greedy construction.
Best result: 69 elements from 2400+ parameter trials (gen 3).

Ceiling 69 confirmed. Beam search (idea_021) achieves 70, establishing this as sub-optimal
within the greedy family. Greedy direction conclusively closed (pattern_011, pattern_013).

**Gen 6 consistency review**: Archived. 3 generations stale (last confirmed gen 3).
Ceiling 69, 36 below frontier (105). Cluster_002 exhausted. No further exploration warranted.


### [archived] idea_016

---
id: idea_016
type: idea
name: "Min-Blocking Greedy"
lifecycle: archived
confidence: 0.2
first_seen: generation_3
last_updated: generation_6
last_confirmed_gen: 4
cluster: cluster_002
supported_by: [gen004_explore_2_sol01]
contradicted_by: []
related_ideas: [idea_003, idea_005, idea_015, idea_021]
tags: [greedy, min-blocking, exhausted, archived]
---

Picks candidates that block the fewest other valid candidates. Corrected implementation
(gen 4) achieves 69 elements.

Ceiling 69 confirmed. Ties with Fibonacci ordering, below beam search (70). Greedy direction
conclusively closed (pattern_011, pattern_013).

**Gen 6 consistency review**: Archived. Ceiling 69, 36 below frontier (105).
Cluster_002 exhausted. No further exploration warranted.


### [archived] idea_021

---
id: idea_021
type: idea
name: "Beam Search Greedy"
lifecycle: archived
confidence: 0.2
first_seen: generation_5
last_updated: generation_6
last_confirmed_gen: 5
cluster: cluster_002
supported_by: [gen005_explore_1_sol01, gen005_explore_1_sol05, gen005_explore_1_sol07]
contradicted_by: []
related_ideas: [idea_015, idea_016, idea_003]
tags: [beam-search, greedy, ceiling-confirmed, archived]
---

Maintains k parallel partial Sidon sets, extending with best candidates. Seven variants
tested in gen 5 with k=30 to k=800.

Best result: **70 elements** (k=500, greedy candidate selection). k=800 produces identical
result — beam width saturates below 500 effective unique beams.

**Gen 6 consistency review**: Archived. Ceiling 70 confirmed and saturated. 35-element gap
to algebraic best (105) is structural. Cluster_002 exhausted. No further exploration warranted.


### [confirmed] pattern_011

---
type: pattern
id: pattern_011
name: "All greedy variants ceiling at 66-70"
lifecycle: confirmed
confidence: 0.9
first_seen: generation_3
last_updated: generation_5
evidence: [gen003_explore_2_sol05, gen004_explore_1_sol01, gen004_explore_2_sol01, gen005_explore_1_sol05, gen005_explore_1_sol07]
related_ideas: [idea_001, idea_003, idea_015, idea_016, idea_021]
tags: [greedy, ceiling, structural-limit]
---

All greedy-family approaches for Sidon set construction in {0, ..., 10000} converge to
a ceiling of 66-70 elements regardless of candidate selection strategy or beam width.

**Updated hierarchy (gen 5)**:
- Random greedy: 58-63
- Standard ascending greedy: 66
- LNS from greedy: 67
- SA from greedy: 68
- Fibonacci ordering: 69
- Min-blocking greedy: 69
- **Beam search k=500+: 70** (NEW gen 5 — ceiling confirmed, k=800 identical to k=500)

**Gen 5 update**: Beam search (idea_021) was the last untested greedy variant. It reaches
70, exactly 1 above the previous ceiling. The beam width saturates at k=500. This
conclusively establishes the greedy-family structural limit at ~70 for N=10000.

The 30+ element gap between greedy ceiling (70) and algebraic constructions (105) confirms
that fundamentally different approaches are needed for competitive scores.


### [debunked] idea_001

---
type: idea
id: idea_001
name: "Randomized Greedy with Restarts"
lifecycle: debunked
confidence: 0.05
first_seen: generation_0
last_updated: generation_3
last_confirmed_gen: 1
supported_by: []
contradicted_by: [gen001_explore_2_sol01, gen001_full_1_sol01, gen003_explore_2_sol01]
related_ideas: [idea_009, idea_015]
cluster: cluster_002
tags: [search, greedy, restarts, debunked]
---

The basic greedy algorithm always adds the smallest valid element, giving 66.
Try random orderings of candidates: shuffle the range [0, 10000] and greedily
add elements that don't violate the Sidon property. Run many restarts and keep
the best. Different random orderings explore different parts of the search space.

**Generation 1 evidence**: Random-order greedy consistently scores 58-62 elements,
significantly WORSE than deterministic greedy (66). Confirmed by explore_2 and full_1.

**Generation 3 evidence**: explore_2/sol01 confirmed again: 63 elements with 25 seconds
of random restarts. Still below deterministic greedy (66).

**Verdict**: Downgraded to debunked. Three generations of evidence confirm randomized
greedy is counterproductive. The deterministic forward scan has algebraic structure
(Erdos-Turan) that random ordering destroys. Fibonacci ordering (idea_015) is the correct
way to modify greedy candidate ordering — it achieves 69 by using exponential growth
structure rather than random shuffling.


### [debunked] idea_002

---
type: idea
id: idea_002
name: "Local Search (Swap Neighborhood)"
lifecycle: debunked
confidence: 0.1
first_seen: generation_0
last_updated: generation_4
last_confirmed_gen: 3
supported_by: []
contradicted_by: [gen003_explore_2_sol06, gen003_explore_2_sol04]
related_ideas: [idea_010, idea_018]
cluster: cluster_002
tags: [search, local-search, swap, debunked]
---

Start from a greedy Sidon set. Define neighborhood: remove one element, try
adding a different one. Accept if the set grows or stays same size with more
room for future additions. Iterate until no improvement. Can be combined with
simulated annealing to escape local optima.

**Evidence summary across 4 generations**:
- LNS from greedy-66: 67 (gen 3, +1 only)
- LNS from spread-first-65: no improvement (gen 3)
- SA with violation relaxation from fib-68: no improvement (gen 3)
- All SA variants debunked (idea_010, idea_018)
- 8 central trials across all gens, best score 68

**Verdict (gen 4 consistency review)**: Downgraded from disputed to debunked. The maximum
gain from any local search variant is +1 element over the greedy seed. SA is confirmed
useless (idea_010, idea_018 both debunked). Pure local search provides negligible improvement
and is not a viable path to competitive scores. The +1 gain does not justify continued
investment when the gap to frontier is 33+ elements.


### [debunked] idea_005

---
id: idea_005
type: idea
name: "Backtracking with Pruning"
lifecycle: debunked
confidence: 0.05
first_seen: generation_0
last_updated: generation_6
last_confirmed_gen: 0
cluster: cluster_002
supported_by: []
contradicted_by: [gen006_explore_1_sol01]
related_ideas: [idea_003, idea_016]
tags: [search, backtracking, exhaustive, debunked]
---

DFS-based construction with aggressive pruning based on remaining valid candidates.

**Generation 6 — FIRST AND FINAL TEST (explore_1/sol01, score: 66):**
Systematic DFS with candidate-count upper bound pruning. Two phases:
1. Sequential ordering (0..N): finds exactly the greedy set (66 elements), then spends
   all remaining time (~27s) backtracking with zero improvement.
2. Randomized restarts (shuffled candidate order): also fails to exceed 66.

**Key insight:** The sequential DFS IS greedy — the forward pass produces the standard
greedy set, and backtracking from 66 elements at N=10000 explores a vanishingly small
fraction of the search tree in 27s. A C implementation (100x speedup) might reach 67-70
but cannot compete with algebraic constructions (105).

**Verdict: Debunked.** After 6 generations of being untested, the first empirical test
confirms backtracking is impractical for N=10000 in bounded time. The approach requires
exponential time to escape the greedy basin. Only potentially useful for small sub-problems
(N≤200) or with a C implementation + much longer time budgets.


### [debunked] idea_010

---
type: idea
id: idea_010
name: "Simulated Annealing from Algebraic Seed"
lifecycle: debunked
confidence: 0.1
first_seen: generation_1
last_updated: generation_3
last_confirmed_gen: 2
supported_by: []
contradicted_by: [gen002_exploit_2_sol01, gen002_exploit_2_sol03, gen003_explore_2_sol06]
related_ideas: [idea_002, idea_006, idea_007, idea_008, idea_018]
cluster: cluster_003
tags: [hybrid, simulated-annealing, search, debunked]
---

Use a high-quality algebraic seed as the starting point for simulated annealing, allowing
temporary size reductions to explore the fitness landscape beyond local optima.

**Generation 2 evidence**: Two SA runs from Singer seeds: SA from 99-element q=97 perturbation
(114s, ~500K iterations, no improvement) and SA from 102-element q=101 truncation (114s,
Boltzmann acceptance, no improvement).

**Generation 3 evidence**: explore_2/sol06 tested SA with violation relaxation (objective =
size - 8*violations) from a 68-element Fibonacci greedy set. 58 seconds, no improvement.
This extends the SA failure to non-algebraic seeds — SA fails not just because Singer sets
are saturated, but because the Sidon constraint landscape fundamentally resists local search.

**Verdict**: Downgraded to debunked. SA has been tried:
1. From Singer q=97 seed (99 elements) — fails
2. From Singer q=101 seed (102 elements) — fails
3. From Fibonacci greedy seed (68 elements) — fails
4. With standard SA and violation-relaxed SA — both fail

Three generations of evidence with zero improvement across all seed types and SA variants.
The swap neighborhood is structurally disconnected for Sidon sets at sizes >60.


### [debunked] idea_012

---
type: idea
id: idea_012
name: "Singer q=101 Perturbation (Remove-k, Re-extend)"
lifecycle: debunked
confidence: 0.05
first_seen: generation_2
last_updated: generation_4
last_confirmed_gen: 2
supported_by: []
contradicted_by: [gen002_exploit_1_sol01, gen002_exploit_2_sol04, gen003_exploit_1_sol01, gen003_experimentator_1, gen004_experimentator_1]
related_ideas: [idea_007, idea_008, idea_006, idea_017]
cluster: cluster_003
tags: [hybrid, perturbation, singer-101, debunked, dead-end]
---

Apply the perturbation strategy (idea_007) to the Singer q=101 base of 102 elements. Remove
k elements, then greedily re-extend.

**Generation 2 evidence**: Small-k (1-5) tested exhaustively. Net zero every time.

**Generation 3 evidence**: exploit_1 tested large-k (5-25) with strategic and random removals
(4000+ trials). All returned <=102. Experimentator_1 proved minimum blocker count.

**Generation 4 correction**: Experimentator_1 found the true minimum blocker count is **43**
(at c=9931), not 45 as reported in gen 3. For k < 43, perturbation is provably futile —
cannot free even a single new candidate. For k >= 43, the base drops to <=59 elements and
greedy recovery cannot reach 103.

**Verdict**: Debunked. Perturbation of Singer q=101 is proven ineffective across the full
spectrum of k values. The 43-blocker minimum creates a structural barrier that no
perturbation size can overcome.


### [debunked] idea_013

---
type: idea
id: idea_013
name: "Multi-Singer Hybrid (Elements from Multiple Prime Fields)"
lifecycle: debunked
confidence: 0.05
first_seen: generation_2
last_updated: generation_6
last_confirmed_gen: 4
supported_by: []
contradicted_by: [gen004_experimentator_1]
related_ideas: [idea_006, idea_008]
cluster: cluster_003
tags: [algebraic, singer, hybrid, debunked]
---

Combine elements from Singer sets of different primes (e.g., core from q=101, extensions
from q=97 or q=103) to build a hybrid Sidon set larger than any single Singer construction.

**Generation 4 evidence (experimentator_1) — DEFINITIVELY DEBUNKED**:
- Full Singer-102 base + Singer-97 additions: **0 additions**
- Full Singer-102 base + ET-71 additions: **0 additions**
- Singer-97 base (98) + Singer-101 additions: **0 additions**
- Reduced bases (k=40-90 from Singer-102) + Singer-97: additions only appear at k<=60,
  all totals well below 102
- Three-way hybrid (Singer-97 + Singer-101 + ET-71): net gain 0 for k=70-85

**Verdict**: Singer sets from different primes are completely incompatible at competitive
base sizes. The difference structures of different Singer primes collide extensively.
At full base (102 elements), zero elements from any other Singer prime can be added.
This is a strong structural result, not just a search failure.

**Gen 6 consistency fix**: cluster field corrected from cluster_001 to cluster_003.


### [debunked] idea_014

---
type: idea
id: idea_014
name: "Probabilistic Alteration (Random Sample + Repair)"
lifecycle: debunked
confidence: 0.05
first_seen: generation_3
last_updated: generation_3
last_confirmed_gen: 3
supported_by: []
contradicted_by: [gen003_explore_1_sol01]
related_ideas: [idea_001, idea_002]
cluster: cluster_002
tags: [probabilistic, alteration, random-sampling, non-algebraic, debunked]
---

Sample a random subset of {0, ..., N} with probability p per element, then iteratively remove the element with the highest violation count until the set is valid Sidon. Finally, greedily extend with remaining elements in shuffled order. Run many seeds and probabilities to find the best result.

Generation 3 evidence: explore_1/sol01 tested 160 configurations (4 probabilities × 40 seeds). Best result: **63 elements** (p≈0.013). This is significantly worse than deterministic greedy (66) and much worse than Singer (102).

Analysis: The random sampling starts with ~130 elements (p=0.013 × 10001) but must remove ~67 to achieve validity. The repair phase is destructive — each removal cascades into worsening the set. The greedy extension recovers ~30 elements but cannot compensate.

Verdict: **Debunked.** This approach is fundamentally weaker than structured greedy because it starts from a random, violation-heavy state. The repair phase destroys any accidental structure. Scoring 63 — below even the greedy baseline of 66 — confirms this is not a viable direction.


### [debunked] idea_017

---
type: idea
id: idea_017
name: "Large-k Perturbation of Singer q=101 (k=5-25)"
lifecycle: debunked
confidence: 0.05
first_seen: generation_3
last_updated: generation_4
last_confirmed_gen: 3
supported_by: []
contradicted_by: [gen003_exploit_1_sol01, gen004_experimentator_1]
related_ideas: [idea_012, idea_007, idea_008]
cluster: cluster_003
tags: [perturbation, singer-101, large-k, search, debunked]
---

Extend the perturbation approach (idea_012) to larger k values (5-25 removals) from the
Singer q=101 102-element set. Three strategies tested:
1. Remove top-k blockers (elements that block the most non-member candidates)
2. Remove bottom-k blockers (least useful elements)
3. Random k-element removals (hundreds of trials per k)

Generation 3 evidence: exploit_1/sol01 tested k = 5, 8, 10, 12, 15, 18, 20, 25 with all
three strategies. Total: ~4000+ trials across all k values. Result: **102** (no improvement).
Every trial returned exactly 102 or fewer elements.

**Generation 4 correction**: Minimum blockers = **43** (corrected from 45, experimentator_1
gen 4). Removing k < 43 elements cannot free even a single candidate. For k >= 25, the base
drops to 77 elements, and greedy recovery from 77 cannot reach 103. There is a "valley"
between k=1 (net zero) and k=43+ (base too small) where no improvement is possible.

**Verdict**: Debunked. Large-k perturbation is a dead end for Singer q=101. The 43-blocker
minimum creates an impassable barrier for all perturbation sizes. Combined with idea_012,
perturbation of Singer q=101 is proven futile for ALL k values.


### [debunked] idea_018

---
type: idea
id: idea_018
name: "SA with Violation Relaxation"
lifecycle: debunked
confidence: 0.05
first_seen: generation_3
last_updated: generation_3
last_confirmed_gen: 3
supported_by: []
contradicted_by: [gen003_explore_2_sol06]
related_ideas: [idea_010, idea_002]
cluster: cluster_003
tags: [simulated-annealing, violations, relaxation, non-algebraic, debunked]
---

Standard SA for Sidon sets fails because the valid neighborhood is empty at local optima. Relaxed SA uses objective = |S| - penalty × violations, allowing temporary violations. After SA completes, extract the largest valid Sidon subset.

Generation 3 evidence: explore_2/sol06 applied this to the 68-element Fibonacci greedy set. Parameters: T=3.0, T_min=0.05, alpha=0.9998, penalty=8.0. After 58 seconds: **68** (no improvement). The SA never found a valid state with more than 68 elements.

Analysis: The swap neighborhood (remove 1, add 1) with violation relaxation is still too local. Moving through violated states requires coordinated multi-element rearrangements that random swaps almost never find. The penalty term prevents SA from exploring deeply violated states where structure might emerge.

Verdict: **Debunked.** Violation-relaxed SA doesn't help for non-algebraic sets either. Previously shown to fail for Singer seeds (idea_010); now confirmed to fail for search-found seeds too. The fundamental issue is that Sidon constraint satisfaction is too globally coupled for local swap neighborhoods, regardless of relaxation. This, combined with idea_010's debunking, closes the SA research direction entirely.


### [established] idea_004

---
type: idea
id: idea_004
name: "Modular Arithmetic Structure"
lifecycle: established
confidence: 0.9
first_seen: generation_0
last_updated: generation_2
last_confirmed_gen: 2
supported_by: [gen001_explore_1_sol01, gen001_explore_1_sol02, gen001_explore_1_sol03, gen001_explore_1_sol04, gen002_exploit_1_sol01, gen002_exploit_1_sol03]
contradicted_by: []
related_ideas: [idea_006, idea_008, idea_009]
cluster: cluster_001
tags: [algebraic, modular, structure]
---

Elements chosen with modular structure (e.g., quadratic residues, powers modulo a prime) tend to have good difference properties. Explore sets of the form {f(k) mod N : k in range} for various functions f. The structure provides a scaffold that can then be improved by local search.

Generation 1 evidence: This idea is strongly confirmed through the Singer difference set (idea_006), which is the specific instantiation of this general principle. Singer uses GF(q³) arithmetic to produce perfect difference sets. The Erdos-Turan construction (idea_009) is another instance, explaining the greedy-66 baseline.

Caution: Not all modular constructions work. The parabola construction {i*p + (i² mod p)} was tried by full_1 and FAILED for large primes (312 violations for p=101). The construction is only valid for small primes. GF(p³) (Singer) is the correct framework, not simple quadratic residues mod p.

Status: Established. This is the foundational principle behind all competitive solutions. Note: the stale copy in ideas/active/ should be deleted — this established/ version is canonical.


### [established] idea_006

---
type: idea
id: idea_006
name: "Singer Difference Set Construction"
lifecycle: established
confidence: 0.95
first_seen: generation_1
last_updated: generation_4
last_confirmed_gen: 4
supported_by: [gen001_explore_1_sol01, gen001_explore_1_sol02, gen001_explore_1_sol03, gen001_explore_1_sol04, gen004_research_1_sol01]
contradicted_by: []
related_ideas: [idea_003, idea_004, idea_007, idea_008, idea_009]
cluster: cluster_001
tags: [algebraic, singer, construction, high-impact]
---

The Singer difference set is the dominant algebraic construction for Sidon sets. For a prime
power q, the Singer (q^2+q+1, q+1, 1)-difference set gives exactly q+1 elements in
{0, ..., q^2+q} with ALL pairwise differences distinct — a perfect Sidon set.

**For q=97**: The construction yields 98 elements in {0, ..., 9506}, all within {0, ..., 10000}.
This is a jump of +32 over the greedy baseline of 66. Implementation uses GF(97^3) arithmetic:
find an irreducible cubic over GF(97), compute a primitive element, then collect indices k
where the k-th power has zero third component (or equivalently, zero trace). Alternatively,
use the m-sequence recurrence method: find a primitive polynomial x^3 - a_1*x^2 - a_2*x - a_3 over
GF(97), run the linear recurrence, and collect zero indices.

**Evidence**: explore_1/sol01 implemented this and scored 98 (is_valid=1, violations=0) in
0.02 seconds. The construction is deterministic and fast. All four explore_1 solutions used
Singer as their foundation. Gen 4 research_1 confirmed Singer q=103 also works but keeps
only 102 elements in range (min span 10290 > 10000).

**Critical implementation note**: Must use the PRIMITIVE element of GF(q^3)*, not a subgroup
element. Using a subgroup element (e.g., g^96 instead of g) produced 84 elements with 1540
violations. This is a subtle but important distinction not clearly stated in standard references.

**Saturation property**: The Singer set for q=97 uses ALL 9506 positive differences exactly once.
This means the s

[TRUNCATED — read full file for details]


### [established] idea_007

---
type: idea
id: idea_007
name: "Singer Set Perturbation (Remove-k, Re-extend)"
lifecycle: established
confidence: 0.9
first_seen: generation_1
last_updated: generation_2
last_confirmed_gen: 2
supported_by: [gen001_explore_1_sol02, gen001_explore_1_sol03, gen001_explore_1_sol04, gen002_exploit_2_sol01]
contradicted_by: []
related_ideas: [idea_002, idea_006, idea_008, idea_010]
cluster: cluster_003
tags: [hybrid, perturbation, singer, local-search]
---

Starting from the 98-element Singer set (idea_006), remove 1-3 elements to free up their
pairwise differences, then greedily extend the set using candidates from the full range
{0, ..., 10000} (including elements above 9506 not reachable by Singer alone).

**Generation 1 evidence**: explore_1/sol02-04 all achieved fitness=99 using this approach.

**Generation 2 evidence**: exploit_2/sol01 applied SA from the 99-element Singer q=97 perturbation
seed. After 114 seconds and ~500K SA iterations, result remained 99. This confirms the 99-element
basin around Singer q=97 perturbation is a robust local optimum that SA cannot escape.

**Superseded**: With Singer q=101 truncation (idea_008) achieving 102, the Singer q=97 perturbation
approach is no longer the frontier. Its peak of 99 is 3 elements below the new best. However,
the perturbation methodology remains valuable — applying it to the q=101 base (102 elements)
is the logical next step for pushing beyond 102.


### [established] idea_008

---
type: idea
id: idea_008
name: "Singer q=101 Truncation with Cyclic Shifts"
lifecycle: established
confidence: 0.95
first_seen: generation_1
last_updated: generation_2
last_confirmed_gen: 2
supported_by: [gen002_exploit_1_sol01, gen002_exploit_1_sol02, gen002_exploit_1_sol03, gen002_exploit_2_sol02, gen002_exploit_2_sol03, gen002_exploit_2_sol04]
contradicted_by: []
related_ideas: [idea_006, idea_007, idea_004]
cluster: cluster_001
tags: [algebraic, singer, truncation, high-impact, confirmed]
---

The Singer set for q=101 has 102 elements in Z_{10303}. Since 10303 > 10000, not all elements
necessarily fit in {0, ..., 10000}. However, with the optimal cyclic shift, ALL 102 elements
fit in range — zero truncation loss.

**Generation 2 evidence**: exploit_1 implemented this and scored **102** (is_valid=1, violations=0).
The construction uses GF(101³) with irreducible cubic x³ - 3x - 1 and primitive element (0,0,2).
The optimal cyclic shift d=2337 places all 102 elements within {0, ..., 10000}. Confirmed
independently by exploit_2/sol02 (different shift selection method, same result).

**Key findings from gen 2**:
- 569 out of 10303 cyclic shifts (5.5%) preserve all 102 elements within range.
- 43.5% of shifts give ≥100 elements. The averaging argument mathematically guarantees
  ≥105 shifts give ≥100 elements (proved by research_1).
- All 1054 irreducible cubics over GF(101) give identical shift distributions (PGL equivalence).
- Singer q=103 (104 elements in Z_{10713}) gives at most 102 in range. q=107 gives 100. q=109 gives 98.
  q=101 is optimal for N=10000.
- Greedy extension from the 102-element truncated set adds 0 elements — the set is locally saturated.

**Status**: Upgraded from active to established. This is now the dominant construction, superseding
Singer q=97 perturbation (idea_007) for achieving the highest score.


### [established] idea_009

---
type: idea
id: idea_009
name: "Erdos-Turan Construction"
lifecycle: established
confidence: 0.8
first_seen: generation_1
last_updated: generation_6
last_confirmed_gen: 6
supported_by: [gen001_full_1_sol01, gen002_explore_1_sol01, gen002_explore_1_sol02, gen002_explore_1_sol03, gen002_explore_1_sol04, gen006_explore_1_sol02, gen006_explore_1_sol03, gen006_explore_1_sol04]
contradicted_by: []
related_ideas: [idea_003, idea_004, idea_006, idea_011]
cluster: cluster_001
tags: [algebraic, erdos-turan, baseline-explanation, confirmed-alternative]
---

The Erdos-Turan (1941) construction: for prime p, define S_ET(p) = {2pk + (k^2 mod p) : k = 1, ..., p-1}.
This gives p-1 elements that form a Sidon set. The spacing of 2p prevents carry violations,
making it provably valid for all primes.

**Generation 2 evidence**: explore_1 (Track B, non-Singer) implemented ET(71) and confirmed:
- ET(71) base: 70 elements in {143, ..., 9941}. Valid, zero violations.
- ET(71) + greedy extension: 74 elements.
- ET(71) + greedy + 1-opt: 75 elements. This is a robust local optimum — all random restarts converge to 75.

**Generation 6 evidence**: explore_1 confirmed 75 ceiling with 2-opt, LNS (k=2-15), and 30+ randomized restarts. Hard structural ceiling (pattern_015).

**Ceiling**: ET-based approaches max at ~75 elements (vs algebraic best 105). The construction is
mathematically sound but fundamentally less powerful than Singer/Bose-Chowla.

**Gen 6 consistency fix**: last_confirmed_gen updated to 6 (was stuck at 2). Added gen 6 evidence to supported_by.


### [established] idea_020

---
type: idea
id: idea_020
name: "Rokicki-Dogon Near-Optimal Golomb Rulers"
lifecycle: established
confidence: 0.95
first_seen: generation_4
last_updated: generation_6
last_confirmed_gen: 6
supported_by: [gen005_experimentator_1_sol01, gen005_experimentator_1_sol02, gen005_experimentator_1_sol03, gen005_research_1_sol01, gen005_research_1_sol02, gen006_exploit_1_sol01, gen006_full_1_sol01, gen006_full_1_sol02, gen006_full_1_sol03, gen006_full_1_sol04]
contradicted_by: []
related_ideas: [idea_006, idea_008, idea_022, idea_023]
cluster: cluster_001
tags: [literature, golomb-rulers, construction, high-impact, verified]
---

The Rokicki-Dogon "Possibly Optimal Golomb Rulers" database (cube20.org/golomb) contains
near-optimal Golomb ruler constructions (equivalent to Sidon sets) for various mark counts
and spans.

**Generation 5 — VERIFIED AND EXPLOITED**:
Both experimentator_1 and research_1 independently downloaded and parsed the database.
Key results:

| Marks | Span  | Type | q   | Multiplier | Fitness |
|-------|-------|------|-----|------------|---------|
| 105   | 9884  | ap   | 107 | 433        | **105** |
| 104   | 9581  | pp   | 103 | 400        | **104** |
| 103   | 9408  | pp   | 103 | 400        | **103** |
| 102   | 9218  | pp   | 101 | 1758       | 102     |

**Generation 6**: Used as baseline by exploit_1 (perturbation analysis) and full_1 (CP-SAT warm-start, VLNS). The 105-mark set's self-healing property (pattern_014) was discovered through Rokicki-Dogon data.

**Exhaustive search confirms 105 is the ceiling** from this database for N=10000.

**Gen 6 consistency fix**: last_confirmed_gen updated to 6. Added gen 6 solutions to supported_by.


### [established] idea_022

---
type: idea
id: idea_022
name: "Bose-Chowla Affine Plane Construction"
lifecycle: established
confidence: 0.95
first_seen: generation_5
last_updated: generation_6
last_confirmed_gen: 6
supported_by: [gen005_experimentator_1_sol01, gen005_research_1_sol01, gen006_exploit_1_sol01, gen006_full_1_sol01]
contradicted_by: []
related_ideas: [idea_006, idea_004, idea_011, idea_020]
cluster: cluster_001
tags: [algebraic, bose-chowla, affine-plane, construction, high-impact]
---

The Bose-Chowla affine plane construction (type "ap" in Rokicki-Dogon) generates Sidon
sets of size q for prime q, using a different algebraic structure than Singer (projective
plane, size q+1). For prime q, the construction operates in Z_{q^2-1} and applies a
multiplier to optimize span.

**Generation 5 — BREAKTHROUGH**:
- **q=107, multiplier=433**: 105-mark ruler with span=9884. All 105 elements fit in
  {0, ..., 10000}. **Fitness = 105** (pipeline best, +3 over Singer q=101).
- Two independent implementations confirmed (experimentator_1, research_1).

**Generation 6 — STRUCTURAL ANALYSIS**:
- **Self-healing property** (pattern_014): Removing any k elements (k=1-104) opens exactly
  k addable slots = the removed elements. 27K+ perturbation trials, all return 105.
- The swap landscape around 105 is completely flat (zero extensible alternatives).
- Singer pp q=107/109/113 exhaustive multiplier search: max 105/104/102 in [0,10000].

**Algebraic ceiling**: 105 is the maximum achievable by any known algebraic construction for N=10000.

**Maximality**: The 105-mark set is greedy-maximal with zero combinatorial slack.

**Gen 6 consistency fix**: Added gen 6 solutions to supported_by. Added idea_011 to related_ideas.


### [established] idea_023

---
type: idea
id: idea_023
name: "Multiplier Optimization for Algebraic Constructions"
lifecycle: established
confidence: 0.9
first_seen: generation_5
last_updated: generation_5
last_confirmed_gen: 5
supported_by: [gen005_experimentator_1_sol01, gen005_experimentator_1_sol02, gen005_research_1_sol02]
contradicted_by: []
related_ideas: [idea_006, idea_022, idea_008]
cluster: cluster_001
tags: [algebraic, multiplier, optimization, span-minimization]
---

When constructing Sidon sets from algebraic difference sets (Singer pp, Bose-Chowla ap),
applying a multiplier k to all elements modulo the group order can dramatically change the
span of the resulting set. Searching for the optimal multiplier is essential for fitting
the most marks into a bounded range.

**Generation 5 evidence**:
- **Singer q=103 (pp) with multiplier=400**: span=9581, fits 104 marks in {0..10000}.
  Previous pipeline implementations used multiplier=1, getting span ~10290 and only 102
  marks fitting. **The 4-generation mystery of why q=103 scored 102 is solved**: wrong
  multiplier.
- **Bose-Chowla q=107 (ap) with multiplier=433**: span=9884, fits 105 marks.
- **Exhaustive multiplier search for 106 marks**: experimentator_1 tested ALL coprime
  multipliers for q=107 (pp: 9072, ap: ~5700) and q=109 (pp: ~9900). Best 106-mark
  span is 10135 > 10000. No multiplier works for 106 marks.

**Why this matters**: The helpers/singer.py implementation does NOT search multiplier
space adequately. It produces raw Singer sets (effectively multiplier=1 or searches a
small subset). Future algebraic constructions MUST include exhaustive multiplier search
to find minimum span.

**Implication**: The pipeline was leaving 2-3 elements on the table for 4 generations
because it didn't know to search multipliers. This is a generalizable lesson: any
algebraic construction's "usable size for bounded N" depends critically on multiplier
optimization, not just the construction itself.


## All Clusters


### cluster_001

---
type: cluster
id: cluster_001
name: "Algebraic Constructions"
member_ideas: [idea_004, idea_006, idea_008, idea_009, idea_020, idea_022, idea_023, idea_025]
best_score: 105
best_solution: gen005_experimentator_1_sol01
status: active
last_updated: generation_6
---

This cluster contains all ideas based on algebraic/number-theoretic constructions for
Sidon sets.

**Gen 6 — consistency review update**:
- **idea_025 (Ruzsa-Lindström) ADDED**: New algebraic construction type, untested.
  Was claiming cluster_001 but not listed as member. Now added.
- **last_updated** corrected to gen 6 (gen 6 solutions used Bose-Chowla extensively).

**Performance**: **105** (Bose-Chowla ap q=107). All algebraic constructions exhausted.

**Constructive hierarchy for N=10000**:
| Marks | Construction | Multiplier | Span |
|-------|-------------|------------|------|
| 105   | Bose-Chowla ap q=107 | 433 | 9884 |
| 104   | Singer pp q=103 | 400 | 9581 |
| 103   | Singer pp q=103 | 400 | 9408 |
| 102   | Singer pp q=101 | 1758 | 9218 |

**Algebraic ceiling**: 105 (exhaustive multiplier search confirms 106 impossible for N=10000).
**Self-healing property** (pattern_014): The 105-mark set is perfectly rigid under perturbation.

**Next frontier**: Non-algebraic methods (CP-SAT, VLNS) or untested algebraic seed (idea_025 Ruzsa-Lindström).


### cluster_002

---
type: cluster
id: cluster_002
name: "Search-Based and Non-Singer Methods"
member_ideas: [idea_001, idea_002, idea_003, idea_005, idea_011, idea_014, idea_015, idea_016, idea_021]
best_score: 75
best_solution: gen002_explore_1_sol03
status: exhausted
last_updated: generation_6
---

This cluster contains ideas based on search heuristics, ordering strategies, and
non-Singer algebraic constructions.

**Gen 6 — CLUSTER STATUS: EXHAUSTED**

Two critical updates:
1. **idea_005 (Backtracking) DEBUNKED**: First empirical test (explore_1/sol01) scored 66
   (greedy baseline). DFS IS greedy for sequential ordering. Randomized restarts also fail.
   After 6 generations untested, now definitively closed.
2. **75 ceiling confirmed as hard structural barrier** (pattern_015): ET(71)+1-opt tested
   with 2-opt, LNS (k=2-15), and 30+ randomized restarts. All converge to exactly 75.

**All member ideas are now debunked or at confirmed ceilings:**
- idea_001 (Randomized Greedy): debunked, 58-63
- idea_002 (Local Search/LNS): debunked, max +1 gain
- idea_003 (Difference-Aware): active but peripheral only, ceiling 69
- idea_005 (Backtracking): **debunked gen 6**, 66
- idea_011 (ET Extension + Search): active, ceiling 75 (hard)
- idea_014 (Probabilistic Alteration): debunked, 63
- idea_015 (Fibonacci Ordering): active, ceiling 69
- idea_016 (Min-Blocking): active, ceiling 69
- idea_021 (Beam Search): active, ceiling 70

**Non-algebraic ceiling hierarchy (final):**
- Random greedy: 58-63
- Stand

[TRUNCATED — read full file for details]


### cluster_003

---
type: cluster
id: cluster_003
name: "Hybrid Approaches (Algebraic + Search)"
member_ideas: [idea_007, idea_010, idea_012, idea_013, idea_017, idea_018]
best_score: 102
best_solution: gen002_exploit_2_sol03
status: exhausted
last_updated: generation_4
---

This cluster combines algebraic construction seeds with search-based refinement.

**Status: EXHAUSTED.** All ideas in this cluster have been debunked or proven futile.

**Gen 4 consistency review changes**:
- **idea_013 now exclusively here** (removed from cluster_001 where it was duplicated).
- **Blocker minimum corrected**: True minimum is **43** (at c=9931), not 45 as previously
  reported. Corrected in idea_012, idea_017, and pattern_009.

Updated member status:
- idea_007 (Singer q=97 perturbation): Established, ceiling 99. Superseded.
- idea_010 (SA from algebraic seed): Debunked.
- idea_012 (Singer q=101 small-k perturbation): Debunked.
- idea_013 (Multi-Singer Hybrid): Debunked (gen 4).
- idea_017 (Singer q=101 large-k perturbation): Debunked.
- idea_018 (SA with violation relaxation): Debunked.

No further investment recommended in this cluster.


### cluster_004

---
type: cluster
id: cluster_004
name: "Exact Methods (ILP / Constraint Programming)"
member_ideas: [idea_019, idea_024]
best_score: 102
best_solution: gen004_full_1_sol01
status: active
last_updated: generation_6
---

This cluster contains ideas based on exact optimization methods — ILP, CP-SAT, and
constraint programming solvers.

**Gen 6 results (full_1) — major new evidence:**

1. **CP-SAT k=106 (1200s, 16 workers, 105-mark hint):** UNKNOWN. No feasible solution.
2. **k=104 verification (30s):** UNKNOWN — surprisingly hard even with full hint.
3. **Binary search on N:** k=106 UNKNOWN at N=10000, 10200, 10500, 11000, 12000, 15000.
   Difficulty is inherent to k=106, not driven by tight N bound.
4. **VLNS (idea_024, NEW):** Fix 85 elements, solve for 21 free → all 9 trials INFEASIBLE
   in <1s. **Likely formulation bug** (abs-equality domain conflict), not genuine infeasibility.

**Cumulative CP-SAT compute for k≥103:** ~6000s across gens 4-6, zero feasible solutions found.

**New member: idea_024 (VLNS)** — decompose intractable k=106 into smaller sub-problems.
Promising concept but needs formulation fix before real testing.

**Next steps (priority order):**
1. Fix VLNS formulation bug and retry with 50+ patterns
2. Overnight CP-SAT k=106 (4h+, 16 workers)
3. CP-SAT maximize formulation (find max k, not decision for fixed k)
4. Alternative solvers: Gurobi, SCIP, HiGHS
5. VLNS with maximize objective (find max elements given fixed subset)


## All Patterns


### [active] pattern_004

---
type: pattern
id: pattern_004
name: "99-to-100 barrier is robust across perturbation approaches"
lifecycle: active
confidence: 0.7
first_seen: generation_1
last_updated: generation_1
evidence: [gen001_explore_1_sol02, gen001_explore_1_sol03, gen001_explore_1_sol04]
related_ideas: [idea_007, idea_008, idea_010]
tags: [barrier, frontier, singer]
---

Three solutions (explore_1/sol02-04) all reached 99 elements via Singer perturbation but
none broke through to 100. Combined search time: ~280 seconds across different strategies
(small perturbation k=1-3, large perturbation k≤15, targeted blocker removal). All converged
to 99.

This suggests the 99-element basin around the Singer q=97 set is a robust local optimum
under greedy perturbation. Breaking to 100 likely requires either:
1. A different base construction (Singer q=101 truncation, idea_008)
2. A non-greedy search method that accepts temporary size decreases (SA, idea_010)
3. A fundamentally different algebraic approach

The barri

[TRUNCATED — read full file for details]


### [active] pattern_006

---
type: pattern
id: pattern_006
name: "102-element Singer q=101 set is locally saturated (40+ blockers per candidate)"
lifecycle: active
confidence: 0.85
first_seen: generation_2
last_updated: generation_2
evidence: [gen002_exploit_1_sol01, gen002_exploit_2_sol03, gen002_exploit_2_sol04]
related_ideas: [idea_008, idea_012, idea_010]
tags: [saturation, barrier, singer-101, blockers]
---

The 102-element Singer q=101 truncated set has extreme local saturation: every non-member
element in {0, ..., 10000} has at least 40 "blockers" — existing set members whose differences
would collide if the non-member were added.

Evidence:
- exploit_1: exhaustive single-removal (102 trials, net zero), exhaustive pair-removal (5151 pairs, net zero)
- exploit_2/sol03: SA from 102-element base, 114 seconds, no improvement
- exploit_2/sol04: partial shifts + greedy extension, no improvement

The 40-blocker minimum contrasts sharply with Singer q=97 perturbation, where some candidates
had only 4-10 blocker

[TRUNCATED — read full file for details]


### [active] pattern_007

---
type: pattern
id: pattern_007
name: "ET(71) + local search plateaus at 75"
lifecycle: active
confidence: 0.8
first_seen: generation_2
last_updated: generation_2
evidence: [gen002_explore_1_sol03, gen002_explore_1_sol04]
related_ideas: [idea_009, idea_011]
tags: [erdos-turan, local-optimum, non-singer]
---

The Erdos-Turan construction for p=71, extended greedily and refined with 1-opt local search,
converges to exactly 75 elements. This is a robust local optimum: 25 independent random
restarts with different orderings all converged to 75.

This establishes a hierarchy of construction ceilings:
- Raw greedy: 66 (strict 1-opt local optimum, pattern_001)
- SA from greedy: 68
- ET(71) + greedy + 1-opt: 75
- Singer q=97: 98
- Singer q=97 + perturbation: 99 (pattern_004)
- Singer q=101 truncation: 102 (pattern_005)

The 27-element gap between ET-based approaches (75) and Singer (102) confirms that
algebraic construction quality is the dominant factor, not search refinement.


### [active] pattern_008

---
type: pattern
id: pattern_008
name: "Non-algebraic search methods ceiling at 69 for N=10000"
lifecycle: active
confidence: 0.8
first_seen: generation_3
last_updated: generation_3
evidence: [gen003_explore_2_sol01, gen003_explore_2_sol02, gen003_explore_2_sol03, gen003_explore_2_sol04, gen003_explore_2_sol05, gen003_explore_2_sol06, gen003_explore_1_sol01]
related_ideas: [idea_001, idea_002, idea_015, idea_018]
tags: [ceiling, non-algebraic, search, landscape]
---

Generation 3 thoroughly explored non-algebraic search methods:

| Method | Best Score | Trials |
|--------|-----------|--------|
| Randomized greedy restarts | 63 | 25s worth |
| Probabilistic alteration | 63 | 160 configs |
| LNS from greedy-66 | 67 | 24s LNS |
| Spread-first greedy + LNS | 65 | multiple restarts |
| Fibonacci ordering greedy | 69 | 2400+ params |
| SA with violation relaxation | 68 | 58s |

The hierarchy is clear:
- Random greedy: 58-63
- Standard greedy: 66
- LNS from greedy: 67
- Fibonacci ordering: 6

[TRUNCATED — read full file for details]


### [active] pattern_009

---
type: pattern
id: pattern_009
name: "Singer q=101 perturbation is provably futile for all k"
lifecycle: active
confidence: 0.9
first_seen: generation_3
last_updated: generation_3
evidence: [gen003_exploit_1_sol01, gen003_experimentator_1]
related_ideas: [idea_012, idea_017, idea_008]
tags: [singer-101, perturbation, dead-end, proof]
---

Combined evidence from gen 2 (small k=1-5) and gen 3 (large k=5-25, plus blocker analysis)
proves that perturbation of the Singer q=101 set cannot exceed 102 for any value of k:

- **k < 45**: The minimum blocker count is 45. Removing fewer than 45 elements cannot free
  even a single new candidate. Proved by exhaustive blocker enumeration (experimentator_1).
- **k = 5-25**: 4000+ random and strategic trials, all return ≤ 102 (exploit_1).
- **k ≥ 45**: The base drops to ≤ 57 elements. No greedy extension from 57 elements has
  ever reached 102, let alone 103.

This closes the entire perturbation research direction for Singer q=101. The remove-k/re-

[TRUNCATED — read full file for details]


### [active] pattern_010

---
type: pattern
id: pattern_010
name: "Truncated Singer sets have zero addable elements for all primes tested"
lifecycle: active
confidence: 0.9
first_seen: generation_3
last_updated: generation_3
evidence: [gen003_experimentator_1]
related_ideas: [idea_006, idea_008, idea_013]
tags: [singer, saturation, rigidity, structural]
---

Experimentator_1 tested truncated Singer sets for q = 97, 101, 103, 107, 109, 113.
In every case, after optimal truncation to fit [0, 10000], the resulting set has ZERO
addable elements via greedy single-element extension.

This is surprising for larger primes where significant truncation occurs:
- q=107: loses 9 elements (108→99), freeing 927 differences. Still zero addable.
- q=109: loses 11 elements (110→99), freeing 1089 differences. Still zero addable.

The Singer difference structure has a deep rigidity property: even partial subsets
of Singer sets inherit full local saturation. This goes beyond the well-known "perfect
difference set uses all differen

[TRUNCATED — read full file for details]


### [active] pattern_011

---
type: pattern
id: pattern_011
name: "All greedy heuristics converge to 66-69 ceiling regardless of selection strategy"
lifecycle: active
confidence: 0.85
first_seen: generation_4
last_updated: generation_4
evidence: [gen004_explore_1_sol01, gen004_explore_2_sol01, gen003_explore_2_sol05, gen003_explore_2_sol03, gen003_explore_2_sol04]
related_ideas: [idea_016, idea_015, idea_003, idea_001]
tags: [ceiling, greedy, structural-limit]
---

Generation 4 confirmed that min-blocking greedy (idea_016, corrected) achieves 69 elements —
identical to the Fibonacci ordering ceiling (idea_015). Combined with prior generations:

| Greedy Variant | Best Score | Evidence |
|----------------|-----------|---------|
| Ascending (standard) | 66 | gen 1-3, many trials |
| Descending | 66 | gen 4 explore_2 |
| Random ordering | 58-63 | gen 1, 3 |
| Fibonacci ordering | 69 | gen 3 (2400+ params) |
| Min-blocking greedy | 69 | gen 4 (corrected impl) |
| Spread-first greedy | 65 | gen 3 |
| LNS from greedy

[TRUNCATED — read full file for details]


### [confirmed] pattern_001

---
type: pattern
id: pattern_001
name: "Greedy-66 is a strict 1-opt local optimum"
lifecycle: confirmed
confidence: 0.95
first_seen: generation_1
last_updated: generation_1
evidence: [gen001_explore_2_sol03, gen001_explore_2_sol04, gen001_explore_2_sol05, gen001_full_1_sol01]
related_ideas: [idea_002, idea_009]
tags: [landscape, local-optimum, greedy]
---

The standard greedy Sidon set (66 elements, built by adding the smallest valid element)
is a strict local optimum under 1-opt (single element swap). Removing any single element
from the greedy-66 set leaves exactly 1 available candidate — the removed element itself.
No single-element replacement improves the set.

Evidence from multiple agents: explore_2 confirmed via exhaustive single-removal scan
(sol03, sol05). full_1 independently verified: "after removing any single element, only 1
candidate becomes available." This explains why simple local search fails to improve on 66.

2-opt CAN escape: explore_2/sol04 found a 67-element se

[TRUNCATED — read full file for details]


### [confirmed] pattern_002

---
type: pattern
id: pattern_002
name: "Random-order greedy is worse than deterministic"
lifecycle: confirmed
confidence: 0.9
first_seen: generation_1
last_updated: generation_1
evidence: [gen001_explore_2_sol01, gen001_full_1_sol01]
related_ideas: [idea_001, idea_009]
tags: [greedy, randomization, counterintuitive]
---

Random-order greedy (shuffling candidates before greedy construction) consistently produces
Sidon sets of 58-62 elements, significantly worse than the deterministic forward-scan greedy
(66 elements). This is counterintuitive — random restarts usually help in combinatorial
optimization.

Explanation: The deterministic greedy packs small numbers first, which minimizes the magnitude
of used differences. This is equivalent to the Erdos-Turan construction (idea_009) for p=67.
Random ordering disrupts this algebraic structure and wastes differences on large gaps.

Implication: Random restarts are not useful for this problem. Any improvement over 66 must
come from algebraic 

[TRUNCATED — read full file for details]


### [confirmed] pattern_003

---
type: pattern
id: pattern_003
name: "Singer set is saturated — all differences used exactly once"
lifecycle: confirmed
confidence: 0.95
first_seen: generation_1
last_updated: generation_1
evidence: [gen001_explore_1_sol01]
related_ideas: [idea_006, idea_007]
tags: [singer, saturation, algebraic]
---

The Singer difference set for q=97 uses ALL 9506 positive differences {1, ..., 9506} exactly
once. This is the defining property of a perfect (v, k, 1)-difference set. As a consequence,
the Singer set is maximally "saturated" — no element from {0, ..., 9506} can be added without
creating a collision.

This saturation explains why greedy extension of Singer fails: any candidate element generates
98 new differences, all of which must be unused. With 100% difference coverage in {1, ..., 9506},
extensions are only possible using elements from {9507, ..., 10000}, and even those have very
low probability of fitting (each must avoid 98 collisions).

The perturbation approach (idea_007) works 

[TRUNCATED — read full file for details]


### [confirmed] pattern_005

---
type: pattern
id: pattern_005
name: "Singer q=101 is optimal prime for N=10000"
lifecycle: confirmed
confidence: 0.95
first_seen: generation_2
last_updated: generation_2
evidence: [gen002_exploit_1_sol01, gen002_exploit_2_sol02, gen002_exploit_2_sol04]
related_ideas: [idea_008, idea_006]
tags: [singer, optimization, prime-selection]
---

Among all Singer constructions for different primes q, q=101 maximizes the number of
elements achievable in {0, ..., 10000}:

| q   | Singer size | v = q²+q+1 | Best in {0,...,10000} |
|-----|-------------|------------|----------------------|
| 97  | 98          | 9507       | 98 (all fit)         |
| 101 | 102         | 10303      | **102** (all fit!)   |
| 103 | 104         | 10713      | 102                  |
| 107 | 108         | 11557      | 100                  |
| 109 | 110         | 11991      | 98                   |

q=101 hits the sweet spot: v=10303 is only 3% larger than 10001, so the best cyclic
shift can fit all 102 elements. Larger

[TRUNCATED — read full file for details]


### [confirmed] pattern_012

---
type: pattern
id: pattern_012
name: "105 is the algebraic ceiling for N=10000"
lifecycle: confirmed
confidence: 0.95
first_seen: generation_5
last_updated: generation_5
evidence: [gen005_experimentator_1_sol01, gen005_experimentator_1_sol02, gen005_experimentator_1_sol03, gen005_research_1_sol01, gen005_research_1_sol02]
related_ideas: [idea_022, idea_023, idea_006, idea_008, idea_020]
tags: [ceiling, algebraic, construction, boundary]
---

Exhaustive search across all algebraic construction types (Singer/projective plane,
Bose-Chowla/affine plane) and all prime powers q ≤ 109, with exhaustive multiplier
search for each, confirms that **105 marks is the maximum achievable by known algebraic
constructions for N=10000**.

**Evidence**:
- Best 105: Bose-Chowla q=107, mul=433, span=9884 (fits)
- Best 104: Singer q=103, mul=400, span=9581 (fits)
- Best 106: Singer q=107, mul=best, span=10135 (DOES NOT FIT, 135 over)
- Tested: pp q=107 (9072 multipliers), ap q=107 (~5700), pp q=109 (~990

[TRUNCATED — read full file for details]


### [confirmed] pattern_013

---
type: pattern
id: pattern_013
name: "Beam search greedy ceiling at 70"
lifecycle: confirmed
confidence: 0.85
first_seen: generation_5
last_updated: generation_5
evidence: [gen005_explore_1_sol01, gen005_explore_1_sol02, gen005_explore_1_sol03, gen005_explore_1_sol04, gen005_explore_1_sol05, gen005_explore_1_sol06, gen005_explore_1_sol07]
related_ideas: [idea_021, idea_015, idea_016, idea_003]
tags: [beam-search, greedy, ceiling, non-algebraic]
---

Beam search with greedy candidate selection reaches exactly 70 elements for N=10000,
one more than standard greedy variants (69). The beam width saturates at k=500 — going
to k=800 produces identical results.

**Updated non-algebraic greedy hierarchy** (extends pattern_011):
- Random greedy: 58-63
- Standard greedy: 66
- LNS from greedy: 67
- SA from greedy: 68
- Fibonacci ordering: 69
- Min-blocking greedy: 69
- **Beam search k=500+: 70** (NEW)
- ET(71) + greedy + 1-opt: 75 (still best non-Singer)

**Key insight**: Diverse candidate sam

[TRUNCATED — read full file for details]


### [confirmed] pattern_014

---
type: pattern
id: pattern_014
name: "105-mark Bose-Chowla set has perfect self-healing property"
lifecycle: confirmed
confidence: 0.95
first_seen: generation_6
last_updated: generation_6
evidence: [gen006_exploit_1_sol01]
related_ideas: [idea_022, idea_020, idea_012]
tags: [perturbation, self-healing, algebraic, structural, bose-chowla]
---

The 105-mark Bose-Chowla set (ap q=107, mul=433, span=9884) exhibits a perfect
self-healing property under perturbation: removing any k elements (tested k=1-104)
opens exactly k addable slots, and those slots are always the original removed elements.

**Evidence (exploit_1, 27,000+ trials):**
- k=2-10, ordered greedy extension (18K+ trials): ALL return exactly 105
- k=2-10, shuffled greedy extension (8K+ trials): ALL return exactly 105
- k=15-40: always 105
- k=50-104: degrades (base too small for full recovery)
- Remove-1 add-2 exhaustive search (all 105 elements): each removal opens exactly 1 slot; 0 candidate pairs exist
- Swap walk explorat

[TRUNCATED — read full file for details]


### [confirmed] pattern_015

---
type: pattern
id: pattern_015
name: "ET(71)+1-opt ceiling at 75 is a hard structural barrier"
lifecycle: confirmed
confidence: 0.90
first_seen: generation_6
last_updated: generation_6
evidence: [gen006_explore_1_sol02, gen006_explore_1_sol03, gen006_explore_1_sol04, gen002_explore_1_sol03, gen002_explore_1_sol04]
related_ideas: [idea_011, idea_009, idea_002]
tags: [erdos-turan, local-search, ceiling, non-algebraic]
---

The ET(71) + greedy extension + 1-opt pipeline reliably converges to exactly 75 elements
for N=10000, and this ceiling is resistant to all tested escape strategies.

**Gen 6 evidence (30+ independent trials):**
- 2-opt on 75-element set: no improvement (sol02, timed out after partial search)
- LNS with k=2-15 random element removal + re-extend + 1-opt: always 75 (sol03)
- Randomized greedy from diverse starts (ET base, shuffled, ET-perturbed) + 1-opt: always 75 (sol04)

**Cross-generation evidence:**
- Gen 2: ET(71)+1-opt = 75 (first discovery)
- Gen 6: Confirmed ac

[TRUNCATED — read full file for details]
