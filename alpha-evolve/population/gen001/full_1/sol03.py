# fitness: TBD
"""
L-BFGS-B optimization with explicit non-negativity bounds.
L-BFGS-B uses curvature (second-order) information and enforces f>=0 via box constraints,
avoiding the relu-clipping gradient issues of Adam-based approaches.

Strategy:
1. Phase 1: Adam 20k steps to reach a good basin
2. Phase 2: L-BFGS-B refinement from Phase 1 result (up to 20k iterations)
3. 3 restarts, keep best
"""
import jax
import jax.numpy as jnp
import numpy as np
import optax
import scipy.optimize as scipy_opt

from helper import compute_c


def entrypoint() -> np.ndarray:
    N = 800

    # --- Adam phase ---
    adam_steps = 20000
    warmup_steps = 1000
    peak_lr = 0.005

    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=peak_lr,
        warmup_steps=warmup_steps,
        decay_steps=adam_steps - warmup_steps,
        end_value=peak_lr * 1e-2,  # don't fully decay — keep momentum for L-BFGS-B handoff
    )
    optimizer = optax.adam(learning_rate=schedule)

    @jax.jit
    def adam_step(f_vals, opt_st):
        loss, grads = jax.value_and_grad(compute_c)(f_vals)
        updates, new_opt_st = optimizer.update(grads, opt_st, f_vals)
        f_vals = optax.apply_updates(f_vals, updates)
        return f_vals, new_opt_st, loss

    # --- L-BFGS-B phase ---
    compute_c_val_grad = jax.jit(jax.value_and_grad(compute_c))

    def lbfgsb_obj(x):
        f = jnp.array(x, dtype=jnp.float32)
        val, grad = compute_c_val_grad(f)
        return float(val), np.array(grad, dtype=np.float64)

    bounds = scipy_opt.Bounds(lb=0.0, ub=np.inf)

    best_c = float('inf')
    best_f = None

    seeds = [42, 1234, 9999]
    x = jnp.linspace(-0.25, 0.25, N)

    for i, seed in enumerate(seeds):
        key = jax.random.PRNGKey(seed)
        noise = 0.05 * jax.random.uniform(key, (N,))

        if i == 0:
            f_init = jnp.zeros((N,))
            s, e = N // 4, 3 * N // 4
            f_init = f_init.at[s:e].set(1.0)
            f_init = f_init + noise
        elif i == 1:
            f_init = jnp.zeros((N,))
            s, e = int(N * 0.15), int(N * 0.85)
            f_init = f_init.at[s:e].set(1.0)
            f_init = f_init + noise
        else:
            f_init = jnp.maximum(0.0, 1.0 - 4.0 * jnp.abs(x)) + noise

        # Phase 1: Adam warm-up
        f_values = f_init
        opt_state = optimizer.init(f_values)
        for _ in range(adam_steps):
            f_values, opt_state, _ = adam_step(f_values, opt_state)

        x0 = np.array(jax.nn.relu(f_values), dtype=np.float64)

        # Phase 2: L-BFGS-B refinement with non-negativity bounds
        result = scipy_opt.minimize(
            lbfgsb_obj,
            x0,
            method='L-BFGS-B',
            jac=True,
            bounds=bounds,
            options={'maxiter': 20000, 'maxfun': 50000, 'ftol': 1e-14, 'gtol': 1e-9},
        )

        f_final = np.maximum(0.0, result.x)
        final_c = float(compute_c(jnp.array(f_final, dtype=jnp.float32)))

        if final_c < best_c:
            best_c = final_c
            best_f = f_final

    return best_f.astype(np.float32)
