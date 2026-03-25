# fitness: 0.0
# Approach: Asymmetric free-form gradient descent, right-biased initialization
# Key insight: symmetric functions give C>=2 (convolution peak at t=0).
# Concentrating mass near x=0.25 (right edge) moves the conv peak to t~0.5
# (boundary of the max domain), allowing C < 2.
# Run more steps than baseline with better initialization.

import numpy as np
import jax
import jax.numpy as jnp
import optax
import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')
from helper import compute_c


def entrypoint() -> np.ndarray:
    N = 600
    num_steps = 50000
    warmup_steps = 2000

    def objective(f_values):
        return compute_c(f_values)

    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=0.005,
        warmup_steps=warmup_steps,
        decay_steps=num_steps - warmup_steps,
        end_value=5e-8,
    )
    optimizer = optax.adam(learning_rate=schedule)

    @jax.jit
    def train_step(f_vals, opt_st):
        loss, grads = jax.value_and_grad(objective)(f_vals)
        updates, opt_st = optimizer.update(grads, opt_st, f_vals)
        f_vals = optax.apply_updates(f_vals, updates)
        return f_vals, opt_st, loss

    # Right-biased initialization: box in top 3/4 of domain (x in [-1/8, 1/4])
    key = jax.random.PRNGKey(42)
    f_values = jnp.zeros((N,))
    start_idx = N // 4
    f_values = f_values.at[start_idx:].set(1.0)
    f_values = f_values + 0.05 * jax.random.uniform(key, (N,))

    opt_state = optimizer.init(f_values)

    for _ in range(num_steps):
        f_values, opt_state, loss = train_step(f_values, opt_state)

    return np.array(jax.nn.relu(f_values))
