# fitness: 1.515505474999503
# Multiple random seeds + select best + refine with L-BFGS
# Strategy: Run 8 random seeds for 15k steps, pick best, then run 60k steps + L-BFGS
# Rationale: Problem may have many local minima; wider search over initial conditions

import jax
import jax.numpy as jnp
import numpy as np
import optax
import scipy.optimize

from helper import compute_c


def run_adam(f_init, num_steps, lr):
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=lr,
        warmup_steps=max(200, num_steps // 10),
        decay_steps=num_steps,
        end_value=lr * 1e-5,
    )
    optimizer = optax.adam(learning_rate=schedule)
    f_values = jnp.array(f_init)
    opt_state = optimizer.init(f_values)

    @jax.jit
    def train_step(f_vals, opt_st):
        loss, grads = jax.value_and_grad(compute_c)(f_vals)
        updates, opt_st = optimizer.update(grads, opt_st, f_vals)
        f_vals = optax.apply_updates(f_vals, updates)
        return f_vals, opt_st, loss

    best_loss = float('inf')
    best_f = f_values
    for step in range(num_steps):
        f_values, opt_state, loss = train_step(f_values, opt_state)
        if float(loss) < best_loss:
            best_loss = float(loss)
            best_f = f_values

    return np.array(jax.nn.relu(best_f)), best_loss


def entrypoint() -> np.ndarray:
    N = 600
    n_seeds = 8

    # Phase 1: quick run with multiple seeds to find best basin
    best_overall_loss = float('inf')
    best_overall_f = None

    for seed in range(n_seeds):
        key = jax.random.PRNGKey(seed)
        f_init = jnp.zeros((N,))
        # Vary initialization: different offsets and scales
        start_idx = max(0, N // 4 + (seed - n_seeds // 2) * N // 16)
        end_idx = min(N, 3 * N // 4 + (seed - n_seeds // 2) * N // 16)
        f_init = f_init.at[start_idx:end_idx].set(1.0)
        f_init = f_init + 0.05 * jax.random.uniform(key, (N,))

        f_result, loss = run_adam(f_init, num_steps=15000, lr=0.007)
        if loss < best_overall_loss:
            best_overall_loss = loss
            best_overall_f = f_result

    # Phase 2: refine best with longer Adam
    best_f_long, _ = run_adam(best_overall_f, num_steps=60000, lr=0.003)

    # Phase 3: L-BFGS fine-tuning
    def objective_and_grad(f_np):
        f_jax = jnp.array(f_np, dtype=jnp.float32)
        loss, grads = jax.value_and_grad(compute_c)(f_jax)
        return float(loss), np.array(grads, dtype=np.float64)

    bounds = [(0.0, None)] * N
    result = scipy.optimize.minimize(
        objective_and_grad,
        best_f_long.astype(np.float64),
        method='L-BFGS-B',
        jac=True,
        bounds=bounds,
        options={'maxiter': 5000, 'ftol': 1e-12, 'gtol': 1e-8},
    )

    return np.maximum(result.x, 0.0).astype(np.float32)
