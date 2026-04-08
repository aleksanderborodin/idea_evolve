# Experimentator 1 — Generation 6 Debrief

## 1. What did I try?

**Task:** Create two shared helper modules for the pipeline.

**Helper 1: `output/helpers/rokicki_data.py`**
- Stored BEST_105, BEST_104, BEST_102 as Python literals
- Read actual solution files to get exact integer lists (population/top/rank03_104.py → gen005/experimentator_1/sol02.py, rank06_102.py → gen003/exploit_1/sol01.py)
- Validated all three sets with `is_sidon()` — all pass

**Helper 2: `output/helpers/extend.py`**
- Implemented `greedy_extend`, `count_addable`, `random_perturbation`, `blocking_power`
- All functions use Python sets for O(k) per-candidate difference checks
- Ran all four validation tests — all pass

**Interesting discovery:** `blocking_power(BEST_105)` shows element 4662 blocks 7851 candidates.
This is useful metadata for perturbation strategies — exploit agents should target high-blockers.

## 2. What information did I lack?

- Sets of other sizes (103, 106, 107+). The brief says to store BEST_102/104/105, but agents
  working near the boundary (105→106) would benefit from knowing if 106-element sets exist in
  the database or are conjectured. A `BEST_KNOWN` dict keyed by size would be more extensible.
- Whether BEST_102 in gen003/exploit_1/sol01.py is actually from the Rokicki database or a
  computed result. It looks like the base Singer q=101 set (not an optimized construction).
  The 102 count matches Singer q=101 (q²+q+1 = 10303 elements in GF(q³), select q+1 = 102).

## 3. What given facts might be wrong or outdated?

- The BEST_102 set in the codebase (gen003/exploit_1/sol01.py) has `# fitness: TBD` —
  it was never evaluated. I stored it as BEST_102 but I cannot confirm it achieves score 102
  from the evaluate.py scoring. The `is_sidon()` check confirms it's a valid 102-element set,
  but its "rank" as the best 102-element set is unverified. Users should not assume BEST_102
  is the Rokicki database entry — it's likely the Singer q=101 base construction.

## 4. Was the State of Affairs accurate?

I did not read the full State of Affairs (the brief directed me primarily to helper creation).
The brief itself was accurate — the helper need was real, and the solutions referenced existed
where expected.

## 5. What would I do differently with more or different context?

- Download the actual Rokicki database entry for score-102 to verify BEST_102 is optimal
  (or find that a better 102-element set exists within span 10000)
- Add BEST_103 if it exists in the database
- Add a `load_from_database()` function that could fetch newer entries from cube20.org

## 6. Specific experiments to run?

1. **Greedy scan order experiment:** Does scanning in random order vs. 0..N order affect the
   size of the greedy extension? Hypothesis: random order finds same or slightly worse result
   on average. Could be tested by running 1000 random scans and comparing to deterministic.

2. **Perturbation k vs. recovery rate:** For `random_perturbation(BEST_105, k)`, what k value
   maximizes the probability of recovering 105+ elements? Based on gen 3-5 experience, k=3-5
   seems to preserve length but rarely improves it.

3. **Blocking power distribution:** Is the blocking power distribution skewed (power law) or
   roughly uniform? If skewed, targeted removal of top-k blockers is a strong strategy.
   Preliminary result: element 4662 blocks 7851/~9895 candidates (79% of non-members) —
   suggests highly skewed distribution.

## 7. What surprised me?

- `greedy_extend(BEST_105[:100])` recovers the full 105-element set exactly. This means
  the last 5 elements of BEST_105 are "forced" by the greedy scan — the greedy order
  uniquely determines the extension from any 100-element sub-prefix. This suggests BEST_105
  may not be "improvable" by greedy extension from subsets — the greedy algorithm is
  maximally extractive from this starting point.

- Element 4662 blocks 7851 candidates — this is 79% of all ~9895 non-member positions.
  The blocking power is extraordinarily concentrated in a small number of elements.

## 8. Helper tools feedback

**Used:** `helpers/core.py` — `is_sidon()` was essential for validation. Correct and useful.

**Wished existed:** Exactly what I just built! `greedy_extend` and `blocking_power` were
both reimplemented from scratch in gen003/exploit_1/sol01.py and likely in other agents too.

**Note on `is_sidon` performance:** It's O(k²) per call where k is set size. For k=105,
that's ~5460 sum checks — fast enough for validation but not for high-frequency use in
optimization loops. A difference-set based check (O(k²) precompute, O(k) per new element)
as used in `extend.py` is better for iterative extension.

## 9. Time budget

Task completed efficiently. Both helpers created, validated, and documented.

If I had more time:
1. Run the blocking power distribution analysis to characterize skewness
2. Add BEST_103 (fetch from cube20.org if accessible)
3. Add a `perturb_and_extend_best` convenience function that wraps random_perturbation
   with multiple trials and returns the best result — used by every exploit agent
4. Add `targeted_perturbation(S, k, N)` that removes the top-k blockers rather than random k
