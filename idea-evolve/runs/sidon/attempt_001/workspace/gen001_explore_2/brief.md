## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/gen000/baseline/sol01.py` → fitness = 66
No other solutions yet.

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/ideas/active/idea_002.md` — Local search / swap neighborhood idea
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/ideas/active/idea_001.md` — Randomized greedy with restarts idea
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/facts/fact_001.md` — Greedy baseline score
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/facts/fact_002.md` — Theoretical upper bound
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/facts/fact_004.md` — Violation tolerance
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/gen000/baseline/sol01.py` — Baseline greedy (read to understand the problem, then build your own approach)
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/description.md` — Problem definition
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/helpers/core.py` — Available helper functions

## Directive

**Metaheuristic optimization: simulated annealing and local search for Sidon sets.**

Start from a greedy Sidon set and apply metaheuristic optimization to grow it:

1. **Simulated annealing with swap moves:** Start with the greedy set of 66 elements. Define moves:
   - Remove a random element, try adding a different one (swap)
   - Remove an element and try adding two new ones (grow move)
   - Accept worse moves with probability exp(-delta/T) where delta measures set size decrease
   - Cool slowly to allow the set to reorganize and grow

2. **Iterative local search with perturbation:** Run a local search (greedy add/swap) to local optimum. Then perturb by removing k random elements and re-optimizing. Repeat with different perturbation sizes.

3. **Population-based search:** Maintain multiple Sidon sets. Each generation: mutate (random swap), crossover (merge two sets, extract valid subset), select best. This is a simple evolutionary approach within a single agent.

4. **Multi-start with difference-aware greedy:** Instead of always adding the smallest valid element, use heuristics like "add element that blocks fewest future additions" or "add element with rarest differences." Run many random starts with this heuristic.

The key constraint: all pairwise sums must be distinct. Use `from helpers.core import is_sidon, count_violations, can_add` for efficient checking.

Do NOT use algebraic constructions (quadratic residues, Singer sets, etc.) — those are assigned to another agent. Focus on search-based methods that start from an arbitrary set and optimize.

Write solutions to `output/sol01.py`, `output/sol02.py`, etc. Evaluate each immediately after writing. Your report goes to `output/report.md`.
