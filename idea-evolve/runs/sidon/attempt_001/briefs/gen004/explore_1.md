## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py` → fitness = 102 (Singer q=101 truncation)
Second best: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/top/rank02_69.py` → fitness = 69 (Fibonacci ordering greedy)
Non-algebraic ceiling: 69.

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/ideas/active/idea_016.md` (min-blocking greedy — broken implementation, you will fix it)
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/ideas/active/idea_003.md` (difference-aware construction)
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/ideas/active/idea_005.md` (backtracking with pruning)
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/clusters/cluster_002.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/history/coverage_matrix.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/description.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/helpers/core.py` (has `is_sidon`, `can_add`, `count_violations`, `differences`)

## Dead Ends — DO NOT pursue these
- Singer perturbation (any k): proven futile, 45+ minimum blockers. Don't touch Singer sets.
- SA from any seed: zero improvement in all trials across 3 generations.
- Randomized greedy restarts: ceiling 63, worse than deterministic (66).
- Standard ascending greedy: ceiling 66, well-established.
- Fibonacci ordering greedy: ceiling 69 after 2400+ parameter search. Saturated.

## CRITICAL: Stale fact files warning
`/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/facts/fact_002.md` says upper bound is "~100-102" — WRONG. Correct: ~109.
`/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/facts/fact_004.md` says validator extracts valid subsets — WRONG. Sentinel scoring, 0 for invalid.
Ignore these files.

## Directive

**Correct implementation of min-blocking greedy (idea_016) + backtracking variants (idea_005).**

The min-blocking greedy concept was tested in gen 3 (explore_1/sol02) but the implementation was critically broken — it did NOT verify the Sidon property when adding elements. Result: 775 elements with 280,849 violations → fitness 0. The concept is untested with a correct implementation.

### Approach 1: Min-Blocking Greedy (correct)

At each greedy step:
1. Compute the set of VALID candidates: elements c where `can_add(S_sorted, used_diffs, c)` returns True.
2. For each valid candidate, compute its "blocking score": how many OTHER current valid candidates would become invalid if c were added.
3. Pick the candidate with the LOWEST blocking score (breaks ties by smallest value).
4. Add it, update used_diffs.

**CRITICAL**: Every candidate MUST pass `can_add()` (or equivalent Sidon check using a maintained `used_diffs` set) BEFORE being considered. The gen 3 bug was skipping this check.

**Performance**: The naive implementation is O(N² * |S|) total. Use a numpy-vectorized approach:
- Maintain `used_diffs` as a boolean array of size N+1
- For candidate c, new diffs are `abs(c - s)` for all s in S. Check none are in used_diffs.
- Blocking score: for each valid candidate c, count how many other valid candidates c' have `abs(c - c')` NOT in used_diffs (but WOULD be in used_diffs after adding c).

Test at N=1000 first (should run in <10 seconds). If the concept works (beats 69), scale to N=10000.

### Approach 2: Backtracking with beam search

Pure backtracking on N=10000 is infeasible. But a beam search variant could work:
1. Maintain a beam of k partial solutions (k=50-100).
2. At each step, for each partial solution, try adding the top-m lowest-blocking candidates.
3. Keep the best k solutions (by size + heuristic remaining potential).
4. Prune beams where remaining potential < current best.

This is idea_005 adapted for practical computation. Target: 70-80 elements.

### Approach 3: Hybrid — greedy seed + systematic improvement

1. Build a min-blocking greedy set (approach 1).
2. Try removing each element one at a time, re-running min-blocking greedy from the reduced set. Accept if net gain > 0.
3. Repeat until no single-removal improves.

### Execution order
1. Implement approach 1 at N=1000. Verify it produces a valid Sidon set.
2. Scale to N=10000. Record score.
3. If score > 69, try approach 3 to improve further.
4. If time remains, try approach 2.

Run `python3 evaluate.py output/sol01.py` after EACH solution. Verify the `.score` file exists and shows a valid score before moving on.
