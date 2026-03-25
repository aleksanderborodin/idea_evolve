# fitness: 0.0
# Approach: Multi-seed at N=1000 with L-BFGS refinement
# N=1000 showed better discretization than N=600.
# Run 3 seeds × 50k steps, pick best, then L-BFGS refine.

import numpy as np
import jax
import jax.numpy as jnp
import optax
from scipy.optimize import minimize
import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')
from helper import compute_c


def run_adam(init_f, N, steps=50000):
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0, peak_value=0.005,
        warmup_steps=2000, decay_steps=steps - 2000, end_value=5e-8,
    )
    opt = optax.adam(schedule)
    params = init_f
    state = opt.init(params)

    @jax.jit
    def step(p, st):
        loss, grads = jax.value_and_grad(compute_c)(p)
        updates, st = opt.update(grads, st, p)
        return optax.apply_updates(p, updates), st, loss

    for _ in range(steps):
        params, state, _ = step(params, state)
    return jax.nn.relu(params)


def entrypoint() -> np.ndarray:
    N = 1000
    seeds = [42, 7, 2024]

    best_c = float('inf')
    best_f = None

    for seed in seeds:
        key = jax.random.PRNGKey(seed)
        f0 = jnp.zeros((N,))
        f0 = f0.at[N//4:3*N//4].set(1.0)
        f0 = f0 + 0.05 * jax.random.uniform(key, (N,))

        f_opt = run_adam(f0, N, steps=50000)
        c_val = float(compute_c(f_opt))
        if c_val < best_c:
            best_c = c_val
            best_f = f_opt

    # L-BFGS refinement on best
    warm = np.array(best_f)
    val_and_grad = jax.jit(jax.value_and_grad(compute_c))

    def scipy_obj(x):
        x_jax = jnp.array(x.astype(np.float32))
        val, g = val_and_grad(x_jax)
        return float(val), np.array(g, dtype=np.float64)

    result = minimize(
        scipy_obj,
        warm.astype(np.float64),
        method='L-BFGS-B',
        jac=True,
        bounds=[(0, None)] * N,
        options={'maxiter': 5000, 'ftol': 1e-15, 'gtol': 1e-9}
    )

    return np.maximum(result.x, 0.0).astype(np.float32)
