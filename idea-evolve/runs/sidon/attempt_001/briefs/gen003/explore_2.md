## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py` -> fitness = 102 (Singer q=101 truncation)
All top-10 solutions score 102. Target: 109.

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/history/coverage_matrix.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/description.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/helpers/core.py`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/helpers/search.py`

## Directive

**This is a Track B radical exploration. You must NOT start from the current 102-element Singer set or any Singer construction. Build from scratch.**

Your goal: attack the Sidon set problem using computational search with intelligent heuristics -- NOT algebraic constructions.

**Your specific approach: Backtracking search with constraint propagation.**

The Sidon property is a constraint satisfaction problem. Every pair of elements (a,b) produces a sum a+b that must be unique. This is similar to N-queens or graph coloring -- problems where backtracking with pruning is highly effective.

**Implementation plan:**

1. **Formulate as a tree search.** Each level adds one element to the Sidon set. At each level, the "domain" is all elements in {0,...,10000} that don't violate the Sidon property with existing elements.

2. **Pruning via difference tracking.** Maintain a set of used differences. A candidate c can be added iff abs(c - x) is not in used_diffs for all x in the current set. This is O(|S|) per candidate check.

3. **Variable ordering heuristic.** Don't add elements in order 0,1,2,... Instead, pick the candidate that leaves the MOST remaining candidates (most-constrained-first or least-constraining-value). This dramatically reduces the search tree.

4. **Iterative deepening.** First search for a set of size 90. Then 95. Then 100. Then 103. Increasing the target prunes the tree more aggressively.

5. **Randomized restarts.** Use random tiebreaking in the variable ordering. Run 100+ restarts, each with different random seeds.

6. **Beam search variant.** If full backtracking is too slow, keep the top-B partial solutions at each level and expand only those.

**Alternative: Stochastic local search (non-SA).**
- Tabu search: maintain a tabu list of recently removed elements, preventing cycling.
- Late acceptance hill climbing: accept moves if they improve on the solution from k steps ago.
- These are different from SA (which is proven useless here due to the 40+ blocker landscape).

**Rules:**
- Do NOT read or use `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py` or any file in `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/top/`.
- Do NOT implement any Singer/algebraic construction.
- Evaluate EVERY solution: `python3 evaluate.py output/solNN.py`
- Write at least 3 solutions with different search strategies.

**Why this might work:** SA failed because the 102-element Singer set has 40+ blockers per candidate. But that's a property of the SINGER set's structure. A set discovered by search may have a completely different blocker profile -- fewer, sparser blockers that allow further extension. The Singer set is optimal among CYCLIC difference sets but not necessarily among all Sidon sets.

## Dead Ends -- Do NOT Investigate
- Singer constructions of any kind
- SA from any existing solution (proven useless)
- Plain greedy (ceiling 66-75)
- Erdos-Turan (ceiling 75)
