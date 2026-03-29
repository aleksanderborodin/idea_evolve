# explore_1 — Generation 7

## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen006/exploit_1/sol01.py` → C = 1.5028628724712894
Second best: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/top/rank02_1.502863.py` → C = 1.502862898

## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/state_of_affairs.md` — Strategic overview
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/clusters/cluster_001.md` — Optimization algorithms (coordinate descent frontier)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen006/exploit_1/sol01.py` — Best solution to perturb (N=30000)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/compute_c_f64.py` — Float64 C computation
- `/home/sasha/Desktop/project_alpha/alpha-evolve/reports/gen006/exploit_1.md` — Pair-wise perturbation found only 1 improvement

## Directive

**Mission: Triplet perturbation on the TTT-Discover 30k array.**

Pair-wise perturbation (f[i] += d, f[j] -= d) found only 1 improvement in 300 trials (gen 6 exploit_1). The solution is near pair-wise optimal. But coordinated 3-element moves are completely untested. Triplet moves explore a larger perturbation space that pairs cannot reach.

### Implementation plan

1. **Load best solution** from `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen006/exploit_1/sol01.py`.

2. **Implement integral-preserving triplet perturbation:**
   ```python
   import numpy as np
   from helpers.compute_c_f64 import compute_c_f64

   f = load_solution()
   best_c = compute_c_f64(f)
   dx = 0.5 / len(f)

   # Strategy: pick 3 elements (i, j, k), perturb as:
   # f[i] += d1, f[j] += d2, f[k] -= (d1 + d2)
   # This preserves the integral exactly.

   # Selection strategies for (i, j, k):
   # A) Random triplets from nonzero elements
   # B) Structured: i from top-1000, j from bottom-1000, k compensating
   # C) Neighbor triplets: consecutive or nearby indices
   # D) Autoconvolution-peak-guided: elements contributing to max(f★f)

   nonzero = np.where(f > 1e-10)[0]
   improvements = 0

   for trial in range(50000):  # 50k trials
       # Pick strategy
       strategy = trial % 4
       if strategy == 0:  # random triplets
           idx = np.random.choice(nonzero, 3, replace=False)
       elif strategy == 1:  # large + small + compensator
           large = nonzero[np.argsort(f[nonzero])[-1000:]]
           small = nonzero[np.argsort(f[nonzero])[:1000]]
           idx = np.array([np.random.choice(large), np.random.choice(small),
                          np.random.choice(nonzero)])
       elif strategy == 2:  # neighbors
           start = np.random.choice(nonzero[:-2])
           idx = np.array([start, start+1, start+2])
       else:  # random from full array
           idx = np.random.choice(len(f), 3, replace=False)

       i, j, k = idx
       for d1 in [1e-7, 1e-6, 1e-5, 1e-4, 1e-3]:
           for d2 in [1e-7, 1e-6, 1e-5, 1e-4, 1e-3]:
               d3 = -(d1 + d2)
               # Check non-negativity
               if f[i] + d1 < 0 or f[j] + d2 < 0 or f[k] + d3 < 0:
                   continue
               old = f[i], f[j], f[k]
               f[i] += d1; f[j] += d2; f[k] += d3
               new_c = compute_c_f64(f)
               if new_c < best_c:
                   best_c = new_c
                   improvements += 1
                   break
               f[i], f[j], f[k] = old
           else:
               continue
           break
   ```

3. **Also try sign-mixed triplets:**
   - f[i] += d, f[j] += d, f[k] -= 2d (two up, one down)
   - f[i] -= d, f[j] -= d, f[k] += 2d (two down, one up)
   - These shift mass between elements in ways pairs cannot.

4. **Time budget:** At N=30000, each compute_c_f64 call takes ~20ms. Budget 10000 evaluations (200 seconds). If finding improvements, continue. If zero improvements after 5000 evals, try quadruplet perturbation (4-element moves).

5. **Bake any improved array as literal in entrypoint().**

### Important: Begin coding immediately
Do NOT spend more than 3 turns reading files. The brief contains all necessary context. Start implementing immediately after loading the solution array.

### What NOT to do
- Do NOT use smooth-max Adam (confirmed dead)
- Do NOT use pair-wise perturbation (already near pair-wise optimal, only 1 improvement in 300 trials)
- Do NOT try gradient descent approaches

### Success criteria
- Primary: Find any triplet improvement (even one is significant — proves the space is not triplet-optimal)
- Secondary: If no improvements found, establish the number of trials attempted as evidence
- Tertiary: Compare improvement density across selection strategies (random vs structured vs neighbor)
