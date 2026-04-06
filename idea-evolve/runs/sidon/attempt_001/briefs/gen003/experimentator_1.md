## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py` -> fitness = 102 (Singer q=101 truncation)
Target: 109.

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/helpers/singer.py`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/helpers/search.py`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/helpers/core.py`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/feedback/system_recommendations.md` (see REC-4)
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/feedback/experiment_suggestions/gen002.md` (see EXP-6)

## Directive

**Two tasks:**

### Task 1 (PRIMARY): Build `find_optimal_shift(q, N)` helper

This helper has been requested by 3+ agents across gen 2 (REC-4, appearing for 2nd consecutive generation). Build it.

**Specification:**
```python
def find_optimal_shift(singer_set, v, N=10000):
    """
    Given a Singer set in Z_v, find the cyclic shift d that maximizes
    the number of elements in {0, ..., N}.

    Args:
        singer_set: list of integers in Z_v (the raw Singer set)
        v: the modulus (q^2 + q + 1)
        N: upper bound of target range (default 10000)

    Returns:
        (best_shift, truncated_set) where truncated_set is the sorted list
        of elements in {0, ..., N} after applying the best shift.
    """
```

- Test on q=97, q=101, q=103 using the existing `find_singer_set(q)` from `helpers/singer.py`
- Verify: for q=101, should return 102 elements (all fit in range)
- Deploy to `output/helpers/optimal_shift.py`
- Also add a companion function:
  ```python
  def analyze_blockers(sidon_set, N=10000):
      """For each non-member in {0,...,N}, count how many current members block it."""
  ```

### Task 2 (SECONDARY): Singer set gap/shift analysis (EXP-6)

Analyze the cyclic structure of Singer q=101:
1. Compute the maximum consecutive gap between elements in the Singer set (in Z_10303)
2. For each shift, how many elements fall in {0,...,10000}? Plot the distribution.
3. For q=103 (v=10713): what is the best shift? How many elements fit? Why exactly 102 and not 104?
4. For q=107 (v=11557): same analysis. Why does it drop to 100?

Write findings to `output/report.md` with the analysis results.

**The question:** Is there a mathematical reason why no Singer construction can exceed 102 for N=10000, or is 102 just a coincidence of q=101's specific structure?

## Dead Ends -- Do NOT Investigate
- Building new Singer constructions from scratch (singer.py already works)
- SA or local search (not your task)
- Solution code (focus on helpers and analysis)
