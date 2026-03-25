# fitness: 1.5162
# Approach: SA wrapper with sol03-quality initial convergence as starting point
# Fix for sol01: initial convergence was too weak (25k steps) → SA started from bad point
#
# Strategy:
#   1. Run 4 seeds with full sol03-style convergence (5 phases × 15k steps each = 75k/seed)
#   2. Keep best converged solution as SA starting point (should be ~1.511-1.513)
#   3. Run SA: 60 iterations, each with 6k inner re-optimization steps
#   4. SA inner temp schedule: [0.01, 0.003, 0.001] (start cold — near good solution)
#
# Result: 1.5162 — improved over sol01 (1.5176) but still below sol03 (1.5108)
# Root cause: 4 seeds insufficient; sol03 uses 8 seeds to find better basins
# Total: 4*75k + 60*6k = 300k + 360k = 660k steps ≈ 3 min

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax
from helper import compute_c


def smooth_compute_c_dyn(f_values, temp):
    """Smooth-max C with dynamic temperature (JAX-traceable — compiles once)."""
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
    """Inverse softplus: x such that softplus(x) = y"""
    return jnp.log(jnp.expm1(jnp.clip(y, 1e-4, None)))


def entrypoint() -> np.ndarray:
    N = 600
    x = jnp.linspace(-0.25, 0.25, N)

    # ---- SA hyperparameters ----
    n_sa_iters = 60         # SA perturbation-reoptimize cycles
    sigma_0 = 0.35          # initial perturbation scale (fraction of f_max)
    sigma_min = 0.015       # minimum perturbation scale
    sigma_decay = 0.97      # sigma cooling factor per SA step
    T_anneal_0 = 0.006      # initial SA acceptance temperature (in units of C)
    T_anneal_decay = 0.94   # SA temperature cooling per step

    # ---- Initial convergence (sol03-style) ----
    n_init_seeds = 4
    init_base_lr = 0.005
    # Same 5-phase smooth-max schedule as sol03
    init_temps = [0.05, 0.01, 0.003, 0.001, 0.0003]
    init_steps_per_phase = 15000   # 5 phases × 15k = 75k steps per seed (same as sol03)

    # ---- SA inner re-optimization ----
    inner_base_lr = 0.002          # lower LR: fine-tuning near convergence
    # Start cold — no need to warm up since we're near a good basin
    inner_temps = [0.01, 0.003, 0.001]
    inner_steps_per_phase = 2000   # 3 phases × 2k = 6k steps per SA iteration

    # ---- Build optimizers ----
    total_init_steps = len(init_temps) * init_steps_per_phase
    init_lr_schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=init_base_lr,
        warmup_steps=500,
        decay_steps=total_init_steps - 500,
        end_value=init_base_lr * 1e-3,
    )
    init_opt = optax.adam(learning_rate=init_lr_schedule)

    # Inner optimizer: constant LR (short focused bursts)
    inner_opt = optax.adam(learning_rate=inner_base_lr)

    # ---- JIT-compiled train steps (temp as dynamic arg → compiles once) ----
    @jax.jit
    def init_step(raw_p, opt_st, temp):
        loss, grads = jax.value_and_grad(
            lambda p: smooth_compute_c_dyn(p, temp)
        )(raw_p)
        updates, new_st = init_opt.update(grads, opt_st, raw_p)
        return optax.apply_updates(raw_p, updates), new_st, loss

    @jax.jit
    def inner_step(raw_p, opt_st, temp):
        loss, grads = jax.value_and_grad(
            lambda p: smooth_compute_c_dyn(p, temp)
        )(raw_p)
        updates, new_st = inner_opt.update(grads, opt_st, raw_p)
        return optax.apply_updates(raw_p, updates), new_st, loss

    def run_init(raw_params):
        """Full sol03-style convergence from raw_params."""
        opt_st = init_opt.init(raw_params)
        for temp_val in init_temps:
            temp = jnp.array(temp_val, dtype=jnp.float32)
            for _ in range(init_steps_per_phase):
                raw_params, opt_st, _ = init_step(raw_params, opt_st, temp)
        return raw_params

    def run_inner(raw_params):
        """Short re-optimization after SA perturbation (cold start)."""
        opt_st = inner_opt.init(raw_params)
        for temp_val in inner_temps:
            temp = jnp.array(temp_val, dtype=jnp.float32)
            for _ in range(inner_steps_per_phase):
                raw_params, opt_st, _ = inner_step(raw_params, opt_st, temp)
        return raw_params

    # ---- Phase 1: Multi-seed initial convergence ----
    seed_best_c = float('inf')
    seed_best_raw = None

    for seed in range(n_init_seeds):
        key = jax.random.PRNGKey(seed * 17 + 3)  # same seeds as sol03
        pos = float(jax.random.uniform(key, (), minval=-0.15, maxval=0.15))
        width = float(jax.random.uniform(jax.random.fold_in(key, 1), (), minval=0.05, maxval=0.2))
        init_bump = jnp.exp(-((x - pos) ** 2) / (2 * width ** 2))
        noise = 0.05 * jax.random.normal(jax.random.fold_in(key, 2), (N,))
        raw_params = inv_softplus(jnp.clip(init_bump, 1e-4, None)) + noise

        raw_params = run_init(raw_params)
        f_val = jax.nn.softplus(raw_params)
        c_val = float(compute_c(f_val))
        if c_val < seed_best_c:
            seed_best_c = c_val
            seed_best_raw = raw_params

    # ---- Phase 2: SA from the best converged seed ----
    rng = np.random.default_rng(42)

    raw_current = seed_best_raw
    f_current = jax.nn.softplus(raw_current)
    c_current = float(compute_c(f_current))

    sa_best_c = c_current
    sa_best_raw = raw_current

    sigma = sigma_0
    T_anneal = T_anneal_0

    for sa_iter in range(n_sa_iters):
        # Perturb current function in value space
        f_scale = float(jnp.max(f_current))
        pert_key = jax.random.PRNGKey(9999 + sa_iter)
        perturbation = sigma * f_scale * jax.random.normal(pert_key, (N,))
        f_perturbed = jnp.maximum(f_current + perturbation, 0.0)

        # Map to parameter space and re-optimize
        raw_perturbed = inv_softplus(jnp.clip(f_perturbed, 1e-4, None))
        raw_new = run_inner(raw_perturbed)

        f_new = jax.nn.softplus(raw_new)
        c_new = float(compute_c(f_new))

        # SA acceptance criterion
        delta_c = c_new - c_current
        accept = (delta_c < 0) or (rng.random() < float(np.exp(-delta_c / T_anneal)))
        if accept:
            raw_current = raw_new
            f_current = f_new
            c_current = c_new

        # Track SA-global best (not just current trajectory)
        if c_current < sa_best_c:
            sa_best_c = c_current
            sa_best_raw = raw_current

        # Cool down
        sigma = max(sigma * sigma_decay, sigma_min)
        T_anneal *= T_anneal_decay

    return np.array(jax.nn.softplus(sa_best_raw))
