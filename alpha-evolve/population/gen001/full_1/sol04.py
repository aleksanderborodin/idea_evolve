# fitness: TBD
"""
Two-phase optimization: longer Adam warm-up + deeper L-BFGS-B refinement.
Based on sol03 result (1.5178) showing L-BFGS-B works — increase compute.

N=1000, Adam 40k steps + L-BFGS-B 50k iters, 3 restarts.
All restarts use baseline-like init (proven best basin), different noise seeds.
"""
import jax
import jax.numpy as jnp
import numpy as np
import optax
import scipy.optimize as scipy_opt

from helper import compute_c


def entrypoint() -> np.ndarray:
    N = 1000

    # Adam warm-up phase
    adam_steps = 40000
    warmup_steps = 2000
    peak_lr = 0.005

    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=peak_lr,
        warmup_steps=warmup_steps,
        decay_steps=adam_steps - warmup_steps,
        end_value=peak_lr * 1e-3,
    )
    optimizer = optax.adam(learning_rate=schedule)

    @jax.jit
    def adam_step(f_vals, opt_st):
        loss, grads = jax.value_and_grad(compute_c)(f_vals)
        updates, new_opt_st = optimizer.update(grads, opt_st, f_vals)
        f_vals = optax.apply_updates(f_vals, updates)
        return f_vals, new_opt_st, loss

    # L-BFGS-B refinement phase
    compute_c_vg = jax.jit(jax.value_and_grad(compute_c))

    def lbfgsb_obj(x):
        f = jnp.array(x, dtype=jnp.float32)
        val, grad = compute_c_vg(f)
        return float(val), np.array(grad, dtype=np.float64)

    bounds = scipy_opt.Bounds(lb=0.0, ub=np.inf)

    best_c = float('inf')
    best_f = None

    # All 3 restarts use the proven-best baseline-like init, just with different noise
    seeds = [42, 7777, 31415]

    for seed in seeds:
        key = jax.random.PRNGKey(seed)
        noise = 0.05 * jax.random.uniform(key, (N,))
        f_init = jnp.zeros((N,))
        s, e = N // 4, 3 * N // 4
        f_init = f_init.at[s:e].set(1.0)
        f_init = f_init + noise

        # Phase 1: Adam
        f_values = f_init
        opt_state = optimizer.init(f_values)
        for _ in range(adam_steps):
            f_values, opt_state, _ = adam_step(f_values, opt_state)

        x0 = np.array(jax.nn.relu(f_values), dtype=np.float64)

        # Phase 2: L-BFGS-B
        result = scipy_opt.minimize(
            lbfgsb_obj,
            x0,
            method='L-BFGS-B',
            jac=True,
            bounds=bounds,
            options={'maxiter': 50000, 'maxfun': 100000, 'ftol': 1e-15, 'gtol': 1e-10},
        )

        f_final = np.maximum(0.0, result.x)
        final_c = float(compute_c(jnp.array(f_final, dtype=jnp.float32)))

        if final_c < best_c:
            best_c = final_c
            best_f = f_final

    return best_f.astype(np.float32)
