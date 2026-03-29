## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen008/explore_1/sol01.py` → C = 1.5028628684790137
Second best: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen008/exploit_1/sol01.py` → C = 1.5028628686351897

## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/clusters/cluster_003.md` — Published solutions and LP approaches
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/disputed/idea_020.md` — LP refinement (disputed, 0.2 confidence)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/patterns/active/pattern_013.md` — Autoconv plateau blocks LP at N=30k
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/patterns/active/pattern_015.md` — Downsampling destroys structure
- `/home/sasha/Desktop/project_alpha/alpha-evolve/reports/gen008/explore_2.md` — LP plateau analysis (critical context: downsampling gives C=7)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/initial_programs/optimize.py` — Gradient descent baseline (adapt for N=5000)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/compute_c_f64.py` — Float64 C computation
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/cross_convolution_f64.py` — Autoconvolution
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/incremental_autoconv_update.py` — O(N) incremental update
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/lp_matrix.py` — LP solver helper

## Directive

**N=5000 optimization from scratch → coordinate descent → LP tractability study.**

This is the ONLY remaining avenue that could lead to a fundamentally different optimization path. The goal is NOT to beat the N=30k frontier (you almost certainly won't) but to **definitively answer whether LP is tractable at intermediate resolution.**

**Protocol:**

### Phase 1: Build a near-optimal N=5000 solution (budget: 30-45 min compute)

1. Port the logic from `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/initial_programs/optimize.py` to run at N=5000:
   - Use JAX + smooth-max gradient descent (Adam optimizer)
   - Temperature schedule: [0.05, 0.01, 0.003, 0.001, 0.0003]
   - 15k-20k steps per temperature phase
   - 4-8 random seeds, keep best
   - **Do NOT downsample the N=30k TTT-Discover array** — gen 8 showed this gives C=7+ (pattern_015)
   - Start from random init (Gaussian bumps or uniform noise)
2. Target: reach C ≈ 1.509-1.510 from gradient descent
3. Then run coordinate descent (use `incremental_update` for O(N) updates):
   - Full-array scan, delta grid [±1e-2 to ±1e-7] + proportional + zeroing
   - Multiple rounds until convergence
   - Target: push as low as possible (maybe C ≈ 1.505-1.508?)

### Phase 2: LP tractability study (budget: 15-20 min)

Once you have a well-optimized N=5000 solution:
1. Measure tight constraint counts at multiple epsilon levels:
   - tight@1e-4, tight@1e-5, tight@1e-6, tight@1e-7
   - Record exact counts for each
2. If tight@1e-5 < 500:
   - Run `scipy_lp_solve` from `helpers/lp_matrix.py`
   - Apply line search with 20 log-spaced step sizes (alpha from 1e-6 to 1e-1)
   - Record: whether LP direction improves C, by how much, how many LP iterations succeed
3. If tight@1e-5 ≥ 500: record the counts and report that LP at N=5000 hits the same plateau problem

### Phase 3: Report (even if LP fails)

**This experiment produces a diagnostic report, not necessarily a frontier-competing solution.** The report should answer:
- What C did N=5000 optimization reach?
- How many tight constraints at each epsilon level?
- Is the plateau at N=5000 similar in character to N=30k (pattern_013)?
- Is LP mechanically feasible? Does it find improvement?
- **Definitive recommendation:** should the system pursue LP at intermediate N, or archive idea_020?

**DO NOT** spend time trying to make the N=5000 solution competitive with N=30k. The N=30k TTT-Discover array is a special structure from external research. The point is LP tractability data, not a new best solution.

**Off-limits:** Do not attempt to downsample N=30k to N=5000 (confirmed C=7+, pattern_015). Do not attempt LP at N=30k (confirmed blocked by 6500-point plateau, pattern_013).
