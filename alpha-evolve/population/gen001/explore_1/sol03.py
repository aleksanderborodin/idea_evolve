# fitness: 1.5256975893935902
# Adam 80k steps at N=600, cosine window initialization
# Score: 1.5257 — near baseline but slightly worse. Cosine init not better than flat block.

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax

from helper import compute_c


def entrypoint() -> np.ndarray:
    N = 600
    num_steps = 80000
    learning_rate = 0.003
    warmup_steps = 3000

    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=learning_rate,
        warmup_steps=warmup_steps,
        decay_steps=num_steps - warmup_steps,
        end_value=learning_rate * 1e-4,
    )
    optimizer = optax.adam(learning_rate=schedule)

    x = jnp.linspace(-0.25, 0.25, N)
    f_values = 0.5 * (1.0 - jnp.cos(2.0 * jnp.pi * (x + 0.25) / 0.5))
    key = jax.random.PRNGKey(7)
    f_values = f_values + 0.02 * jax.random.uniform(key, (N,))

    opt_state = optimizer.init(f_values)

    @jax.jit
    def train_step(f_vals, opt_st):
        loss, grads = jax.value_and_grad(compute_c)(f_vals)
        updates, opt_st = optimizer.update(grads, opt_st, f_vals)
        f_vals = optax.apply_updates(f_vals, updates)
        return f_vals, opt_st, loss

    for _ in range(num_steps):
        f_values, opt_state, _ = train_step(f_values, opt_state)

    return np.array(jax.nn.relu(f_values))
