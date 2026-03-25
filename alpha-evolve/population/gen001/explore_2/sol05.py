# fitness: 0.0
# Approach: Multi-start with 3 diverse initializations, 40000 steps each
# Covers wider search space than single-start baseline.
# Picks the best result across all starts.

import numpy as np
import jax
import jax.numpy as jnp
import optax
import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')
from helper import compute_c


def entrypoint() -> np.ndarray:
    N = 600
    num_steps = 40000

    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0, peak_value=0.005,
        warmup_steps=2000, decay_steps=num_steps - 2000,
        end_value=5e-8,
    )
    optimizer = optax.adam(schedule)

    @jax.jit
    def train_step(p, st):
        loss, grads = jax.value_and_grad(compute_c)(p)
        updates, st = optimizer.update(grads, st, p)
        p = optax.apply_updates(p, updates)
        return p, st, loss

    # Init 1: baseline-style (middle box), seed 42
    key = jax.random.PRNGKey(42)
    f0 = jnp.zeros((N,))
    f0 = f0.at[N//4:3*N//4].set(1.0)
    f0 = f0 + 0.05 * jax.random.uniform(key, (N,))

    # Init 2: baseline-style, different seed
    key2 = jax.random.PRNGKey(999)
    f1 = jnp.zeros((N,))
    f1 = f1.at[N//4:3*N//4].set(1.0)
    f1 = f1 + 0.05 * jax.random.uniform(key2, (N,))

    # Init 3: right-heavy, with right 60% set to 1
    key3 = jax.random.PRNGKey(2024)
    f2 = jnp.zeros((N,))
    f2 = f2.at[2*N//5:].set(1.0)
    f2 = f2 + 0.05 * jax.random.uniform(key3, (N,))

    inits = [f0, f1, f2]

    best_c = float('inf')
    best_f = None

    for init_f in inits:
        params = init_f
        opt_state = optimizer.init(params)
        for _ in range(num_steps):
            params, opt_state, loss = train_step(params, opt_state)
        f_final = jax.nn.relu(params)
        c_val = float(compute_c(f_final))
        if c_val < best_c:
            best_c = c_val
            best_f = f_final

    return np.array(best_f)
