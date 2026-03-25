# fitness: 2.000046
# Approach: Symmetric truncated Gaussian with optimized width
# Enforce symmetry by mirroring, use parametric family optimization

import numpy as np
import jax
import jax.numpy as jnp
import optax
import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')
from helper import compute_c


def entrypoint() -> np.ndarray:
    N = 800

    # Grid over [-1/4, 1/4]
    x = jnp.linspace(-0.25, 0.25, N)

    def make_symmetric_gaussian(params):
        # params: [log_sigma, log_amplitude, center_offset (forced 0 for symmetry)]
        log_sigma = params[0]
        sigma = jnp.exp(log_sigma)
        # Symmetric Gaussian centered at 0
        f = jnp.exp(-0.5 * (x / sigma) ** 2)
        f = jnp.maximum(f, 0.0)
        return f

    # Optimize width of a centered Gaussian
    def objective(params):
        f = make_symmetric_gaussian(params)
        return compute_c(f)

    # Try several Gaussian widths analytically first
    best_c = float('inf')
    best_f = None

    for sigma_val in [0.05, 0.08, 0.1, 0.12, 0.15, 0.2, 0.25]:
        params = jnp.array([jnp.log(sigma_val)])
        f = make_symmetric_gaussian(params)
        c = float(compute_c(f))
        if c < best_c:
            best_c = c
            best_sigma = sigma_val

    # Now optimize with gradient descent
    params = jnp.array([jnp.log(best_sigma)])
    optimizer = optax.adam(0.01)
    opt_state = optimizer.init(params)

    @jax.jit
    def step(p, st):
        loss, grads = jax.value_and_grad(objective)(p)
        updates, st = optimizer.update(grads, st, p)
        p = optax.apply_updates(p, updates)
        return p, st, loss

    for _ in range(2000):
        params, opt_state, loss = step(params, opt_state)

    f_final = make_symmetric_gaussian(params)
    return np.array(f_final)
