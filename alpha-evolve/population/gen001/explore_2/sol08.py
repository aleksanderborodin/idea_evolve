# fitness: 1.5207
# Extended optimization from symmetric init with cyclical LR + Lion optimizer
# The baseline (symmetric box, Adam, 40k steps) achieves 1.5185.
# This tries: symmetric narrow box init but 100k steps total, using
# cyclical cosine restarts to escape local minima + Lion for better convergence.
# Lion optimizer often outperforms Adam for smooth objectives.

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax

from helper import compute_c


def entrypoint() -> np.ndarray:
    N = 1000
    key = jax.random.PRNGKey(99)

    # Symmetric narrow-box init (like baseline, but more noise to help exploration)
    f_init = jnp.zeros(N)
    start_idx, end_idx = N // 4, 3 * N // 4
    f_init = f_init.at[start_idx:end_idx].set(1.0)
    f_init = f_init + 0.03 * jax.random.uniform(key, (N,))

    def objective(p):
        return compute_c(jax.nn.relu(p))

    params = f_init

    # Phase 1: Lion optimizer, cosine schedule, 60k steps
    # Lion uses sign gradient updates which can escape plateaus faster
    schedule1 = optax.cosine_decay_schedule(
        init_value=3e-4,
        decay_steps=60000,
        alpha=1e-4,
    )
    opt1 = optax.lion(learning_rate=schedule1)
    opt_state1 = opt1.init(params)

    @jax.jit
    def train_step1(p, opt_st):
        loss, grads = jax.value_and_grad(objective)(p)
        updates, opt_st = opt1.update(grads, opt_st, p)
        p = optax.apply_updates(p, updates)
        return p, opt_st, loss

    best_params = params
    best_c = float('inf')

    for step in range(60000):
        params, opt_state1, loss = train_step1(params, opt_state1)
        if float(loss) < best_c:
            best_c = float(loss)
            best_params = params

    # Phase 2: Adam with warm restart from best found, 50k more steps
    params = best_params
    schedule2 = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=0.004,
        warmup_steps=2000,
        decay_steps=48000,
        end_value=1e-6,
    )
    opt2 = optax.adam(learning_rate=schedule2)
    opt_state2 = opt2.init(params)

    @jax.jit
    def train_step2(p, opt_st):
        loss, grads = jax.value_and_grad(objective)(p)
        updates, opt_st = opt2.update(grads, opt_st, p)
        p = optax.apply_updates(p, updates)
        return p, opt_st, loss

    for step in range(50000):
        params, opt_state2, loss = train_step2(params, opt_state2)
        if float(loss) < best_c:
            best_c = float(loss)
            best_params = params

    return np.array(jax.nn.relu(best_params))
