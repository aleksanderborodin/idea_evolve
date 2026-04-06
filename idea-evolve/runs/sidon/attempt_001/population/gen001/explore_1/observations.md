# Observations — Explore Agent 1, Generation 1

## Approaches Tried

### sol01 — Singer Difference Set (q=97), fitness=98
**Construction:** Singer (v, q+1, 1)-difference set in Z_v for prime q=97, v=q²+q+1=9507.

Key insight: Let g=(5,1,0) be a primitive element of GF(97³)=GF(97)[x]/(x³+2).
The Singer set D = {k ∈ [0,9506] : g^k has zero 3rd component (i.e., lies in GF(97)²×{0})}.
This gives exactly q+1=98 elements forming a perfect (9507,98,1)-difference set:
every difference 1..9506 appears exactly once among all pairs. This is a valid Sidon set.

**Score: 98** — exactly meets the target. Elements in [0,9506] ⊆ [0,10000].

**Key debugging note:** My first attempt used alpha=g^96 (order-9507 element) instead of the
primitive element g. That gave 84 elements with violations. The correct construction uses the
PRIMITIVE element g and indexes k ∈ [0,v-1], NOT a subgroup element.

**Why it works as Sidon:** A (v,k,1)-difference set has every non-zero element of Z_v as
a difference exactly once. Since elements are in [0,v-1], integer differences equal modular
differences → all pairwise differences distinct → Sidon set.

### sol02 — Singer + Perturbation Search, fitness=99
**Construction:** Start from 98-element Singer set. Remove 1-3 elements, shuffle remaining
non-Singer candidates [0,10000], greedily extend. Accept if net size improves.

**Key insight:** The Singer set is "saturated" in Z_9507 (all diffs 1..9506 used), so no
element can be added directly. But removing 1-2 Singer elements frees up differences,
allowing 2-3 new elements from outside [0,9506] to be added for a net gain of 1.

**Score: 99** — 1 better than the Singer baseline. Achieved in 55 seconds.

### sol03 — Larger Perturbations, fitness=99
**Construction:** Same strategy as sol02 but removes up to 15 elements and samples more trials.

**Score: 99** — Same result as sol02 despite more search. The 100-element barrier appears
hard with this approach. 115 seconds of search didn't help.

### sol04 — Targeted 99→100 Push, fitness=99
**Construction:** Two phases:
1. Quickly find the 99-element set (replicate sol02)
2. For each candidate x not in the 99-set, find which elements of the 99-set block it,
   remove those blockers, and greedily rebuild trying to include x plus fill back.

**Score: 99** — Still 99. The 100-element barrier is robust.

## What I Learned

1. **Singer difference set is the key algebraic construction.** For q=97, it gives 98 elements
   in [0,9506] — nearly optimal for N=10000. The construction is clean and fast (< 1 second).

2. **Singer set is saturated.** Every difference 1..9506 is used exactly once. No element can
   be added to the Singer set without creating a conflict.

3. **99 is achievable** by removing 1-2 Singer elements and adding 2-3 new ones. Multiple
   independent runs all found 99.

4. **100 is hard.** The theoretical upper bound is ~100-102 for N=10000. Getting from 99 to 100
   requires a fundamentally better construction, not just more local search iterations.

5. **The wrong Singer element (alpha=g^96 not g)** gave 84 elements with violations.
   The critical insight: use the PRIMITIVE element g (order q³-1) and index first v=q²+q+1
   powers, NOT a subgroup element of order v.

6. **Evaluation semantics:** validate.py returns fitness=0 for ANY violations (sentinel score),
   even if the violations are few. Must produce a perfectly valid Sidon set.

## What Might Work for 100+

- **Singer set for prime q where v=q²+q+1 is slightly larger than 10000**: Would give 100+
  elements but max element might exceed 10000. For q=99 (not prime), q=101 (prime): v=10303>10000.
  Could scale/truncate but likely creates violations.
- **Weil/character sum constructions** from analytic number theory might give denser sets.
- **Backtracking search** with better pruning, starting from the 99-element set.
- **Computer search using ILP or SAT solvers** which can find 99-105 element sets for N=10000
  (known in the literature — optimal or near-optimal solutions exist but require dedicated search).

## Hypotheses for Future Agents

1. The perturbation approach (Singer + local search) converges quickly to 99 and gets stuck.
   A qualitatively different move (e.g., remove 10+ elements and rebuild with simulated annealing)
   might escape the local optimum.
2. The 99-element set found by sol02 might itself be extendable if we understand its structure —
   which differences are NOT used (the "slack") and which candidates can exploit that slack.
3. Known optimal Sidon sets for N=10000 in the literature might exist; a research agent
   could find explicit constructions achieving 100.
