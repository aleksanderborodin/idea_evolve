## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/best.py` → C = 1.5028628689
Second best: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen007/exploit_2/sol01.py` → C = 1.5028628703

## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen007/explore_1/sol01.py` — current best, YOUR starting point
- `/home/sasha/Desktop/project_alpha/alpha-evolve/reports/gen007/explore_1.md` — triplet implementation details
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/incremental_autoconv_update.py` — O(N) incremental update
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/cross_convolution_f64.py` — autoconvolve(), tight_constraint_indices()
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/compute_c_f64.py` — float64 C computation
- `/home/sasha/Desktop/project_alpha/alpha-evolve/feedback/experiment_suggestions/gen007.md` — Experiment 5 describes quadruplets

## Directive

**Quadruplet perturbation (d1+d2+d3+d4=0).** Pairs failed where triplets succeeded. Triplets found 160 improvements (gen 7) where coordinate descent (single-element) was converged. The mathematical argument generalizes: optimality under k-element moves does NOT imply optimality under (k+1)-element moves. Quadruplets may succeed where triplets exhaust.

**Protocol:**
1. Load gen007_explore_1_sol01.py (C=1.5028628689)
2. Initialize autoconvolution
3. Run 100k quadruplet trials with gradient-guided selection

**Quadruplet implementation:**
For quadruplet (i, j, k, l), you have 3 free variables (d1, d2, d3) with d4 = -d1-d2-d3.

Gradient computation:
- Let n* = argmax(autoconv). The gradient of autoconv[n*] w.r.t. d_m (for element m) is approximately:
  `g_m = 2 * dx * f_padded[(n* - m) % M]`
  where f_padded is the zero-padded array of length M=2N.
- Project the 4D gradient onto the 3D constraint plane (d1+d2+d3+d4=0):
  `g_projected = g - mean(g) * ones(4)` where g = [g_i, g_j, g_k, g_l]
- Descent direction: d = -g_projected (negate for minimization)
- Scale d so that d4 = -d1-d2-d3 (already satisfied by projection)
- Try step sizes: [1e-7, 3e-7, 1e-6, 3e-6, 1e-5, 3e-5, 1e-4, 3e-4, 1e-3]
- For each step size alpha: apply f[i]+=alpha*d1, f[j]+=alpha*d2, f[k]+=alpha*d3, f[l]+=alpha*d4
- Update autoconv incrementally (4 incremental updates per trial)
- Accept if C improves and all f values remain >= 0

**Selection strategies (rotate every 4 trials, log per-strategy):**
- S0: 4 random from nonzero elements
- S1: 2 large (top-10%) + 2 small (bottom-10%) — mass redistribution
- S2: 4 consecutive neighbors from a random nonzero element
- S3: 2 random nonzero + 2 fully random from [0..N)

**MANDATORY logging:** Track improvements per strategy in `by_strategy = {0: 0, 1: 0, 2: 0, 3: 0}`. Report breakdown in debrief AND observations.md.

**After quadruplet exhaustion:** If time remains and quadruplets found improvements, run a short triplet pass (20k trials) to check if quadruplet moves unlocked new triplet directions.

**Implementation details:**
- ALL float64 (numpy)
- Use `from helpers.incremental_autoconv_update import incremental_update` for O(N) updates
- Apply 4 incremental updates per accepted move (one per changed element)
- Non-negativity: reject any move that would make any element negative
- Verify final C with compute_c_f64
- Bake final array as literal in sol01.py

**What NOT to do:**
- Do NOT try coordinate descent, LP, gradient descent, or any method in dead ends
- Do NOT spend time on standard triplets (exploit_1 and exploit_2 are doing that)
- Begin coding immediately. Do NOT spend more than 3 turns reading files.
