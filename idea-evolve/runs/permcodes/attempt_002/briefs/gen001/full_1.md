# Agent Brief — full_1 — Generation 1

## Current Population Status
Best solution: `population/gen000/baseline/sol01.py` → fitness = 262 (greedy baseline)
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
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/helpers/core.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/helpers/agl18.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/helpers/compat.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/constraints.md`

## Directive

Build a complete, reliable solution that reaches **at least 616 codewords**, then attempts
to push beyond.

**Phase 1 — Reach 616 using AGL(1,8):**

The `helpers/agl18.py` module provides `agl18_max_clique_code()` which uses the AGL(1,8)
group orbit structure to find a maximum clique in the orbit compatibility graph. Call it
directly:

```python
from helpers.agl18 import agl18_max_clique_code
code = agl18_max_clique_code(d=5)  # returns shape (616, 8)
```

Write this as `sol01.py`, evaluate it, confirm fitness = 616.

**Phase 2 — Attempt extension beyond 616:**

After confirming 616, try to extend the code by searching for permutations outside the AGL
clique that are still compatible with all 616 codewords:

```python
from helpers.compat import build_all_perms, build_bucket_ids, fast_compatible_mask
import numpy as np

all_perms = build_all_perms(8)
bucket_ids = build_bucket_ids(all_perms)

# Get indices of current 616 codewords in all_perms
code_set = set(map(tuple, code.tolist()))
code_indices = np.array([i for i, p in enumerate(all_perms) if tuple(p.tolist()) in code_set])

# Find compatible extensions
compat_mask = fast_compatible_mask(code_indices, bucket_ids)
# Remove existing codewords from candidates
compat_mask[code_indices] = False
extension_candidates = all_perms[compat_mask]
```

If `extension_candidates` is non-empty, greedily add them one by one (after each addition,
rebuild `code_indices` and re-run `fast_compatible_mask`). Even adding 1 permutation (→ 617)
is a new record.

If the 616-code is maximal (no extensions exist), try:
- Run `agl18_max_clique_code()` multiple times with different seeds (it uses greedy with
  randomized starting vertex order) — sometimes finds 11+ orbit cliques
- Try expanding the orbit search beyond 50 starting vertices

**Phase 3 — Simulated annealing (if time permits):**

After stabilizing the best code found, try a brief SA phase:
- Accept the current K-code
- Randomly swap out 1-5 codewords for alternatives from compatible_candidates
- If the swap maintains validity AND opens up room for more additions → accept
- Repeat for 1000-5000 iterations

**Output format:**
```python
def entrypoint() -> np.ndarray:
    # returns np.ndarray of shape (K, 8), dtype int
```

Write your best solutions as `output/sol01.py` (baseline 616), `output/sol02.py` (best
extension attempt). Evaluate each one immediately after writing. Report in `output/report.md`
what you found and what code sizes you achieved.
