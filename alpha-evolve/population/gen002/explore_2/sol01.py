# fitness: 1.5176
# Approach: Simulated Annealing (SA) wrapper around smooth-max Adam optimization
# Based on Boyer et al. Finding 4: SA escapes local minima that gradient descent can't reach.
#
# Key distinction:
#   - Smooth-max temperature (T_smooth): controls gradient spreading via log-sum-exp
#   - SA temperature (T_anneal): acceptance probability for worse C solutions
#
# Algorithm:
#   1. Run smooth-max Adam to local minimum (initial convergence)
#   2. Perturb function: f <- f + sigma * f_scale * N(0,1), clip >= 0
#   3. Re-optimize from perturbed point (short inner Adam run)
#   4. Accept if C improves, else accept with prob exp(-dC / T_anneal)
#   5. Decay sigma and T_anneal each SA iteration
#   6. Repeat from step 2 for n_sa_iters iterations
#   7. Multiple restarts with different random seeds

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax
from helper import compute_c


def smooth_compute_c_dyn(f_values, temp):
    """Smooth-max C with dynamic temperature (JAX-traceable — compiles once for all temps)."""
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
    # log-sum-exp is numerically stable even for small temp
    # as temp->0, this converges to true max
    smooth_max = temp * jax.scipy.special.logsumexp(scaled_conv / temp)
    return smooth_max / integral_f_sq


def inv_softplus(y):
    """Inverse softplus: x such that softplus(x) = y"""
    return jnp.log(jnp.expm1(jnp.clip(y, 1e-4, None)))


def entrypoint() -> np.ndarray:
    N = 600
    x = jnp.linspace(-0.25, 0.25, N)

    # ---- SA hyperparameters ----
    n_restarts = 2          # full SA restarts with different random seeds
    n_sa_iters = 40         # SA perturbation-reoptimize cycles per restart
    sigma_0 = 0.4           # initial perturbation scale (fraction of f_max)
    sigma_min = 0.02        # minimum perturbation scale
    sigma_decay = 0.97      # sigma cooling factor per SA step
    T_anneal_0 = 0.008      # initial SA acceptance temperature (in units of C)
    T_anneal_decay = 0.93   # SA temperature cooling per step

    # ---- Optimization hyperparameters ----
    base_lr = 0.005

    # Initial convergence: warm -> cold smooth-max schedule
    init_temps = [0.05, 0.01, 0.003, 0.001, 0.0003]  # 5 phases
    init_steps_per_phase = 5000                         # 25,000 total initial steps

    # SA inner re-optimization: start cold (tight landscape around perturbed point)
    inner_temps = [0.005, 0.001]   # 2 phases
    inner_steps_per_phase = 1500   # 3,000 total inner steps per SA iteration

    # ---- Build optimizers ----
    total_init_steps = len(init_temps) * init_steps_per_phase
    init_lr_schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=base_lr,
        warmup_steps=500,
        decay_steps=total_init_steps - 500,
        end_value=base_lr * 5e-4,
    )
    init_opt = optax.chain(
        optax.clip_by_global_norm(1.0),
        optax.adam(learning_rate=init_lr_schedule),
    )

    # Inner optimizer: constant LR (short burst, no warmup needed)
    inner_opt = optax.chain(
        optax.clip_by_global_norm(1.0),
        optax.adam(learning_rate=base_lr * 0.4),
    )

    # ---- JIT-compiled train steps (compiled once; temp is a dynamic arg) ----
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
        """Run initial convergence from raw_params (warm to cold smooth-max)."""
        opt_st = init_opt.init(raw_params)
        for temp_val in init_temps:
            temp = jnp.array(temp_val, dtype=jnp.float32)
            for _ in range(init_steps_per_phase):
                raw_params, opt_st, _ = init_step(raw_params, opt_st, temp)
        return raw_params

    def run_inner(raw_params):
        """Short re-optimization after SA perturbation (cold smooth-max)."""
        opt_st = inner_opt.init(raw_params)
        for temp_val in inner_temps:
            temp = jnp.array(temp_val, dtype=jnp.float32)
            for _ in range(inner_steps_per_phase):
                raw_params, opt_st, _ = inner_step(raw_params, opt_st, temp)
        return raw_params

    # ---- Main optimization loop ----
    global_best_c = float('inf')
    global_best_raw = None
    rng = np.random.default_rng(42)

    for restart in range(n_restarts):
        seed = restart * 13 + 7
        key = jax.random.PRNGKey(seed)

        # Random asymmetric initialization (same style as sol03)
        pos = float(jax.random.uniform(key, (), minval=-0.15, maxval=0.15))
        width = float(jax.random.uniform(jax.random.fold_in(key, 1), (), minval=0.05, maxval=0.2))
        init_bump = jnp.exp(-((x - pos) ** 2) / (2 * width ** 2))
        noise = 0.05 * jax.random.normal(jax.random.fold_in(key, 2), (N,))
        raw_params = inv_softplus(jnp.clip(init_bump, 1e-4, None)) + noise

        # Phase 1: Converge to local minimum
        raw_params = run_init(raw_params)
        f_current = jax.nn.softplus(raw_params)
        c_current = float(compute_c(f_current))
        raw_current = raw_params

        sa_best_c = c_current
        sa_best_raw = raw_current

        # Phase 2: Simulated Annealing around local minimum
        sigma = sigma_0
        T_anneal = T_anneal_0

        for sa_iter in range(n_sa_iters):
            # Perturb current function in value space
            f_scale = float(jnp.max(f_current))
            pert_key = jax.random.PRNGKey(seed * 10000 + sa_iter)
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

            # Track SA best
            if c_current < sa_best_c:
                sa_best_c = c_current
                sa_best_raw = raw_current

            # Cool down
            sigma = max(sigma * sigma_decay, sigma_min)
            T_anneal *= T_anneal_decay

        if sa_best_c < global_best_c:
            global_best_c = sa_best_c
            global_best_raw = sa_best_raw

    return np.array(jax.nn.softplus(global_best_raw))
