## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/knowledge/clusters/cluster_001.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/knowledge/clusters/cluster_002.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/knowledge/ideas/established/idea_007.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/knowledge/research/gen001/research_1/findings.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/population/gen001/full_1/sol03.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/history/coverage_matrix.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problem/description.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problem/constraints.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problem/evaluate.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problem/helper.py`

## Directive

**Explore coarse-to-fine optimization combined with smooth-max** — this is the #1 unexplored high-priority combination from the coverage matrix.

The research findings (Finding 3) describe exactly how this works based on Boyer et al.:
1. Start at coarse resolution (N=30-50), run smooth-max optimization with warm temperature
2. Upsample to medium resolution (N=150-200) via `jnp.interp`, continue optimization
3. Upsample to final resolution (N=600), run smooth-max with full temperature annealing schedule

**Why this should work:** In gen 1, multi-scale WITHOUT smooth-max failed badly (C=1.5270-1.5730) because gradient descent at coarse scale locked into bad basins. Smooth-max's gradient spreading should prevent basin-locking at the coarse stage, allowing the optimizer to find the right global structure before refining at fine scale.

**Implementation guidance:**
- At coarse scale (N=30-50): use smooth-max with T=0.1-0.01, run 10,000-20,000 Adam steps with 8+ restarts. The small parameter count makes this very fast.
- Upsample: `f_fine = jnp.interp(jnp.linspace(0,1,N_fine), jnp.linspace(0,1,N_coarse), f_coarse)`
- At each subsequent scale: resume smooth-max optimization starting from a warmer temperature than the previous scale ended at.
- Use softplus reparameterization throughout (as in sol03).
- Keep the best of multiple restarts at each scale level.

**Do NOT:** Try simulated annealing (another agent covers that). Do NOT try L-BFGS refinement (exploit agent covers that). Focus purely on the coarse-to-fine + smooth-max combination.

Target: C < 1.510. Stretch goal: C < 1.505.
