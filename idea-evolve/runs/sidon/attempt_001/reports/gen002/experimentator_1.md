# Debrief Report — Experimentator 1, Generation 2

## 1. What did you try?

### Primary task: Build three shared helpers
- **find_singer_set(q)**: GF(q³) construction via irreducible cubic and primitive element search.
  Developed iteratively in sandbox, tested on q=2,3,5,7,97,101. All pass is_sidon verification.
  **Result**: Working, deployed to `output/helpers/singer.py`.

- **greedy_sidon(candidates, N)**: Incremental greedy Sidon set builder with used_diffs tracking.
  Verified: baseline matches 66, Singer sets preserved.
  **Result**: Working, deployed to `output/helpers/search.py`.

- **build_diff_counts(S)**: Pairwise difference counter. Verified against Singer q=97 (4753 diffs,
  all count=1) and manually checked small cases.
  **Result**: Working, deployed to `output/helpers/search.py`.

### Bonus discovery: Singer q=101 cyclic shift search
While running integration tests, discovered that Singer q=101 with shift=3538 places ALL 102
elements within {0..10000}. Wrote sol01.py implementing this — **scored fitness=102**.

## 2. What information did you lack?

Nothing critical. The brief was excellent — it provided the reference implementation (best.py),
exact verification criteria, and deployment paths. The experiment suggestions (EXP-1, EXP-7)
were precisely what was needed.

## 3. What given facts might be wrong or outdated?

- **fact_002** (upper bound ~100-102): State of Affairs notes this is wrong, should be ~109.
  Confirmed — we achieved 102 with a basic construction, so 100-102 is clearly not a ceiling.
- **fact_004** (violations lead to subset extraction): Already flagged as wrong. Violations → 0.

## 4. Was the State of Affairs accurate?

Mostly yes, but the characterization of the "99→100 barrier" was misleading. It framed this
as a hard local search problem requiring sophisticated perturbation or SA. In reality, the
barrier was simply an artifact of using q=97 (which gives only 98 elements). Switching to
q=101 trivially exceeds 100 with the right cyclic shift.

The State of Affairs correctly identified Singer q=101 as the highest priority untested approach.

## 5. What would you do differently with more context?

Nothing — the task was well-defined and the brief had all necessary information.

## 6. Specific experiments to run

1. **Singer q=101 + perturbation**: Start from the 102-element set and try to reach 103-105
   by removing 1-3 elements and greedily extending into {0..10000}. The Singer set covers
   diffs in Z_{10303} but {0..10000} has ~300 more candidate values that may be compatible.

2. **Singer q=103 (next prime)**: 104 elements in Z_{10713}. Only 9347/10713 = 93.4% of Z
   is covered by {0..10000}, so expect ~97 elements. Probably worse than q=101, but worth
   confirming.

3. **Multi-polynomial Singer q=101**: Different primitive polynomials over GF(101) yield
   different Singer sets. Some may have better perturbation properties for going beyond 102.

4. **Combine Singer q=101 shift with greedy extension**: After getting 102 elements via shift,
   check if any elements in {0..10000} not in the set can be added while maintaining Sidon.

## 7. What surprised you?

The biggest surprise: **569 out of 10303 cyclic shifts (5.5%) preserve all 102 elements
of Singer q=101 within {0..10000}.** I expected maybe 1-2 shifts would give 100+, and most
would give 99. Instead, 43.5% of shifts give ≥100 elements. This shows q=101 is almost
perfectly matched to N=10000 — the "overflow" region {10001..10302} contains only 302 values
(2.93% of Z_{10303}), so most shifts avoid it entirely for most elements.

Also surprising: `greedy_sidon(find_singer_set(101))` (without any cyclic shift) gives 100
elements. Even the naive approach of just taking Singer q=101 elements that happen to be ≤10000
gives exactly 100. The cyclic shift search finds 2 more.

## 8. Helper tools feedback

- **Used**: `is_sidon` and `count_violations` from `helpers/core.py` — correct and useful
  for verification. No bugs found.
- **`can_add` from core.py**: Not used directly but verified it works correctly via the
  greedy_sidon implementation (which uses the same logic).
- **Missing helpers I built**: `find_singer_set`, `greedy_sidon`, `build_diff_counts` —
  now deployed in `output/helpers/`.

## 9. Time budget

Had plenty of time. Primary task (build and test 3 helpers) took about 60% of budget.
Used remaining time for the cyclic shift experiment and writing sol01.py (fitness=102).
If I had more time, I would have:
- Tested Singer q=101 + perturbation to see if 103+ is reachable
- Investigated multi-polynomial variants for different q=101 Singer sets
- Written a `find_optimal_shift(q, N)` helper function
