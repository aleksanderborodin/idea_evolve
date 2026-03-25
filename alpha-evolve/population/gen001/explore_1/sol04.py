# fitness: 1.5181960065224405
# Longer Adam run with baseline initialization (80k steps, N=600)
# Strategy: Same as baseline but 2x more steps + lower final LR for fine convergence
# Rationale: Baseline converges but may not be fully saturated; more steps could help

import jax
import jax.numpy as jnp
import numpy as np
import optax

from helper import compute_c


def entrypoint() -> np.ndarray:
    N = 600
    learning_rate = 0.005
    num_steps = 80000
    warmup_steps = 2000

    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=learning_rate,
        warmup_steps=warmup_steps,
        decay_steps=num_steps - warmup_steps,
        end_value=learning_rate * 1e-5,
    )
    optimizer = optax.adam(learning_rate=schedule)

    key = jax.random.PRNGKey(42)
    f_values = jnp.zeros((N,))
    start_idx, end_idx = N // 4, 3 * N // 4
    f_values = f_values.at[start_idx:end_idx].set(1.0)
    f_values = f_values + 0.05 * jax.random.uniform(key, (N,))

    opt_state = optimizer.init(f_values)

    @jax.jit
    def train_step(f_vals, opt_st):
        loss, grads = jax.value_and_grad(compute_c)(f_vals)
        updates, opt_st = optimizer.update(grads, opt_st, f_vals)
        f_vals = optax.apply_updates(f_vals, updates)
        return f_vals, opt_st, loss

    for step in range(num_steps):
        f_values, opt_state, loss = train_step(f_values, opt_state)

    return np.array(jax.nn.relu(f_values))
