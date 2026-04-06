## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py` → fitness = 102 (Singer q=101 truncation)
The 102-element Singer set is in SINGER_SET in that file.

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/ideas/active/idea_013.md` (Multi-Singer hybrid — untested)
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/feedback/experiment_suggestions/gen003.md` (EXP-4 and EXP-6)
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/helpers/core.py`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/helpers/singer.py`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/helpers/optimal_shift.py`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py` (contains the 102-element set as SINGER_SET)

## Directive

**Two quick computational experiments to resolve open questions and provide structural insight.**

### Experiment 1 (EXP-6): Multi-Singer Hybrid Test

**Question**: Can elements from different algebraic constructions (Singer q=101, ET p=71, Singer q=97) be combined into a Sidon set larger than 102?

**Method**:
1. Load the Singer q=101 set (102 elements) from `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py`.
2. Build the Erdos-Turan set for p=71: S_ET = {(i² + i) mod 71 + 143*k : ...} — approximately 70-75 elements. Use the formula from the literature or from `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/ideas/active/idea_009.md` if needed.
3. Build Singer q=97 set (98 elements) using `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/helpers/singer.py`.
4. For each pair of constructions, compute their pairwise differences and check for conflicts.
5. Try combining: take all 102 Singer q=101 elements, then try adding each ET element one by one (checking Sidon validity). Record how many ET elements can be added.
6. Repeat with Singer q=97 elements instead of ET.
7. Try the reverse: take ET base, add Singer elements one by one.
8. Try taking k elements from Singer q=101 (k=90,80,70,60) and greedily adding elements from ET or Singer q=97.

**Expected result**: Likely zero elements can be added to the full 102-set (consistent with pattern_010: zero addable elements). But reduced bases (k=70-90) might allow additions. Even 1 additional element from a different algebraic family would be a significant finding.

**Success criteria**: If any combination yields >102 elements → major breakthrough. If all combinations fail → idea_013 can be debunked.

**Time budget**: ~15-20 minutes.

### Experiment 2 (EXP-4): Unused Difference Spectrum Analysis

**Question**: What is the algebraic structure of the "free" differences not used by the Singer q=101 set?

**Method**:
1. Load the 102-element Singer set.
2. Compute all C(102,2) = 5151 pairwise differences.
3. Compute the 4849 "free" differences in {1,...,10000} not used.
4. Analyze:
   - Are the free differences clustered or uniformly distributed?
   - Do the free differences form any algebraic pattern (e.g., are they quadratic residues mod some prime)?
   - For each non-member c ∈ {0,...,10000} \ S, how many of the differences {|c-s| : s ∈ S} fall in the free set vs the used set? (This gives the "blocker count" — already known to be ≥45, but the DISTRIBUTION matters.)
   - What is the minimum number of Singer elements you'd need to REMOVE to make at least one non-member addable? (This tests whether "element trading" is possible.)
5. Specifically: find the non-member with the fewest blockers (45). Identify which 45 Singer elements block it. How many Singer elements share blockers? Can removing 2-3 carefully chosen Singer elements free up enough differences to add 3-4 new elements?

**Expected result**: Structural understanding of why 102 is rigid. The trading analysis may reveal whether 103 is mathematically possible via element swaps, even if search hasn't found it.

**Time budget**: ~15-20 minutes.

### Output format
Write results to:
- `output/experiment_results.md` — structured results for both experiments
- `output/report.md` — standard debrief

For each experiment, include: hypothesis, method, raw data, conclusion, implications for future generations.
