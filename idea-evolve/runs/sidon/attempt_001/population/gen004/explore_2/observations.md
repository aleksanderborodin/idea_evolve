# Observations — Gen 4 Explore 2

## Summary

Attempted radical exploration away from Singer constructions. Produced one solution (fitness=69).
The brief's listed "Option A–E" directions were explored but many had fundamental issues.

---

## Approaches Tried

### 1. Ruzsa Quadratic Construction (abandoned — not actually Sidon)
**Formula:** `phi(x) = x*p + (x^2 mod p)` for x in {0,...,p-1}

Tested p=97, 101, 103. All produced violations in the integers:
- p=97: 97 elements, 198+7855=8053 == 0+8053 (violation immediately)
- p=101: 99 elements after filter, violation found
- p=103: 97 elements after filter, violation found

**Root cause:** The formula generates a Sidon set in Z_p × Z_p (a product group), but the
embedding into integers via `a*p + b` is NOT a group homomorphism from Z_p × Z_p to Z_{p^2}.
The "carry" between components breaks the Sidon property in the integers.

The correct Ruzsa construction requires a careful embedding that prevents cross-component
interference. This is more complex than the brief suggested.

### 2. CRT (Chinese Remainder Theorem) Product Construction (abandoned — structural violations)
**Approach:** Find Sidon sets S1 in Z_97 and S2 in Z_103 (cyclic groups), combine via CRT.

- S1 size: 8 elements, S2 size: 8 elements
- CRT product size: 64 elements in {0,...,9895}
- Violations: 448 (extremely high)

**Root cause:** The cross-term problem. For any a1≠a2 in S1 and b1≠b2 in S2, the pairs
(a1,b1),(a2,b2) and (a1,b2),(a2,b1) have the same sum in each coordinate, creating a sum
collision in the integers. With |S1|=|S2|=8, there are C(8,2)^2 ≈ 784 such cross-term
violations. CRT of full products is fundamentally NOT Sidon.

### 3. Min-Blocking Greedy (implemented, fitness=69)
**Approach:** At each step, add the element that blocks the fewest remaining candidates.

**Critical bug discovered:** The standard validity check (used_diffs tracking) misses the
"midpoint" case. When S contains elements s1, s2, the midpoint (s1+s2)/2 is also invalid
because |midpoint - s1| = |midpoint - s2| (equal distances). The initial implementation
never blocked midpoints, causing violations.

**Fix applied:** When adding element e to S, additionally block midpoints (e+s)/2 for each
s in S (where integer). This is now correct.

**Performance:** The algorithm is O(N * |used_diffs| * |S|) per step.
- N=500: 20 elements (same as standard greedy), 0.1s
- N=1000: 28 elements (vs 27 standard greedy), 1.0s
- N=2000: 36 elements (vs 35 standard greedy), 4.6s
- N=10000: 69 elements (vs 66 standard greedy), ~20s ✓

**Result:** +3 elements over standard ascending greedy (69 vs 66). Valid Sidon set.

### 4. Ordering variations (tested, all gave 66 or worse)
- Descending order: 66 (same as ascending)
- Middle-out order: 61 (worse)
- Random permutation (500 seeds): best 63

---

## Key Findings

1. **Min-blocking greedy achieves 69** — a legitimate improvement over standard greedy (66),
   confirming the hypothesis that smarter element selection helps.

2. **The midpoint bug in idea_016** was real. The correct fix blocks (e+s)/2 for each s in S
   when adding e. Without this fix, the greedy produces violations.

3. **CRT and Ruzsa approaches from the brief don't work as described.** The brief was
   optimistic — the algebraic constructions don't naturally give Sidon sets in the integers
   without additional care. The brief's Option A and C are mathematically flawed as stated.

4. **Min-blocking is fundamentally limited.** Even with correct implementation, it only
   gives ~5% improvement over standard greedy. The reason: greedy in any ordering tends to
   saturate around 66-69 because the difference space fills up. The first 66 elements cover
   most "useful" differences.

5. **Randomized greedy ceiling is ~63.** 500 random seeds, best was 63. This confirms
   the state of affairs assessment.

---

## What I Wish I Had Time For

1. **Proper Ruzsa construction** — The correct version requires a different embedding. The
   actual Ruzsa-Lindstrom construction uses a polynomial map f: GF(p) → Z with carefully
   chosen spacing. Literature search needed for exact formula.

2. **Beam search greedy** — Keep k=50 best partial Sidon sets at each step. This would
   explore much more of the search space and likely beat 69 significantly.

3. **B-tree / backtracking with pruning** — Systematic search with aggressive pruning.
   Idea_005 lists this as untested. For N=10000 it's computationally challenging but
   worth trying at smaller N for calibration.

4. **Multi-Singer hybrid (idea_013)** — Still untested. Quick to implement.

---

## Stale/Wrong Facts

- fact_002.md: upper bound "~100-102" is WRONG (correct: ~109)
- fact_004.md: "validator extracts valid subsets" is WRONG (sentinel scoring, 0 for invalid)
- Brief's description of Ruzsa and Bose-Chowla constructions is oversimplified and misleading

## State of Affairs Accuracy
Accurate. The coverage map correctly identifies min-blocking greedy (idea_016) as untested
with a correct implementation. The 69 ceiling for Fibonacci greedy matches — min-blocking
achieves the same score (69) via a different path.
