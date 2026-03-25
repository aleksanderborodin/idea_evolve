## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/description.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/constraints.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/initial_programs/optimize.py`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helper.py`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_001.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_002.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_005.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_006.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_004.md`

## Directive
Explore analytical and structural approaches to minimizing C. Do NOT just tune the gradient descent from the baseline -- explore_1 handles that. Your job is to find fundamentally different function shapes.

Directions to try:

1. **Symmetry exploitation.** The autoconvolution (f*f) is symmetric. Try functions that are symmetric about the center of [-1/4, 1/4]. Enforce symmetry as a hard constraint (mirror the array) before computing C. This halves the search space.

2. **Known function families with good autoconvolution properties.** Try: (a) truncated Gaussians with optimized width, (b) raised cosine windows, (c) B-spline basis functions with optimized coefficients, (d) piecewise linear "tent" functions. Parameterize each family with a few parameters and optimize those parameters.

3. **Sparse/concentrated functions.** Instead of smooth functions, try functions with support on a small subset of the domain. The Sidon set connection suggests sparse constructions might yield low C. Try indicator functions on carefully chosen subsets, or functions that are zero except on a few intervals.

4. **Regularization-guided search.** Add smoothness penalties (TV norm, Laplacian) or entropy terms to the objective. These may reshape the loss landscape to avoid bad local minima.

For each approach, write a solution, evaluate it, then iterate. Use gradient optimization (JAX/optax) as needed to fine-tune parameters within each structural family.
