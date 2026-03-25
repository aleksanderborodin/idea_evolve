# fitness: 1.5188
# Approach: coarse-to-fine + smooth-max (log-sum-exp annealing)
# Stage 1: N=40, 6 restarts, warm smooth-max T=0.1→0.003, finds global basin
# Stage 2: upsample to N=150, T=0.005→0.0005, refines basin structure
# Stage 3: upsample to N=600, T=0.001→0.00003, precision refinement
# Key insight: smooth-max at coarse stage spreads gradient signal,
# preventing basin-locking that killed vanilla multi-scale in gen1 (1.5270-1.5730)

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax
from helper import compute_c


def make_smooth_c(N):
    """Create a smooth-max compute_c for array of length N.
    temp is passed as a dynamic (traced) arg — compiled once per N."""
    def _fn(raw_params, temp):
        domain_width = 0.5
        dx = domain_width / N
        f_nn = jax.nn.softplus(raw_params)
        integral_f = jnp.sum(f_nn) * dx
        integral_f_sq = jnp.maximum(integral_f ** 2, 1e-9)
        padded_f = jnp.pad(f_nn, (0, N))
        fft_f = jnp.fft.fft(padded_f)
        conv_f_f = jnp.fft.ifft(fft_f * fft_f).real
        scaled_conv = conv_f_f * dx
        smooth_max = temp * jax.scipy.special.logsumexp(scaled_conv / temp)
        return smooth_max / integral_f_sq
    return _fn


def make_train_step(N, optimizer):
    """Create JIT'd train step for a given N."""
    smooth_c = make_smooth_c(N)

    @jax.jit
    def step(raw_params, temp, opt_state):
        loss, grads = jax.value_and_grad(smooth_c)(raw_params, temp)
        updates, new_opt_state = optimizer.update(grads, opt_state, raw_params)
        new_raw = optax.apply_updates(raw_params, updates)
        return new_raw, new_opt_state, loss

    return step


def run_stage(raw_init, temps, steps_per_temp, peak_lr, end_lr):
    """One stage: temperature-annealed smooth-max with Adam."""
    N = len(raw_init)
    total_steps = steps_per_temp * len(temps)
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0, peak_value=peak_lr,
        warmup_steps=min(300, total_steps // 15),
        decay_steps=total_steps, end_value=end_lr)
    optimizer = optax.adam(learning_rate=schedule)
    step_fn = make_train_step(N, optimizer)

    opt_state = optimizer.init(raw_init)
    raw_params = raw_init

    for temp in temps:
        t = jnp.array(temp, dtype=jnp.float32)
        for _ in range(steps_per_temp):
            raw_params, opt_state, _ = step_fn(raw_params, t, opt_state)

    return raw_params


def upsample(raw_coarse, N_fine):
    N_coarse = len(raw_coarse)
    x_coarse = jnp.linspace(0, 1, N_coarse)
    x_fine = jnp.linspace(0, 1, N_fine)
    return jnp.interp(x_fine, x_coarse, raw_coarse)


def entrypoint() -> np.ndarray:
    N_coarse = 40
    N_mid = 150
    N_fine = 600
    num_restarts = 6

    temps_coarse = [0.1, 0.03, 0.01, 0.003]          # 4 temps × 10k = 40k steps
    temps_mid    = [0.005, 0.002, 0.0005]              # 3 temps × 12k = 36k steps
    temps_fine   = [0.001, 0.0003, 0.0001, 0.00003]   # 4 temps × 15k = 60k steps

    best_c = float('inf')
    best_raw_fine = None
    x_coarse = jnp.linspace(-0.25, 0.25, N_coarse)

    for seed in range(num_restarts):
        key = jax.random.PRNGKey(seed * 31 + 7)

        # Two-bump asymmetric init
        pos1 = jax.random.uniform(key, (), minval=-0.15, maxval=0.15)
        w1   = jax.random.uniform(jax.random.fold_in(key, 1), (), minval=0.04, maxval=0.15)
        pos2 = jax.random.uniform(jax.random.fold_in(key, 3), (), minval=-0.2, maxval=0.2)
        w2   = jax.random.uniform(jax.random.fold_in(key, 4), (), minval=0.02, maxval=0.1)
        amp2 = jax.random.uniform(jax.random.fold_in(key, 5), (), minval=0.2, maxval=0.9)
        bump1 = jnp.exp(-((x_coarse - pos1) ** 2) / (2 * w1 ** 2))
        bump2 = amp2 * jnp.exp(-((x_coarse - pos2) ** 2) / (2 * w2 ** 2))
        noise = 0.05 * jax.random.normal(jax.random.fold_in(key, 2), (N_coarse,))
        init_f = jnp.clip(bump1 + bump2, 1e-4, None)
        raw_coarse_init = jnp.log(jnp.expm1(init_f)) + noise

        # Stage 1: coarse — warm smooth-max finds correct global basin
        raw_coarse = run_stage(raw_coarse_init, temps_coarse,
                               steps_per_temp=10000, peak_lr=0.01, end_lr=5e-5)

        # Stage 2: mid — refine basin structure
        raw_mid = run_stage(upsample(raw_coarse, N_mid), temps_mid,
                            steps_per_temp=12000, peak_lr=0.005, end_lr=3e-5)

        # Stage 3: fine — precision annealing
        raw_fine = run_stage(upsample(raw_mid, N_fine), temps_fine,
                             steps_per_temp=15000, peak_lr=0.003, end_lr=1e-5)

        f_final = jax.nn.softplus(raw_fine)
        c_val = float(compute_c(f_final))
        print(f"[seed {seed}] C = {c_val:.6f}  (best = {best_c:.6f})")

        if c_val < best_c:
            best_c = c_val
            best_raw_fine = raw_fine

    print(f"Final best C = {best_c:.6f}")
    return np.array(jax.nn.softplus(best_raw_fine))
