# fitness: TIMEOUT
# Approach: 3-stage coarse-to-fine + smooth-max, 12 restarts
# N=80 → N=200 → N=600. Fine stage uses 6-phase annealing with more steps.
# Key improvement over sol02: intermediate N=200 stage + 12 restarts + more fine steps (20k each)
# Targeting C < 1.505

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax
from helper import compute_c


def make_smooth_c(N):
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


def run_stage(raw_init, temps, steps_per_temp, peak_lr, end_lr):
    N = len(raw_init)
    smooth_c = make_smooth_c(N)
    total_steps = steps_per_temp * len(temps)
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0, peak_value=peak_lr,
        warmup_steps=min(400, total_steps // 15),
        decay_steps=total_steps, end_value=end_lr)
    optimizer = optax.adam(learning_rate=schedule)

    @jax.jit
    def step_fn(raw_params, temp, opt_state):
        loss, grads = jax.value_and_grad(smooth_c)(raw_params, temp)
        updates, new_opt_state = optimizer.update(grads, opt_state, raw_params)
        return optax.apply_updates(raw_params, updates), new_opt_state, loss

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
    N_coarse = 80
    N_mid = 200
    N_fine = 600
    num_restarts = 12

    # Stage 1: coarse — aggressive warm exploration
    temps_coarse = [0.1, 0.05, 0.02, 0.005, 0.001]   # 5 × 8k = 40k
    # Stage 2: mid — bridge from basin to fine structure
    temps_mid = [0.05, 0.02, 0.005, 0.001]            # 4 × 10k = 40k
    # Stage 3: fine — full warm-to-cold 6-phase annealing
    temps_fine = [0.05, 0.02, 0.007, 0.002, 0.0005, 0.0001]  # 6 × 20k = 120k

    best_c = float('inf')
    best_raw_fine = None
    x_coarse = jnp.linspace(-0.25, 0.25, N_coarse)

    for seed in range(num_restarts):
        key = jax.random.PRNGKey(seed * 37 + 11)

        # Multi-bump asymmetric init
        pos1 = jax.random.uniform(key, (), minval=-0.18, maxval=0.18)
        w1   = jax.random.uniform(jax.random.fold_in(key, 1), (), minval=0.03, maxval=0.18)
        bump1 = jnp.exp(-((x_coarse - pos1) ** 2) / (2 * w1 ** 2))

        pos2 = jax.random.uniform(jax.random.fold_in(key, 3), (), minval=-0.23, maxval=0.23)
        w2   = jax.random.uniform(jax.random.fold_in(key, 4), (), minval=0.02, maxval=0.12)
        amp2 = jax.random.uniform(jax.random.fold_in(key, 5), (), minval=0.1, maxval=1.0)
        bump2 = amp2 * jnp.exp(-((x_coarse - pos2) ** 2) / (2 * w2 ** 2))

        # Optional third small bump
        pos3 = jax.random.uniform(jax.random.fold_in(key, 6), (), minval=-0.24, maxval=0.24)
        w3   = jax.random.uniform(jax.random.fold_in(key, 7), (), minval=0.01, maxval=0.06)
        amp3 = jax.random.uniform(jax.random.fold_in(key, 8), (), minval=0.0, maxval=0.5)
        bump3 = amp3 * jnp.exp(-((x_coarse - pos3) ** 2) / (2 * w3 ** 2))

        noise = 0.04 * jax.random.normal(jax.random.fold_in(key, 2), (N_coarse,))
        init_f = jnp.clip(bump1 + bump2 + bump3, 1e-4, None)
        raw_coarse_init = jnp.log(jnp.expm1(init_f)) + noise

        # Stage 1: coarse
        raw_coarse = run_stage(raw_coarse_init, temps_coarse,
                               steps_per_temp=8000, peak_lr=0.01, end_lr=5e-5)

        # Stage 2: mid
        raw_mid = run_stage(upsample(raw_coarse, N_mid), temps_mid,
                            steps_per_temp=10000, peak_lr=0.007, end_lr=3e-5)

        # Stage 3: fine (warm start, full annealing)
        raw_fine = run_stage(upsample(raw_mid, N_fine), temps_fine,
                             steps_per_temp=20000, peak_lr=0.005, end_lr=5e-6)

        f_final = jax.nn.softplus(raw_fine)
        c_val = float(compute_c(f_final))
        print(f"[seed {seed}] C = {c_val:.6f}  (best = {best_c:.6f})")

        if c_val < best_c:
            best_c = c_val
            best_raw_fine = raw_fine

    print(f"Final best C = {best_c:.6f}")
    return np.array(jax.nn.softplus(best_raw_fine))
