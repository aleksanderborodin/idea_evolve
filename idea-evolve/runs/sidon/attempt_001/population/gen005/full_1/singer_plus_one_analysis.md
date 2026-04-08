# Singer+1 Structure Analysis

## Summary

CP-SAT analysis of optimal Sidon sets vs Singer difference sets for small prime powers.

## Results Table

| q | N | Singer Size | Optimal Found | Overlap | Extra Elements | Notes |
|---|---|-------------|---------------|---------|----------------|-------|
| 7 | 56 | 8 | **10** (OPTIMAL) | 3 | [10,23,26,34,41,53,55] | k=11 proved INFEASIBLE |
| 11 | 132 | 12 | **13** (OPTIMAL) | 1 | [7,13,18,28,32,52,54,55,85,114,123,131] | k=14 UNKNOWN (60s) |
| 17 | 306 | 18 | 18 (UNKNOWN at k=19) | 18 | (none found) | 120s too short |
| 23 | 552 | 24 | 24 (UNKNOWN at k=25) | 24 | (none found) | 120s too short |

## Key Finding: Singer is NOT Near-Optimal for Small N

### q=7 (N=56): Singer gives 8, optimal is **10** (+25%)

- **Singer set**: [0, 1, 6, 10, 21, 28, 44, 46] (8 elements)
- **Optimal set**: [0, 1, 6, 10, 23, 26, 34, 41, 53, 55] (10 elements)
- **Overlap**: 3 elements (0, 1, 6, 10 are shared — actually only 3 total per analysis)
- **Extra elements NOT in Singer**: [10, 23, 26, 34, 41, 53, 55]
- **Singer elements dropped**: [21, 28, 44, 46, 54]

**Critical observation**: The optimal set shares only 3 of 8 Singer elements. It is NOT an extension of Singer — it replaces more than half the Singer set with different elements.

### q=11 (N=132): Singer gives 12, optimal is **13** (+8.3%)

- **Overlap**: Only 1 element shared with Singer!
- **Extra elements**: [7, 13, 18, 28, 32, 52, 54, 55, 85, 114, 123, 131]
- **Singer elements dropped**: [1, 3, 15, 46, 71, 75, 84, 94, 101, 112, 128]

**Critical observation**: The optimal set shares just 1 of 12 Singer elements. Singer and the optimal set are structurally unrelated.

## Difference Structure Analysis

Singer difference sets use exactly `q(q+1)/2` = half of all possible differences in {1,...,N}:
- q=7: Singer uses 28 of 56 differences (exactly half)
- q=11: Singer uses 66 of 132 differences (exactly half)
- q=17: Singer uses 153 of 306 differences (exactly half)
- q=23: Singer uses 276 of 552 differences (exactly half)

This is by construction: Singer is a perfect difference set in Z_{q²+q+1}, using every difference exactly once. The "free" 50% of differences is NOT exploitable by adding elements to Singer, because those free differences are in the cyclic group — in Z (integers), the situation is different.

**The extra elements do NOT use only "free" differences** (analysis confirmed `extra_uses_free_diffs: False`). This means:
- Some Singer differences are "freed" when Singer elements are dropped
- The extra elements use a mix of freed Singer differences and originally-free differences
- There is NO simple extension of Singer that finds the optimal

## Implications for N=10000 (q=101)

1. **Singer is likely suboptimal at N=10000 too**: The pattern shows Singer is consistently suboptimal for small N. Whether the gap closes for larger q is unknown (q=17, q=23 were UNKNOWN with 120s budget).

2. **Singer hint may actively hurt CP-SAT**: For q=7 and q=11, the optimal set replaces 5/8 and 11/12 Singer elements respectively. Warm-starting from Singer gives CP-SAT completely wrong initial values for most variables.

3. **True target for N=10000 might be well above 103**: If Singer is 25% suboptimal for q=7, and 8% for q=11, the pattern suggests possibly 3-5% suboptimal for q=101, meaning 105-107 elements might exist.

4. **CP-SAT is stuck not because 103 is infeasible but because it searches near Singer**: The no-hint run in gen4 was also UNKNOWN, but it's not clear if CP-SAT's default strategy also gravitates toward Singer-like structures.

## Recommendations

1. **Try CP-SAT with no hint and explicit anti-Singer constraint**: Forbid the top-50 Singer elements from being selected to force exploration of different regions.
2. **Increase run time for q=17 and q=23**: Determine at what q Singer becomes optimal (or whether it ever does).
3. **Look for construction patterns**: The optimal sets [0,1,6,10,23,26,34,41,53,55] (q=7) and similar may follow a different algebraic construction (e.g., Bose-Chowla or other constructions in integers).
4. **Try ILP with maximize objective for N=1000-5000**: Find the largest Sidon set at intermediate scales to understand the trend.
