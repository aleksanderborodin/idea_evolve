# fitness: 1.51890466365198
# Adam warm-up + L-BFGS fine-tuning
# Strategy: Adam finds good basin (20k steps), then L-BFGS refines to local optimum
# Rationale: Adam is robust but slow to converge; L-BFGS uses curvature for fast final convergence

import jax
import jax.numpy as jnp
import numpy as np
import optax
import scipy.optimize

from helper import compute_c


def entrypoint() -> np.ndarray:
    N = 600
    key = jax.random.PRNGKey(42)

    # Baseline-style initialization: flat in middle half + small noise
    f_init = jnp.zeros((N,))
    start_idx, end_idx = N // 4, 3 * N // 4
    f_init = f_init.at[start_idx:end_idx].set(1.0)
    f_init = f_init + 0.05 * jax.random.uniform(key, (N,))

    # Phase 1: Adam warm-up for 30k steps
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=0.005,
        warmup_steps=2000,
        decay_steps=28000,
        end_value=0.005 * 1e-4,
    )
    optimizer = optax.adam(learning_rate=schedule)
    f_values = f_init
    opt_state = optimizer.init(f_values)

    @jax.jit
    def train_step(f_vals, opt_st):
        loss, grads = jax.value_and_grad(compute_c)(f_vals)
        updates, opt_st = optimizer.update(grads, opt_st, f_vals)
        f_vals = optax.apply_updates(f_vals, updates)
        return f_vals, opt_st, loss

    for step in range(30000):
        f_values, opt_state, loss = train_step(f_values, opt_state)

    # Phase 2: L-BFGS-B fine-tuning (bounded to non-negative)
    # Convert JAX gradients to numpy for scipy
    f_adam = np.array(jax.nn.relu(f_values))

    def objective_and_grad(f_np):
        f_jax = jnp.array(f_np, dtype=jnp.float32)
        loss, grads = jax.value_and_grad(compute_c)(f_jax)
        return float(loss), np.array(grads, dtype=np.float64)

    bounds = [(0.0, None)] * N  # non-negativity constraint

    result = scipy.optimize.minimize(
        objective_and_grad,
        f_adam.astype(np.float64),
        method='L-BFGS-B',
        jac=True,  # gradients included in objective return value
        bounds=bounds,
        options={
            'maxiter': 5000,
            'ftol': 1e-12,
            'gtol': 1e-8,
        }
    )

    f_final = np.maximum(result.x, 0.0).astype(np.float32)
    return f_final
