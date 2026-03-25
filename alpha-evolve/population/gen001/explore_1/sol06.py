# fitness: 1.5182650530840966
# Aggressive multi-seed search + high-resolution refinement
# Strategy: 16 seeds at N=600, top-3 refined for 60k steps, best upsampled to N=1500 + L-BFGS
# Rationale: sol05 showed multi-seed helps; pushing to N=1500 for finer representation

import jax
import jax.numpy as jnp
import numpy as np
import optax
import scipy.optimize
import scipy.interpolate

from helper import compute_c


def run_adam(f_init, num_steps, lr, warmup_frac=0.05):
    n = len(f_init)
    warmup = max(200, int(num_steps * warmup_frac))
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0, peak_value=lr,
        warmup_steps=warmup, decay_steps=num_steps - warmup,
        end_value=lr * 1e-5,
    )
    optimizer = optax.adam(learning_rate=schedule)
    f_values = jnp.array(f_init, dtype=jnp.float32)
    opt_state = optimizer.init(f_values)

    @jax.jit
    def train_step(f_vals, opt_st):
        loss, grads = jax.value_and_grad(compute_c)(f_vals)
        updates, opt_st = optimizer.update(grads, opt_st, f_vals)
        f_vals = optax.apply_updates(f_vals, updates)
        return f_vals, opt_st, loss

    best_loss = float('inf')
    best_f = f_values
    for _ in range(num_steps):
        f_values, opt_state, loss = train_step(f_values, opt_state)
        if float(loss) < best_loss:
            best_loss = float(loss)
            best_f = f_values

    return np.array(jax.nn.relu(best_f)), best_loss


def upsample(f_arr, new_n):
    old_n = len(f_arr)
    xs_old = np.linspace(-0.25, 0.25, old_n)
    xs_new = np.linspace(-0.25, 0.25, new_n)
    interp = scipy.interpolate.interp1d(xs_old, f_arr, kind='cubic', fill_value='extrapolate')
    return np.maximum(interp(xs_new), 0.0)


def lbfgs_refine(f_init):
    n = len(f_init)
    def obj_grad(f_np):
        f_jax = jnp.array(f_np, dtype=jnp.float32)
        loss, grads = jax.value_and_grad(compute_c)(f_jax)
        return float(loss), np.array(grads, dtype=np.float64)

    result = scipy.optimize.minimize(
        obj_grad, f_init.astype(np.float64), method='L-BFGS-B',
        jac=True, bounds=[(0.0, None)] * n,
        options={'maxiter': 3000, 'ftol': 1e-13, 'gtol': 1e-9},
    )
    return np.maximum(result.x, 0.0).astype(np.float32)


def entrypoint() -> np.ndarray:
    N = 600
    n_seeds = 16

    # Phase 1: quick exploration with 16 diverse seeds
    results = []
    for seed in range(n_seeds):
        key = jax.random.PRNGKey(seed * 7 + 13)  # varied seeds
        f_init = jnp.zeros((N,))
        # Vary the support: shift and scale
        offset = (seed % 5 - 2) * N // 20  # offsets: -2, -1, 0, 1, 2 * N/20
        start_idx = max(0, N // 4 + offset)
        end_idx = min(N, 3 * N // 4 + offset)
        f_init = f_init.at[start_idx:end_idx].set(1.0)
        # Vary noise level
        noise_scale = 0.02 + 0.1 * (seed % 4) / 3
        f_init = f_init + noise_scale * jax.random.uniform(key, (N,))

        f_result, loss = run_adam(np.array(f_init), num_steps=10000, lr=0.008)
        results.append((loss, f_result))

    results.sort(key=lambda x: x[0])

    # Phase 2: refine top 3 seeds further at N=600
    top3_refined = []
    for loss_init, f_init in results[:3]:
        f_ref, loss_ref = run_adam(f_init, num_steps=60000, lr=0.003)
        top3_refined.append((loss_ref, f_ref))

    top3_refined.sort(key=lambda x: x[0])
    best_loss, best_f = top3_refined[0]

    # Phase 3: upsample to N=1500 and refine
    N_high = 1500
    f_high_init = upsample(best_f, N_high)
    f_high, _ = run_adam(f_high_init, num_steps=20000, lr=0.001)

    # Phase 4: L-BFGS fine-tuning
    f_final = lbfgs_refine(f_high)

    return f_final
