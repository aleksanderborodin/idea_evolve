# Initial Ideas

## idea_001: Gradient descent with JAX
Use JAX + optax for differentiable optimization of the C constant directly.
The initial program uses Adam with cosine schedule. Try different optimizers,
learning rates, and initialization strategies.

## idea_002: Higher resolution discretization
Increase the number of grid points N beyond the baseline 600. More points
give a finer representation of the function shape, potentially finding
better optima. Trade-off: slower computation per iteration.

## idea_003: Function shape priors
Initialize with known function families that have good autoconvolution properties:
Gaussians, bump functions, cosine windows, B-splines. Use these as starting
points for optimization rather than flat/random initialization.

## idea_004: Multi-scale optimization
Start with low resolution (small N), optimize, then upsample and refine at
higher resolution. Coarse optimization finds the right general shape;
fine optimization tunes it.

## idea_005: Regularization approaches
Add regularization terms to the objective: smoothness penalties, sparsity,
symmetry enforcement. These may help the optimizer avoid local minima
with high C values.

## idea_006: Analytical constructions
Study the mathematical structure of the problem. The optimal function may
have analytical properties (symmetry, specific support pattern) that can
be constructed directly rather than optimized numerically.
