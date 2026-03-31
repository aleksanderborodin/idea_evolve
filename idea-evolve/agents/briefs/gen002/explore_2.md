## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/knowledge/clusters/cluster_001.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/knowledge/ideas/established/idea_007.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/knowledge/research/gen001/research_1/findings.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/population/gen001/full_1/sol03.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/history/coverage_matrix.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problem/description.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problem/constraints.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problem/evaluate.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problem/helper.py`

## Directive

**Explore simulated annealing wrapper around smooth-max gradient descent.** This is strongly recommended by the research findings (Finding 4) based on Boyer et al., and was the #1 gap identified by the agent gaps analysis — no gen 1 agent tried it.

**The approach:**
1. Run smooth-max Adam optimization to convergence (use sol03's approach as the inner optimizer)
2. Perturb the converged function: `f_perturbed = f + sigma * noise`, clip to >= 0
3. Re-optimize from the perturbed point using smooth-max Adam
4. Accept the new solution if its C is lower; otherwise accept with probability exp(-delta_C / T_anneal)
5. Reduce sigma by factor 0.95-0.99 each iteration
6. Repeat for 50-200 anneal iterations

**Key parameters to tune:**
- Initial perturbation scale sigma_0: try 0.3-0.5 (relative to function max)
- Cooling factor: 0.97
- Inner optimization steps per anneal iteration: 3,000-5,000 (just enough to re-converge)
- Use a shorter smooth-max temperature schedule for inner iterations (e.g., T from 0.01 to 0.001 only)
- 4 restarts of the entire annealing process with different seeds

**Important:** The smooth-max temperature schedule and the simulated annealing temperature are DIFFERENT things:
- Smooth-max temperature = how soft the max approximation is (controls gradient flow)
- SA temperature = acceptance probability for worse solutions (controls exploration vs exploitation)

**Do NOT:** Try coarse-to-fine (another agent covers that). Do NOT try L-BFGS refinement (exploit agent covers that). Focus purely on the simulated annealing + smooth-max combination.

This is compute-intensive. Budget your turns carefully — start with a fast prototype (fewer anneal iterations, fewer inner steps), evaluate, then scale up if the approach shows promise.

Target: C < 1.508. Stretch goal: C < 1.503.
