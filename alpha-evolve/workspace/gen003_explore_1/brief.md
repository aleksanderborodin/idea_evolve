## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/description.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/constraints.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helper.py`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/evaluate.py`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/clusters/cluster_001.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/clusters/cluster_002.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_004.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/established/idea_007.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen002/explore_1/sol03.py`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen002/explore_1/sol02.py`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/reports/gen002/explore_2.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/research/gen001/research_1/findings.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/feedback/experiment_suggestions/gen002.md`

## Directive

**Primary objective: Implement coarse-scale Simulated Annealing (N=30-50) followed by upsampling and warm smooth-max fine-tuning.** This is the Boyer et al. approach and the #1 unexplored priority across the entire system. No agent has tried SA at the coarse scale yet — gen2 explore_2 tried SA at N=600 (dead end, confirmed across 3 solutions).

**Why coarse-scale SA:** At N=30-50, the landscape has fewer local minima and each evaluation is ~400x cheaper than N=600. SA can meaningfully explore different basins at this scale. Boyer et al. achieved C=1.503 using SA at N=23.

**Implementation plan:**
1. Start with N=40 (or N=30). Optimize with warm smooth-max (T=0.1→0.01→0.003, 5k steps each) to get a converged coarse solution.
2. Run SA at the coarse scale: 30-50 iterations. Each SA step: perturb the solution (sigma = 0.3 * mean(|f|)), re-optimize with smooth-max Adam (T=0.05→0.01, 5k steps), accept/reject using Metropolis criterion.
3. **Log acceptance rate every 10 SA iterations.** Target 20-50%. If <10%, sigma too large. If >70%, sigma too small. Adjust mid-run if needed.
4. Upsample best coarse solution to N=600 via `jnp.interp`.
5. Run standard warm smooth-max fine-tuning: T=0.05→0.01→0.003→0.001→0.0003, 15k steps each.

**Budget:** 40 SA iterations x 10k inner steps = 400k coarse steps (~130s) + 75k fine steps (~25s) per seed. You can run 4-6 seeds within budget.

**Critical rules:**
- SA MUST be at the coarse grid (N=30-50), NOT at N=600. Fine-grid SA is a confirmed dead end.
- Fine stage MUST start warm (T=0.05). Cold fine stage (T=0.001) is a confirmed dead end (C=1.5188).
- Use softplus reparameterization for non-negativity (consistent with all top solutions).
- Write sol01.py FIRST with the simplest working version (fewer SA iters, fewer seeds). Evaluate it immediately. Then iterate.

**Do NOT:**
- Apply SA at N=600 or any fine resolution
- Use L-BFGS (zero effect after smooth-max, confirmed 4 times in gen2)
- Use cold fine stage after upsampling
- Spend more than 8 restarts on the standard (non-SA) approach — this is well-explored

**Current best: C = 1.5091** (gen002_explore_1_sol03, coarse-to-fine N=80→600, warm smooth-max, 12 restarts, no SA). Target: C <= 1.5053.
