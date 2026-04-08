# Debrief Report — explore_2, gen005

## Solution Summary

| File | Approach | Score | Valid | Violations | Raw Size |
|------|----------|-------|-------|------------|----------|
| sol01.py | Bose-Chowla construction (i*p + i²mod p, p=97) | 0 | No | 312 | 97 |

**No valid solutions produced this session.**

---

## 1. What did I try?

**sol01.py — Bose-Chowla construction:**
The formula S = {i*p + (i² mod p) : i=0,...,p-1} for prime p=97, intended to produce
a 97-element Sidon set with span 9408 that fits in [0,10000]. After a greedy extension
phase it was expected to push past 97 elements. However, the evaluation returned fitness=0
with 312 violations.

Manual debugging confirmed actual violations, e.g.:
- pair (7855, 0) and pair (8053, 198) both have difference 7855.

## 2. What information did I lack?

The correct statement of the Bose-Chowla theorem — specifically that i*p + (i²mod p) is
only proven Sidon for small primes. The actual algebraic construction for large Sidon sets
equivalent to Singer uses the cyclic group Z_{q²+q+1}, NOT the formula I used.

I lacked:
- A lookup table of known valid Sidon constructions beyond Singer
- Confirmation of whether any algebraic Sidon construction exists distinct from Singer for N=10000

## 3. What given facts might be wrong or outdated?

The description mentions "theoretical maximum for N=10,000 is approximately 100 elements"
but the State of Affairs says ~109 (Carter, Hunter, O'Bryant). The description file is stale.

## 4. Was the State of Affairs accurate?

Yes — it correctly identified Singer as the algebraic ceiling (102) and listed computational
search (CP-SAT) and the Rokicki-Dogon database as the only remaining paths forward. My session
confirmed there is no "third algebraic basin" from the naive Bose-Chowla formula.

## 5. What would I do differently with more or different context?

Skip the algebraic construction attempt entirely. The State of Affairs made it clear that
algebraic approaches are exhausted. Instead I should have immediately gone to:
- **Beam search** (width 50-200): maintain top-B partial Sidon sets at each extension step
- **Systematic backtracking** from position 0, pruned by Lindström bound + best_known=102

## 6. Specific experiments to run

**Beam search (highest priority, genuinely unexplored):**
```python
# Maintain beam of B partial solutions
# At each step, extend each solution by trying candidates in order
# Keep top-B by size + tie-breaking heuristic
# Test B=50, 100, 200 with time limit 300s each
```
This has never been tried (state of affairs confirms greedy variants are dead ends but
beam search with width > 1 is unlisted).

**Integer linear programming with warm start:**
The state of affairs says CP-SAT returned UNKNOWN after 600s for k=103. Warm-starting
with the Singer-102 solution and fixing 50-60 variables could dramatically prune the search.

**Rokicki-Dogon database (critical):**
Download the actual mark lists from the Golomb ruler database. The idea_020 entry says a
zip file was found but not downloaded. This is the single highest-value action remaining.

## 7. What surprised me?

The Bose-Chowla construction fails for p=97 with 312 violations. I expected this to be
a valid algebraic construction based on it working for p=5, 7, 11. The failure mode
(Case R=-p in the algebraic analysis) only appears when p is large enough to allow
integer solutions to the modular constraint — a subtle number-theoretic failure.

## 8. Helper tools feedback

Did not use helpers/core.py or helpers/search.py (construction failed before I needed them).

**Wish list:**
- A helper `sidon_upper_bound(N, k_placed, diffs_used)` that computes the Lindström
  upper bound given a partial solution — would enable efficient branch-and-bound.
- A helper `beam_extend(beam, candidates, beam_width)` implementing beam search extension.

## 9. Time budget

Severely insufficient. The algebraic investigation took most of the session, leaving no time
to implement the genuinely novel approaches (beam search, backtracking).

**If given more time:**
1. Implement beam search (width 100) immediately — 50 lines, testable in 10 minutes
2. Test on N=100, N=1000, N=10000 progressively
3. If beam search beats 69: submit; if not, pivot to backtracking
