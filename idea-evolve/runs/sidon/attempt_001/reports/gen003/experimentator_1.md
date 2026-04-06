# Experimentator 1 — Generation 3 Debrief

## 1. What did you try?

### Task 1: `find_optimal_shift` + `analyze_blockers` helpers (PRIMARY)

- Built both functions in `sandbox/scripts/optimal_shift_dev.py`
- Wrote 9 unit tests in `sandbox/scripts/test_optimal_shift.py`
- Tested on q=97 (all 98 fit), q=101 (all 102 fit), q=103 (102 of 104), q=107 (99 of 108), q=109 (99 of 110)
- All tests passed on first run
- Deployed to `output/helpers/optimal_shift.py` with full docstrings and examples

**Result:** Both helpers are correct, tested, and ready for deployment.

### Task 2: Singer gap/shift analysis (EXP-6)

- Computed cyclic gap structure for q=89, 97, 101, 103, 107, 109, 113
- Analyzed shift count distributions (how many shifts preserve k elements)
- Found the geometric explanation for why q=101 is optimal
- Discovered that truncated Singer sets have ZERO addable elements for ALL primes tested

**Result:** Established that 102 is a hard Singer ceiling with a clear geometric explanation.

## 2. What information did I lack?

- **Published Sidon set records for N=10000.** This is still the #1 missing piece. My analysis proves the Singer ceiling is 102, but says nothing about whether non-Singer constructions can exceed it.
- **Other perfect difference set families.** Singer sets come from GF(q³), but there may be other cyclic difference set constructions with different gap properties.

## 3. What given facts might be wrong or outdated?

- **fact_002 and fact_004** — the State of Affairs already flags these as wrong. They should be deleted or corrected.
- The State of Affairs says "40+ minimum blockers" — the actual minimum is **45** (for elements 9843, 9958, 9981). This is a minor understatement but directionally correct.

## 4. Was the State of Affairs accurate?

Mostly yes. The strategic direction (Singer exhausted, need non-Singer approaches) is completely validated by my analysis. The SoA correctly identifies the 102→109 gap as the critical challenge.

One addition needed: the SoA should state the geometric reason WHY 102 is the ceiling (max_gap vs excess argument), not just that it IS the ceiling. This gives future agents better intuition.

## 5. What would I do differently with more context?

- If I knew the published best for F(10000), I could have tailored the analysis to explain the gap between Singer and published best.
- I would have also analyzed the Erdős-Turán construction's gap structure for comparison.

## 6. Specific experiments to run

1. **Multi-Singer hybrid test:** Take 80 elements from Singer q=101 and 22+ elements from a completely different algebraic construction (e.g., ET p=71). Check if the combined set can be Sidon. This tests whether different algebraic structures have compatible difference sets.

2. **Singer q=103 truncation + element swap:** The q=103 truncation loses exactly 2 elements (at positions 10126 and 10549). Remove the 2 closest-to-boundary elements from the truncated 102-set, then check if ANY of the freed differences allow adding 3+ new elements. This is a targeted search, not exhaustive perturbation.

3. **Difference set complement analysis:** For the 102-element set, compute which differences in {1,...,10000} are NOT used. There are C(102,2)=5151 used differences out of 10000 possible. The 4849 unused differences define the "free space" — analyze their structure for algebraic patterns.

## 7. What surprised me?

- **Zero addable elements after truncation for ALL primes.** I expected that q=107 (losing 9 elements and freeing 927 differences) would have at least a few addable elements. The complete saturation even after significant truncation was surprising and suggests the Singer difference structure has a deep rigidity property.

- **q=97 has ALL shifts preserving all elements** (v=9507 < 10001). This was obvious in hindsight but I hadn't considered it before — any Singer prime with v ≤ N+1 trivially fits.

- **The minimum blockers are all near N=10000** (elements 9843, 9958, 9981). This makes sense geometrically — elements far from the dense core of the set have fewer near-differences — but it suggests that extending the range to N=10100 or N=10300 might allow adding 1-2 elements near the boundary.

## 8. Helper tools feedback

- **`helpers/singer.py` (`find_singer_set`):** Correct and useful. ~0.15s for q=101, which is fine. Could be faster with cached polynomial parameters, but not a bottleneck.
- **`helpers/search.py` (`greedy_sidon`):** Did not use directly, but its design informed my `analyze_blockers` implementation.
- **`helpers/core.py` (`is_sidon`):** Used for validation. Correct. O(n²) is fine for n≈100.
- **Wish list:** A `singer_difference_spectrum(q)` function that returns the full set of differences for a Singer set would save agents from recomputing it. Also useful: `count_shifts_by_fitness(q, N)` returning the full distribution.

## 9. Time budget

Had sufficient time to complete both tasks fully. If I had more time, I would have:

1. Run the multi-Singer hybrid test (experiment suggestion #1 above)
2. Analyzed the unused difference spectrum for algebraic structure
3. Tested whether the Erdős-Turán construction has the same zero-addable-element property
4. Computed the exact threshold N* below which q=103 beats q=101 (i.e., for what N does q=103 give 104 elements?)
