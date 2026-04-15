# Agent Brief — explore_2 — Generation 1

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
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/helpers/compat.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/helpers/core.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/constraints.md`

## Directive

**This is a Track B radical exploration. You MUST NOT use the AGL(1,8) algebraic group
structure. You MUST NOT import or use `helpers/agl18.py`. Start entirely from scratch using
combinatorial and stochastic methods on the raw permutation space.**

The AGL(1,8) orbit method is being covered by other agents. Your job is to find out whether
**non-algebraic approaches** can compete with or surpass 616 codewords. This is critical for
the system's diversity — if AGL plateaus, we need alternatives.

**Approach: Iterated Large Neighborhood Search (ILNS)**

The core idea: build a valid code greedily, then iteratively destroy-and-repair large chunks
to escape local optima.

```python
import numpy as np
from itertools import permutations as iperms
from helpers.compat import build_all_perms, build_bucket_ids, fast_compatible_mask

# Setup (do once)
all_perms = build_all_perms(8)   # (40320, 8)
N = len(all_perms)
bucket_ids = build_bucket_ids(all_perms)  # ~0.4s

# Build index map for fast lookup
perm_to_idx = {tuple(p.tolist()): i for i, p in enumerate(all_perms)}
```

**Step 1 — Greedy construction (different starting point each restart):**
```python
def greedy_build(start_idx, all_perms, bucket_ids):
    # Start from permutation at start_idx, greedily add compatible ones
    code_indices = [start_idx]
    remaining = np.ones(len(all_perms), dtype=bool)
    remaining[start_idx] = False
    
    while True:
        mask = fast_compatible_mask(np.array(code_indices), bucket_ids)
        mask[code_indices] = False
        candidates = np.where(mask)[0]
        if len(candidates) == 0:
            break
        # Pick highest-index (or random) candidate
        next_idx = candidates[np.random.randint(len(candidates))]
        code_indices.append(next_idx)
    return code_indices
```

**Step 2 — ILNS loop:**
```python
best_code = greedy_build(0, all_perms, bucket_ids)

for iteration in range(500):
    # Destroy: remove a random 20-40% of codewords
    k = max(1, len(best_code) // 4)
    remove_set = set(np.random.choice(len(best_code), k, replace=False))
    surviving = [c for i, c in enumerate(best_code) if i not in remove_set]
    
    # Repair: greedily rebuild from surviving core
    # Re-run greedy extension from surviving codewords
    remaining_mask = fast_compatible_mask(np.array(surviving), bucket_ids)
    remaining_mask[surviving] = False
    candidates = np.where(remaining_mask)[0]
    np.random.shuffle(candidates)
    
    new_code = list(surviving)
    for cand in candidates:
        test_code = new_code + [cand]
        mask = fast_compatible_mask(np.array([cand]), bucket_ids)
        # Check compatibility (just the new cand against existing)
        dists = np.sum(all_perms[cand] != all_perms[new_code], axis=1)
        if np.all(dists >= 5):
            new_code.append(cand)
    
    if len(new_code) > len(best_code):
        best_code = new_code
        print(f"Iter {iteration}: new best = {len(best_code)}")
```

**Step 3 — Multiple restarts:**
Try 10+ random starting permutations. Each restart runs the full ILNS loop. Keep the best
code found across all restarts.

**Step 4 — Intensification:**
Take the best code found and apply 1-opt improvement:
- For each codeword c in the code, check if removing c and replacing with 2 compatible perms
  yields a net gain of +1.
- This is expensive but worth trying on the final best code.

**Output:**
- `output/sol01.py`: your best ILNS code (target: as close to 616 as possible, minimum 400+)
- `output/sol02.py`: intensification-improved version (if it improves)

Evaluate each immediately after writing. Write `output/report.md` documenting:
- Best sizes found at each stage (greedy vs ILNS vs intensification)
- How many restarts you tried and best vs average
- Whether ILNS can approach the 616 algebraic bound without group structure
- What you'd try next to improve (VNS? larger neighborhoods? SA?)
