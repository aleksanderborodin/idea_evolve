## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/description.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/constraints.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/initial_programs/optimize.py`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helper.py`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_003.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_004.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_005.md`

## Directive
Build a complete, polished solution end-to-end that improves on the baseline (C=1.5185). Your approach: take the baseline gradient descent and apply the most impactful improvements together in one solution.

Concrete plan:
1. Start from the baseline code structure (JAX + optax Adam).
2. Increase resolution to N=1000-2000.
3. Use a multi-restart strategy: run optimization from 3-5 different random initializations, keep the best result.
4. Increase steps to 80k-100k with a lower peak learning rate (0.001-0.003).
5. Apply relu at each step (not just at the end) to enforce non-negativity throughout optimization, which keeps the optimizer in the feasible region.
6. Try adding a symmetry constraint: f_values = (f_values + f_values[::-1]) / 2 after each step.

The goal is a single robust solution that reliably beats 1.5185. Prioritize reliability over novelty. Evaluate after each modification to track which changes help.
