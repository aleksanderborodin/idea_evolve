# fitness: 0.0
# Approach: N=1200, 60k Adam + L-BFGS + multi-seed best-of-2
# Higher resolution reduces discretization error further.
# Two seeds to improve coverage.

import numpy as np
import jax
import jax.numpy as jnp
import optax
from scipy.optimize import minimize
import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')
from helper import compute_c


def run_phase(N, init_f, adam_steps=60000):
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0, peak_value=0.005,
        warmup_steps=2000, decay_steps=adam_steps - 2000, end_value=5e-8,
    )
    optimizer = optax.adam(schedule)
    params = init_f
    opt_state = optimizer.init(params)

    @jax.jit
    def train_step(p, st):
        loss, grads = jax.value_and_grad(compute_c)(p)
        updates, st = optimizer.update(grads, st, p)
        p = optax.apply_updates(p, updates)
        return p, st, loss

    for _ in range(adam_steps):
        params, opt_state, loss = train_step(params, opt_state)

    warm = np.array(jax.nn.relu(params))

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


def entrypoint() -> np.ndarray:
    N = 1200

    key1 = jax.random.PRNGKey(42)
    f0 = jnp.zeros((N,))
    f0 = f0.at[N//4:3*N//4].set(1.0)
    f0 = f0 + 0.05 * jax.random.uniform(key1, (N,))

    key2 = jax.random.PRNGKey(999)
    f1 = jnp.zeros((N,))
    f1 = f1.at[N//4:3*N//4].set(1.0)
    f1 = f1 + 0.05 * jax.random.uniform(key2, (N,))

    best_c = float('inf')
    best_f = None

    for init_f in [f0, f1]:
        f_opt = run_phase(N, init_f, adam_steps=50000)
        c_val = float(compute_c(jnp.array(f_opt)))
        if c_val < best_c:
            best_c = c_val
            best_f = f_opt

    return best_f
