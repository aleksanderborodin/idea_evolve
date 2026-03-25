# fitness: 1.5182
# Best-of-4 multi-seed search with Lion + Adam, 120k total steps per seed
# Builds on sol08 (Lion + Adam = 1.5207). Try 4 seeds with symmetric box init
# but different noise levels. Each gets: Lion 50k + Adam 70k = 120k steps.
# The symmetric box init helps because it doesn't predispose to one chirality.

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax

from helper import compute_c


def run_seed(key, N=1000, lion_steps=50000, adam_steps=70000):
    f_init = jnp.zeros(N)
    start_idx, end_idx = N // 4, 3 * N // 4
    f_init = f_init.at[start_idx:end_idx].set(1.0)
    noise_scale = jax.random.uniform(key, (), minval=0.01, maxval=0.08)
    f_init = f_init + noise_scale * jax.random.uniform(key, (N,))

    def objective(p):
        return compute_c(jax.nn.relu(p))

    # Phase 1: Lion
    sched_lion = optax.cosine_decay_schedule(
        init_value=5e-4, decay_steps=lion_steps, alpha=1e-4
    )
    opt_lion = optax.lion(learning_rate=sched_lion)
    opt_state = opt_lion.init(f_init)
    params = f_init

    @jax.jit
    def step_lion(p, st):
        loss, g = jax.value_and_grad(objective)(p)
        upd, st = opt_lion.update(g, st, p)
        return optax.apply_updates(p, upd), st, loss

    best_p, best_c = params, float('inf')
    for _ in range(lion_steps):
        params, opt_state, loss = step_lion(params, opt_state)
        c = float(loss)
        if c < best_c:
            best_c, best_p = c, params

    # Phase 2: Adam fine-tune from best found so far
    params = best_p
    sched_adam = optax.warmup_cosine_decay_schedule(
        init_value=0.0, peak_value=0.005,
        warmup_steps=2000, decay_steps=adam_steps - 2000, end_value=1e-6,
    )
    opt_adam = optax.adam(learning_rate=sched_adam)
    opt_state = opt_adam.init(params)

    @jax.jit
    def step_adam(p, st):
        loss, g = jax.value_and_grad(objective)(p)
        upd, st = opt_adam.update(g, st, p)
        return optax.apply_updates(p, upd), st, loss

    for _ in range(adam_steps):
        params, opt_state, loss = step_adam(params, opt_state)
        c = float(loss)
        if c < best_c:
            best_c, best_p = c, params

    return best_p, best_c


def entrypoint() -> np.ndarray:
    keys = [jax.random.PRNGKey(i) for i in [17, 42, 99, 137]]

    best_f = None
    best_c = float('inf')

    for key in keys:
        f, c = run_seed(key)
        if c < best_c:
            best_c = c
            best_f = f

    return np.array(jax.nn.relu(best_f))
