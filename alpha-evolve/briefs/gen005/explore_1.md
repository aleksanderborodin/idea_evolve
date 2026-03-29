## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/best.py` → C = 1.5029 (TTT-Discover 30k array)
Second best: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/top/rank02_1.5032.py` (AlphaEvolve 1319 array)
Best gradient-descent result: C = 1.5090

## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/clusters/cluster_002.md` — problem representation cluster
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/established/idea_004.md` — coarse-to-fine strategy
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/established/idea_007.md` — smooth-max temperature annealing
- `/home/sasha/Desktop/project_alpha/alpha-evolve/reports/gen004/explore_1.md` — gen 4 SA timeout post-mortem (READ THIS CAREFULLY)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen004/explore_1/observations.md` — detailed SA budget analysis
- `/home/sasha/Desktop/project_alpha/alpha-evolve/feedback/experiment_suggestions/gen004.md` — Experiment 3 describes your task
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/README.md` — available helpers
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/description.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/constraints.md`

## Available Helpers
- `from helpers.core import compute_c` — JAX-differentiable C computation
- `from helpers.sensitivity import sensitivity_map` — computes dC/df[i] for all elements
- `from helpers.inv_softplus import inv_softplus_safe` — safe inverse softplus conversion
- `from helpers.interpolation import interpolate_sparse` — structure-preserving upsample (use this instead of cubic spline!)

## Compute Budget Reference
- N=23 Adam step: ~0.5ms (estimate)
- N=600 Adam step: ~1.5ms (estimate)
- Evaluation timeout: ~540s
- Safe total compute: < 400s
- **CRITICAL: Run a 100-step timing benchmark at N=23 FIRST. Print results. If step time > 1ms, ABORT SA and use simpler approach.**
- For SA: compute (seeds × SA_iters × inner_steps) × step_time. If > 400s: REDUCE.
- Example budget: 2 seeds × 100 SA iters × 300 inner steps = 60k gradient evals × 0.5ms = ~30s ✓

## Directive

**Implement properly calibrated Simulated Annealing at N=23 with a FIXED reduced budget.** This is the third attempt — gen 3 had miscalibrated temperatures (96-100% acceptance), gen 4 had correct calibration but 10× too many iterations (timed out). Your job: correct calibration AND feasible budget.

**Fixed budget (non-negotiable):**
- 2 seeds (not 4)
- 100 SA iterations (not 500)
- 300 inner optimizer steps per SA iteration
- 5k coarse Adam steps per temperature phase (3 phases: T=0.05, 0.003, 0.001)
- Use `from helpers.interpolation import interpolate_sparse` to upsample best SA result to N=600 (NOT cubic spline)
- 10k fine Adam steps per temperature phase at N=600 (5 phases: T=0.05, 0.01, 0.003, 0.001, 0.0003)
- Early stopping: if no SA improvement for 30 consecutive iterations, stop SA early

**SA calibration protocol (CRITICAL — this is what gen 3 got wrong):**
1. After coarse Adam convergence at N=23, compute baseline C
2. sigma = 0.05 × std(raw_params) — NOT 0.3 × mean
3. Run 20 trial perturbations, measure median |ΔC|
4. Set metro_t = 2 × median|ΔC|
5. Run 10 test SA steps, count acceptances
6. Target: 20-40% acceptance rate. If > 40%, halve metro_t. If < 20%, double metro_t. Repeat 3 times.
7. Print calibration results before starting main SA loop

**Cold inner optimizer:** After each SA perturbation acceptance, run inner optimizer at T=0.001 ONLY (300 steps). This is the "cold start" that gen 3 missed (they ran full T=0.05 schedule inside SA).

**What NOT to do:**
- Do NOT use cubic spline for upsampling (use `interpolate_sparse` from helpers)
- Do NOT run SA at N=600 (fine grid SA always returns to 1.509 basin — confirmed dead end)
- Do NOT use more than 2 seeds or 100 SA iterations (YOU WILL TIME OUT)
- Do NOT skip the calibration step (this is the entire point of this experiment)

**Success criterion:** C < 1.5090 (beat our best gradient-descent result). Even C < 1.510 would show SA found a different basin.
