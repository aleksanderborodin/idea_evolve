## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/description.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/constraints.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/initial_programs/optimize.py`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helper.py`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_001.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_002.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_003.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_004.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_001.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_002.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_003.md`

## Directive
Explore gradient-based optimization improvements to beat the baseline C=1.5185. Focus on three axes:

1. **Optimizer and schedule tuning.** The baseline uses Adam with cosine schedule at lr=0.005 for 40k steps. Try: (a) L-BFGS via scipy.optimize.minimize (since the problem is smooth and moderate-dimensional), (b) higher step counts (80k-200k) with lower learning rate, (c) different optax optimizers (e.g., adamw, lion, sgd with momentum).

2. **Higher resolution.** The baseline uses N=600. Try N=1000, N=2000, N=4000. Higher N gives a finer function representation. If compute is too slow at high N, use multi-scale: optimize at N=600 first, upsample via interpolation, then refine at N=2000+.

3. **Smarter initialization.** The baseline starts from a flat block [0.25, 0.75] + noise. Try: Gaussian bumps centered at 0 (middle of domain), cosine windows, triangular functions, B-splines. The initial shape determines which basin of attraction the optimizer finds.

Do NOT pursue analytical/closed-form constructions -- that is assigned to explore_2. Stay in the numerical optimization lane. Write multiple solutions trying different combinations. Evaluate each one immediately after writing.
