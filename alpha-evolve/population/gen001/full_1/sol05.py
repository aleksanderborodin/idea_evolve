# fitness: TBD
"""
Smooth max annealing: start with soft log-sum-exp max (better gradients),
gradually sharpen toward hard max. This avoids getting stuck at plateau from
gradient through single argmax point.

Pipeline per restart:
  Phase 1: Adam 20k steps, beta=20   (smooth landscape)
  Phase 2: Adam 20k steps, beta=100  (moderate sharpening)
  Phase 3: Adam 20k steps, beta=500  (near-hard max)
  Phase 4: L-BFGS-B, hard max via helper.compute_c

3 restarts, N=1000.
"""
import jax
import jax.numpy as jnp
import numpy as np
import optax
import scipy.optimize as scipy_opt

from helper import compute_c


def make_compute_c_soft(beta: float):
    """Soft-max version of compute_c using log-sum-exp."""
    def _fn(f_values):
        domain_width = 0.5
        N = len(f_values)
        dx = domain_width / N

        f_nn = jax.nn.relu(f_values)
        integral_f = jnp.sum(f_nn) * dx
        integral_f_sq_safe = jnp.maximum(integral_f ** 2, 1e-9)

        padded_f = jnp.pad(f_nn, (0, N))
        fft_f = jnp.fft.fft(padded_f)
        conv_f_f = jnp.fft.ifft(fft_f * fft_f).real
        scaled_conv = conv_f_f * dx

        # Log-sum-exp soft max: (1/beta) * log(sum(exp(beta * v)))
        soft_max = (1.0 / beta) * jax.nn.logsumexp(beta * scaled_conv)

        return soft_max / integral_f_sq_safe
    return _fn


def make_adam_trainer(objective_fn, num_steps, warmup_steps, peak_lr):
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=peak_lr,
        warmup_steps=warmup_steps,
        decay_steps=num_steps - warmup_steps,
        end_value=peak_lr * 1e-3,
    )
    optimizer = optax.adam(learning_rate=schedule)

    @jax.jit
    def step(f_vals, opt_st):
        loss, grads = jax.value_and_grad(objective_fn)(f_vals)
        updates, new_opt_st = optimizer.update(grads, opt_st, f_vals)
        f_vals = optax.apply_updates(f_vals, updates)
        return f_vals, new_opt_st, loss

    def run(f_init):
        f_values = f_init
        opt_state = optimizer.init(f_values)
        for _ in range(num_steps):
            f_values, opt_state, _ = step(f_values, opt_state)
        return f_values

    return run


def entrypoint() -> np.ndarray:
    N = 1000

    # Build smooth objectives at different sharpness levels
    c_soft_20 = make_compute_c_soft(beta=20.0)
    c_soft_100 = make_compute_c_soft(beta=100.0)
    c_soft_500 = make_compute_c_soft(beta=500.0)

    # Adam trainers for each phase (20k steps each, LR tuned per phase)
    run_phase1 = make_adam_trainer(c_soft_20, 20000, 1000, peak_lr=0.008)
    run_phase2 = make_adam_trainer(c_soft_100, 20000, 500, peak_lr=0.005)
    run_phase3 = make_adam_trainer(c_soft_500, 20000, 500, peak_lr=0.003)

    # L-BFGS-B with hard max
    compute_c_vg = jax.jit(jax.value_and_grad(compute_c))

    def lbfgsb_obj(x):
        f = jnp.array(x, dtype=jnp.float32)
        val, grad = compute_c_vg(f)
        return float(val), np.array(grad, dtype=np.float64)

    bounds = scipy_opt.Bounds(lb=0.0, ub=np.inf)

    best_c = float('inf')
    best_f = None

    seeds = [42, 1234, 9999]

    for i, seed in enumerate(seeds):
        key = jax.random.PRNGKey(seed)
        noise = 0.05 * jax.random.uniform(key, (N,))
        f_init = jnp.zeros((N,))
        s, e = N // 4, 3 * N // 4
        f_init = f_init.at[s:e].set(1.0)
        f_init = f_init + noise

        # Phase 1–3: smooth annealing
        f = run_phase1(f_init)
        f = run_phase2(f)
        f = run_phase3(f)

        x0 = np.array(jax.nn.relu(f), dtype=np.float64)

        # Phase 4: L-BFGS-B hard max refinement
        result = scipy_opt.minimize(
            lbfgsb_obj,
            x0,
            method='L-BFGS-B',
            jac=True,
            bounds=bounds,
            options={'maxiter': 30000, 'maxfun': 60000, 'ftol': 1e-15, 'gtol': 1e-10},
        )

        f_final = np.maximum(0.0, result.x)
        final_c = float(compute_c(jnp.array(f_final, dtype=jnp.float32)))

        if final_c < best_c:
            best_c = final_c
            best_f = f_final

    return best_f.astype(np.float32)
