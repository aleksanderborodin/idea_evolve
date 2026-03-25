# fitness: 1.5206852316995636
# Gaussian shape prior + Adam optimizer
# Strategy: Initialize with Gaussian centered at 0, N=800, 100k steps, cosine schedule
# Rationale: Gaussian is smooth and symmetric, likely close to optimal shape family

import jax
import jax.numpy as jnp
import numpy as np
import optax

from helper import compute_c


def entrypoint() -> np.ndarray:
    N = 800
    learning_rate = 0.01
    num_steps = 100000
    warmup_steps = 3000

    # Gaussian initialization centered at 0 over domain [-1/4, 1/4]
    xs = jnp.linspace(-0.25, 0.25, N)
    sigma = 0.08  # Moderate spread relative to domain width 0.5
    f_init = jnp.exp(-xs**2 / (2 * sigma**2))
    # Normalize so integral ≈ 1 initially
    dx = 0.5 / N
    f_init = f_init / (jnp.sum(f_init) * dx)

    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=learning_rate,
        warmup_steps=warmup_steps,
        decay_steps=num_steps - warmup_steps,
        end_value=learning_rate * 1e-5,
    )
    optimizer = optax.adam(learning_rate=schedule)

    f_values = f_init
    opt_state = optimizer.init(f_values)

    @jax.jit
    def train_step(f_vals, opt_st):
        loss, grads = jax.value_and_grad(compute_c)(f_vals)
        updates, opt_st = optimizer.update(grads, opt_st, f_vals)
        f_vals = optax.apply_updates(f_vals, updates)
        return f_vals, opt_st, loss

    for step in range(num_steps):
        f_values, opt_state, loss = train_step(f_values, opt_state)

    f_final = jax.nn.relu(f_values)
    return np.array(f_final)
