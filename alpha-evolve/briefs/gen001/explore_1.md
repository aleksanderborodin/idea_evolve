## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_001.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_002.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_003.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_004.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_005.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_003.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_004.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_005.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/description.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/constraints.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helper.py`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/initial_programs/optimize.py`

## Directive
**Direction: Advanced numerical optimization with shape priors and multi-scale refinement.**

The baseline uses flat initialization with small noise and Adam for 40k steps at N=600, achieving C~1.5185. Your goal is to beat this substantially through better optimization strategies.

Specific approaches to try (in priority order):

1. **Function shape priors (idea_003):** Initialize with known smooth function families that should have good autoconvolution properties — Gaussians, raised cosines, B-splines, or triangular functions. The optimal function for this problem likely has a specific smooth shape; starting near it should converge faster and to better minima.

2. **Multi-scale optimization (idea_004):** Start at low resolution (N=100-200), optimize to convergence, then upsample via interpolation to higher resolution (N=1000-2000) and refine. This avoids getting trapped in local minima at high resolution.

3. **Optimizer variations (idea_001):** Try L-BFGS (via scipy.optimize.minimize or JAX-based), which is better suited to smooth optimization landscapes than Adam. Also try much longer runs (100k+ steps) and learning rate sweeps.

4. **Higher resolution (idea_002):** Push N to 1000-2000 for the final refinement stage. More grid points give a finer representation of the optimal function.

5. **Regularization (idea_005):** Add smoothness penalties (TV norm, L2 gradient penalty) to discourage noisy solutions that may have artificially low C due to discretization artifacts.

Do NOT explore analytical/closed-form constructions — that's assigned to explore_2.

For each solution: write it, run `python3 problem/evaluate.py <path>`, update the `# fitness:` header, then move on to the next variant. Iterate aggressively — try many variants.
