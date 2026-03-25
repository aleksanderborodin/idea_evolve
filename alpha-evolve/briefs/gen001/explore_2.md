## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_001.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_002.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_003.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_004.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_005.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_006.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_003.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/description.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/constraints.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helper.py`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/initial_programs/optimize.py`

## Directive
**Direction: Analytical and structural constructions — exploit mathematical structure of the problem.**

The baseline does pure numerical optimization with no mathematical insight. Your goal is to construct functions with known good autoconvolution properties, then optionally polish them with gradient descent.

Specific approaches to try (in priority order):

1. **Characteristic functions of intervals:** The simplest non-negative function is an indicator function (constant on some subinterval, zero elsewhere). Try indicator functions of different widths and positions within [-1/4, 1/4]. The autoconvolution of a box function is a triangle — analyze what width minimizes C.

2. **Symmetric constructions:** The problem has natural symmetry around 0. Try functions that are symmetric: f(x) = f(-x). This halves the effective search space and the autoconvolution inherits the symmetry.

3. **Piecewise-linear and piecewise-polynomial functions:** Construct tent functions, trapezoidal functions, or piecewise quadratic shapes. These have analytically tractable autoconvolutions and can be parameterized by a few numbers, enabling exhaustive search over the parameter space.

4. **Cosine/Fourier basis constructions:** Represent f as a sum of cosine basis functions with non-negativity enforced. The autoconvolution in Fourier space is just squaring the transform. Optimize the Fourier coefficients directly.

5. **B-spline representations:** Use B-spline basis with a small number of control points. Optimize control point heights. B-splines are non-negative by construction (with positive coefficients), smooth, and have nice convolution properties.

6. **Hybrid: construct then polish.** Take the best analytical construction and use it as initialization for a short JAX gradient descent run (10k steps) to fine-tune.

Do NOT pursue pure numerical optimization with random/flat initialization — that's explore_1's direction.

For each solution: write it, run `python3 problem/evaluate.py <path>`, update the `# fitness:` header, then move on to the next variant.
