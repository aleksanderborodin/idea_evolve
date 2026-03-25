# fitness: 1.5108
# Approach: Full sol03-style initial convergence (8 seeds × 75k steps) + SA with L-BFGS inner
#
# Key improvement over sol01/sol02:
#   - 8 seeds (matches sol03's proven starting quality → C ≈ 1.511)
#   - L-BFGS for SA inner optimization: converges in 300 iters vs 6000 Adam steps
#     L-BFGS uses curvature info, far more efficient for smooth softplus landscape
#
# Result: 1.5108 — matches gen001 sol03. SA did not improve beyond initial Adam convergence.
# The 8-seed Adam phase finds C=1.5108; L-BFGS SA finds nothing better.
#
# Total compute:
#   - 8 seeds × 75k Adam steps = 600k (same as sol03)
#   - 60 SA iters × L-BFGS(300) ≈ 30 seconds
#   - Grand total: ~3.5 minutes

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax
from scipy.optimize import minimize
from helper import compute_c


def smooth_compute_c_dyn(f_values, temp):
    """Smooth-max C with dynamic temperature."""
    domain_width = 0.5
    N = len(f_values)
    dx = domain_width / N
    f_nn = jax.nn.softplus(f_values)
    integral_f = jnp.sum(f_nn) * dx
    integral_f_sq = jnp.maximum(integral_f**2, 1e-9)
    padded_f = jnp.pad(f_nn, (0, N))
    fft_f = jnp.fft.fft(padded_f)
    conv_f_f = jnp.fft.ifft(fft_f * fft_f).real
    scaled_conv = conv_f_f * dx
    smooth_max = temp * jax.scipy.special.logsumexp(scaled_conv / temp)
    return smooth_max / integral_f_sq


def inv_softplus(y):
    """Inverse softplus."""
    return jnp.log(jnp.expm1(jnp.clip(y, 1e-4, None)))


def entrypoint() -> np.ndarray:
    N = 600
    x = jnp.linspace(-0.25, 0.25, N)

    # ---- SA parameters ----
    n_sa_iters = 60
    sigma_0 = 0.25          # perturbation scale (fraction of f_max)
    sigma_min = 0.01
    sigma_decay = 0.97
    T_anneal_0 = 0.004      # SA acceptance temperature
    T_anneal_decay = 0.94

    # ---- Initial convergence (exact sol03 hyperparams) ----
    n_seeds = 8
    base_lr = 0.005
    init_temps = [0.05, 0.01, 0.003, 0.001, 0.0003]
    init_steps_per_phase = 15000   # 5 × 15k = 75k per seed

    total_init_steps = len(init_temps) * init_steps_per_phase
    lr_schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=base_lr,
        warmup_steps=500,
        decay_steps=total_init_steps - 500,
        end_value=base_lr * 1e-3,
    )
    init_opt = optax.adam(learning_rate=lr_schedule)

    # ---- JIT-compiled Adam step ----
    @jax.jit
    def adam_step(raw_p, opt_st, temp):
        loss, grads = jax.value_and_grad(
            lambda p: smooth_compute_c_dyn(p, temp)
        )(raw_p)
        updates, new_st = init_opt.update(grads, opt_st, raw_p)
        return optax.apply_updates(raw_p, updates), new_st, loss

    # ---- JIT-compiled L-BFGS objective ----
    _lbfgs_temp = jnp.float32(0.001)  # cold temp for accurate inner landscape

    @jax.jit
    def lbfgs_obj_grad(raw_p):
        return jax.value_and_grad(
            lambda p: smooth_compute_c_dyn(p, _lbfgs_temp)
        )(raw_p)

    def run_lbfgs(raw_params_init, maxiter=300):
        """L-BFGS inner optimization for SA re-convergence."""
        x0 = np.array(raw_params_init, dtype=np.float64)

        def f_and_g(x):
            x_jax = jnp.array(x, dtype=jnp.float32)
            val, grad = lbfgs_obj_grad(x_jax)
            return float(val), np.array(grad, dtype=np.float64)

        result = minimize(
            f_and_g, x0, method='L-BFGS-B', jac=True,
            options={'maxiter': maxiter, 'ftol': 1e-14, 'gtol': 1e-8},
        )
        return jnp.array(result.x, dtype=jnp.float32)

    def run_adam_init(raw_params):
        """Full sol03-style Adam convergence."""
        opt_st = init_opt.init(raw_params)
        for temp_val in init_temps:
            temp = jnp.array(temp_val, dtype=jnp.float32)
            for _ in range(init_steps_per_phase):
                raw_params, opt_st, _ = adam_step(raw_params, opt_st, temp)
        return raw_params

    # ---- Phase 1: Multi-seed Adam convergence (sol03 style) ----
    seed_best_c = float('inf')
    seed_best_raw = None

    for seed in range(n_seeds):
        key = jax.random.PRNGKey(seed * 17 + 3)  # exact sol03 seeds
        pos = float(jax.random.uniform(key, (), minval=-0.15, maxval=0.15))
        width = float(jax.random.uniform(jax.random.fold_in(key, 1), (), minval=0.05, maxval=0.2))
        init_bump = jnp.exp(-((x - pos) ** 2) / (2 * width ** 2))
        noise = 0.05 * jax.random.normal(jax.random.fold_in(key, 2), (N,))
        raw_params = inv_softplus(jnp.clip(init_bump, 1e-4, None)) + noise

        raw_params = run_adam_init(raw_params)
        f_val = jax.nn.softplus(raw_params)
        c_val = float(compute_c(f_val))
        if c_val < seed_best_c:
            seed_best_c = c_val
            seed_best_raw = raw_params

    # Warm up L-BFGS JIT on a small problem to avoid cold-start timing issues
    _ = lbfgs_obj_grad(seed_best_raw)

    # ---- Phase 2: SA with L-BFGS inner optimization ----
    rng = np.random.default_rng(42)

    raw_current = seed_best_raw
    f_current = jax.nn.softplus(raw_current)
    c_current = float(compute_c(f_current))

    sa_best_c = c_current
    sa_best_raw = raw_current

    sigma = sigma_0
    T_anneal = T_anneal_0

    for sa_iter in range(n_sa_iters):
        # Perturb in function value space
        f_scale = float(jnp.max(f_current))
        pert_key = jax.random.PRNGKey(77777 + sa_iter)
        perturbation = sigma * f_scale * jax.random.normal(pert_key, (N,))
        f_perturbed = jnp.maximum(f_current + perturbation, 0.0)

        # Convert to raw params and re-optimize with L-BFGS
        raw_perturbed = inv_softplus(jnp.clip(f_perturbed, 1e-4, None))
        raw_new = run_lbfgs(raw_perturbed, maxiter=300)

        f_new = jax.nn.softplus(raw_new)
        c_new = float(compute_c(f_new))

        # SA acceptance
        delta_c = c_new - c_current
        accept = (delta_c < 0) or (rng.random() < float(np.exp(-delta_c / T_anneal)))
        if accept:
            raw_current = raw_new
            f_current = f_new
            c_current = c_new

        if c_current < sa_best_c:
            sa_best_c = c_current
            sa_best_raw = raw_current

        # Cool down
        sigma = max(sigma * sigma_decay, sigma_min)
        T_anneal *= T_anneal_decay

    return np.array(jax.nn.softplus(sa_best_raw))
