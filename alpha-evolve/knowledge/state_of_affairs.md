---
generation: 2
best_score: 1.5091
trajectory: improving
last_updated_gen: 2
---

# State of Affairs — Generation 2

## Current Standing

Best score: **C = 1.5091** (gen002_explore_1_sol03), down from 1.5108 (gen 1) and baseline 1.5185. Target is C <= 1.5053; gap is **0.0038**. Published results: AlphaEvolve C=1.5032, ThetaEvolve C=1.503133. Two generations completed, 28 valid solutions total. Trajectory: improving — gen 2 broke through the 1.5108 barrier via coarse-to-fine.

## What Works

1. **Smooth-max temperature annealing** (idea_007, confidence 0.9, established): The single most impactful technique. Log-sum-exp replaces jnp.max, annealed T=0.05→0.0003 over 5 phases of 15k steps. Without it, nothing breaks below 1.5155. With it, 1.5091.

2. **Coarse-to-fine with WARM fine stage** (idea_004+idea_007, confidence 0.65, active): Optimize at N=80 coarse, upsample to N=600, then re-anneal from T=0.05. The warm restart is critical — cold fine stage (T=0.001) gives only 1.5188. Best combination: N=80 coarse + warm fine + 8-12 restarts → 1.5091-1.5093.

3. **Multi-seed restart** (idea_008, confidence 0.8, established): 8 diverse seeds is the sweet spot. 16-20 seeds give diminishing returns (~0.0001 improvement). Diversity of init shape matters more than count.

4. **Asymmetry** (idea_012, confidence 0.9, established): C >= 2 for symmetric functions (proven). All competitive solutions are asymmetric. Deliberate asymmetry in initialization helps.

## Current Frontier

The pipeline just discovered that coarse-to-fine + warm smooth-max breaks the 1.5108 barrier. Three agents independently recommend **coarse-scale SA** (N=30-80, simulated annealing at coarse grid, then upsample) as the next experiment — this is the actual Boyer et al. approach and has never been tried. Also untested: warm-start polish from the 1.5091 solution with tighter temperature schedule.

## Coverage Map

**Well-explored (stable scores):**
- Adam + smooth-max + multi-seed at N=600: 1.5107-1.5108 (5+ trials). Basin floor reached.
- L-BFGS after smooth-max: zero effect (2 trials, both null improvement).
- SA at N=600 fine grid: dead end (3 trials, returns to same basin every time).

**Newly explored (gen 2):**
- Coarse-to-fine (N=80) + warm smooth-max: 1.5091-1.5093 (2 trials). Promising but small sample.
- Cold fine stage coarse-to-fine: 1.5188 (1 trial). Confirmed ineffective.

**Unexplored high-priority:**
1. Coarse-scale SA (N=30-80) → upsample → warm smooth-max fine (Boyer et al. approach).
2. Warm-start from 1.5091 solution + extended fine annealing (T→0.00003).
3. Non-Gaussian coarse inits (comb, step, arcsine) + coarse-to-fine.
4. Fourier-basis parameterization + smooth-max (Fourier alone was 1.5294).

## Dead Ends

- **SA at N=600:** Basin too sticky; every perturbation + re-optimization returns to ~1.5108.
- **L-BFGS after smooth-max:** Zero effect — smooth-max already fully converges the basin.
- **Pure L-BFGS (no Adam):** 1.6887. Cannot navigate non-smooth landscape.
- **Cold fine stage in coarse-to-fine:** 1.5188. Negates coarse benefit entirely.
- **More restarts beyond 8:** 16→1.5107, 20→1.5108. Bottleneck is basin selection.
- **Extended temp schedule (T=0.0001):** Negligible benefit beyond T=0.0003.
- **Symmetric initializations:** C >= 2 mathematical barrier.
- **Higher N (800, 1000, 1500):** Slower iterations, worse scores at current optimization quality.

## Open Questions

1. **Will coarse-scale SA (N=30-80) break below 1.505?** This is Boyer et al.'s actual approach and the #1 priority experiment. All three gen 2 coding agents recommended it.
2. **What is the optimal coarse N?** N=80 worked, N=40 was too small. N=30, 50, 120 untested.
3. **Can warm-start polish push 1.5091 toward 1.505?** Loading the best solution and running tighter annealing is cheap and fast but untested.
4. **Is softplus (idea_009) independently useful?** Present in all top solutions but never isolated. Controlled experiment needed.
5. **Evaluator did not write individual knowledge files in gen 2** — inline recommendations only. Some knowledge files were stale entering this review. The consistency reviewer has corrected the most critical ones (idea_004, idea_007, idea_010, both clusters).
6. **full_1 agent failed for the second consecutive generation** due to over-budgeted compute. Prompt needs explicit "cheapest first" enforcement.
