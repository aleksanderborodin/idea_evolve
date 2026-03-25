## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_001.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_002.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_003.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_004.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_005.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_001.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_002.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/description.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/constraints.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helper.py`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/initial_programs/optimize.py`

## Directive
**Build an improved end-to-end baseline that systematically improves on the initial program.**

The initial program (`/home/sasha/Desktop/project_alpha/alpha-evolve/problem/initial_programs/optimize.py`) achieves C~1.5185 using Adam with cosine schedule, N=600, 40k steps, and flat+noise initialization. Your job is to produce a solid, reliable improvement by making targeted enhancements to this approach.

Focus on these specific improvements:

1. **Better initialization:** Instead of flat+noise, initialize with a Gaussian bump centered at 0 with width ~0.15 (roughly half the domain). This gives the optimizer a head start toward a smooth, peaked function shape.

2. **Longer training:** Increase to 80k-100k steps. The baseline may not have converged.

3. **Higher resolution:** Try N=1000 and N=1500. More grid points allow finer function shapes.

4. **Non-negativity enforcement during training:** The baseline only applies ReLU at the end. Instead, apply `jax.nn.softplus` or `jax.nn.relu` inside the training loop so the optimizer always works with valid functions.

5. **Multiple restarts:** If time permits, run optimization 3-5 times with different random seeds and keep the best result.

Your goal is a reliable solution in the range C~1.50-1.51. This serves as the solid baseline for future exploit agents to refine.

For each solution: write it, run `python3 problem/evaluate.py <path>`, update the `# fitness:` header, then move on to the next variant.
