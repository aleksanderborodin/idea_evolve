# fitness: 0.0
# Approach: Higher resolution N=1000, extended 60k Adam + L-BFGS refinement
# Finer discretization reduces approximation error, may allow finding better shapes.
# Same middle-box init as baseline but more steps and finer grid.

import numpy as np
import jax
import jax.numpy as jnp
import optax
from scipy.optimize import minimize
import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')
from helper import compute_c


def entrypoint() -> np.ndarray:
    N = 1000

    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=0.005,
        warmup_steps=2000,
        decay_steps=58000,
        end_value=5e-8,
    )
    optimizer = optax.adam(schedule)

    key = jax.random.PRNGKey(42)
    f_values = jnp.zeros((N,))
    f_values = f_values.at[N//4:3*N//4].set(1.0)
    f_values = f_values + 0.05 * jax.random.uniform(key, (N,))

    opt_state = optimizer.init(f_values)

    @jax.jit
    def train_step(p, st):
        loss, grads = jax.value_and_grad(compute_c)(p)
        updates, st = optimizer.update(grads, st, p)
        p = optax.apply_updates(p, updates)
        return p, st, loss

    for _ in range(60000):
        f_values, opt_state, loss = train_step(f_values, opt_state)

    warm = np.array(jax.nn.relu(f_values))

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
