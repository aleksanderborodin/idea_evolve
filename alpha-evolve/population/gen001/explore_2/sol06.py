# fitness: 0.0
# Approach: L-BFGS-B via scipy for fast convergence from warm start
# L-BFGS builds a curvature model and takes large Newton-like steps,
# converging in far fewer iterations than Adam.
# Two phases: Adam warm-start (5000 steps) then L-BFGS refinement.

import numpy as np
import jax
import jax.numpy as jnp
import optax
from scipy.optimize import minimize
import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')
from helper import compute_c


def entrypoint() -> np.ndarray:
    N = 800

    # Phase 1: Adam warm-start from middle box init
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0, peak_value=0.01,
        warmup_steps=500, decay_steps=9500, end_value=1e-4,
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

    # 10k Adam warm-up steps
    for _ in range(10000):
        f_values, opt_state, loss = train_step(f_values, opt_state)

    warm_start = np.array(f_values)

    # Phase 2: L-BFGS-B refinement (no non-negativity constraint — relu applied inside)
    # Objective and gradient via JAX
    @jax.jit
    def obj_and_grad(x):
        f = jnp.array(x)
        val, g = jax.value_and_grad(compute_c)(f)
        return val, g

    def scipy_obj(x):
        val, g = obj_and_grad(x.astype(np.float32))
        return float(val), np.array(g, dtype=np.float64)

    result = minimize(
        scipy_obj,
        warm_start.astype(np.float64),
        method='L-BFGS-B',
        jac=True,
        bounds=[(0, None)] * N,  # non-negativity constraint as bounds
        options={'maxiter': 10000, 'ftol': 1e-15, 'gtol': 1e-8}
    )

    f_final = np.maximum(result.x, 0.0)
    return f_final.astype(np.float32)
