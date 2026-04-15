# Agent Brief — explore_1 — Generation 1

## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/permcodes/attempt_002/population/gen000/baseline/sol01.py` → fitness = 262 (greedy baseline)
No top-ranked solutions yet beyond the greedy baseline.

## Context
This is Generation 1, cold start. No clusters, no knowledge base yet.

**Problem:** Maximize M(8,5) — the largest permutation code on {0,...,7} with all pairwise
Hamming distances ≥ 5. Known bounds: 616 ≤ M(8,5) ≤ 926. Target: 624.

**Evaluate solutions with:**
```bash
python3 /home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/evaluate.py output/sol01.py
```
Verify the `.score` file is created and `fitness` > 0 before writing your next solution.

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/description.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/helpers/README.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/helpers/agl18.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/helpers/compat.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/helpers/core.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/constraints.md`

## Directive

**Your task: push the AGL(1,8) clique construction beyond 616 by exhaustive orbit-level search
and mixed individual-permutation extension.**

The AGL(1,8) orbit clique approach works as follows:
1. Partition all 40320 permutations into 720 orbits under AGL(1,8) (56 perms each)
2. Build a compatibility graph on these 720 orbits
3. Find a maximum clique in this graph → each clique orbit contributes 56 codewords

The standard greedy search (50 starting vertices) typically finds an 11-orbit clique → 616.
But the 720-orbit graph has degree 138 per vertex — there may be larger cliques.

**Strategy 1 — Exhaustive orbit clique search:**

Use `helpers/agl18.py` (`agl18_orbits`, `agl18_compat_graph`) to build the orbit graph, then
search more aggressively than the default 50 starting vertices:

```python
from helpers.agl18 import agl18_orbits, agl18_compat_graph
import numpy as np

orbits = agl18_orbits()   # ~1s
compat = agl18_compat_graph()   # ~4s — build once, search many times
n_orbits = len(orbits)  # 720

# Try ALL 720 starting vertices instead of 50
best_clique = []
for sv in range(n_orbits):
    clique = [sv]
    cands = list(np.where(compat[sv])[0])
    while cands:
        # degree-ordered greedy
        scored = [(c, sum(compat[c, c2] for c2 in cands)) for c in cands]
        scored.sort(key=lambda x: -x[1])
        v = scored[0][0]
        clique.append(v)
        cands = [c for c in cands if compat[v, c]]
    if len(clique) > len(best_clique):
        best_clique = clique
        print(f"New best clique: {len(best_clique)} orbits → {len(best_clique)*56} codewords")
```

Note: scanning all 720 starting vertices takes ~720 * (degree^2 / 2) ≈ minutes. Time-box to
30 minutes. If it finishes, you have the best greedy orbit clique.

**Strategy 2 — Randomized clique improvement:**

Start from the 11-orbit 616-clique. Apply perturbation:
1. Remove 1-3 orbits from the current clique
2. Re-run greedy extension from the remaining orbits
3. If you find a larger clique, keep it

Try 500+ perturbation rounds.

**Strategy 3 — Mixed individual extension:**

After finding the best orbit clique (say K orbits × 56 = K×56 codewords), search for
individual permutations NOT in any of those orbits that are still compatible with all
K×56 codewords using `fast_compatible_mask`. Even adding 1-55 individual perms beats the
pure orbit construction.

Write your best solutions:
- `output/sol01.py`: orbit-clique best (should be ≥ 616)
- `output/sol02.py`: mixed individual extension best (should be > sol01)

Evaluate each immediately after writing. Write `output/report.md` with:
- Best code sizes found at each stage
- Whether any orbit cliques larger than 11 were found
- How many individual extensions were possible beyond the orbit clique
