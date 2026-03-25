# fitness: 0.0
# Approach: Symmetry-enforced gradient descent (free-form but mirrored)
# Enforce f(x) = f(-x) by mirroring half the parameters.
# This halves search space and ensures symmetric autoconvolution.

import numpy as np
import jax
import jax.numpy as jnp
import optax
import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')
from helper import compute_c


def entrypoint() -> np.ndarray:
    N = 600  # same as baseline
    half = N // 2

    def symmetric_f(half_params):
        # Mirror: f[i] = f[N-1-i]
        half_relu = jax.nn.relu(half_params)
        # Build full array: [half[::-1], half]
        full = jnp.concatenate([half_relu[::-1], half_relu])
        return full

    def objective(half_params):
        f = symmetric_f(half_params)
        return compute_c(f)

    # Initialize with raised cosine shape on half
    x_half = jnp.linspace(0.0, 0.25, half)
    # Raised cosine window centered at 0, width ~0.4
    W = 0.4
    init_half = jnp.where(x_half <= W/2,
                          0.5 * (1 + jnp.cos(2 * jnp.pi * x_half / W)),
                          0.0)
    init_half = init_half + 0.01 * jax.random.uniform(jax.random.PRNGKey(7), (half,))

    # Multi-stage optimization
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0, peak_value=0.005,
        warmup_steps=1000, decay_steps=19000, end_value=5e-7
    )
    optimizer = optax.adam(schedule)
    params = init_half
    opt_state = optimizer.init(params)

    @jax.jit
    def step(p, st):
        loss, grads = jax.value_and_grad(objective)(p)
        updates, st = optimizer.update(grads, st, p)
        p = optax.apply_updates(p, updates)
        return p, st, loss

    for i in range(20000):
        params, opt_state, loss = step(params, opt_state)

    f_final = symmetric_f(params)
    return np.array(f_final)
