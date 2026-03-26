# fitness: 1.5091
# Approach: Arcsine init winner deep-dive — 3-stage pipeline + 12 seeds
# Best from sol01: arcsine on [-0.05, 0.22] gave C=1.508974 (NEW BEST)
# Strategy: 3 stages (N=80→N=200→N=600), all warm starts.
# Vary subinterval around the winning region to find optimal [a,b].
# 12 seeds across the (a,b) space near [-0.05, 0.22].

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


def make_arcsine_init(x, a, b, tilt_low, tilt_high, noise_key, noise_scale=0.03):
    """Arcsine-weighted init: U-shape on [a, b] with linear tilt."""
    eps = 1e-5
    in_interval = (x >= a) & (x <= b)
    denom = jnp.sqrt(jnp.maximum((x - a) * (b - x), eps))
    arcsine_shape = jnp.where(in_interval, 1.0 / denom, 0.0)
    arcsine_shape = arcsine_shape / (jnp.max(arcsine_shape) + 1e-8) + 0.05
    tilt = jnp.linspace(tilt_low, tilt_high, len(x))
    f = arcsine_shape + tilt
    f = jnp.clip(f, 1e-4, None)
    noise = noise_scale * jax.random.normal(noise_key, x.shape)
    return jnp.log(jnp.expm1(f)) + noise


def entrypoint() -> np.ndarray:
    N_coarse = 80
    N_mid = 200
    N_fine = 600

    # 3-stage warm pipeline
    temps_coarse = [0.1, 0.05, 0.01, 0.003]      # 4 × 6k = 24k
    temps_mid =    [0.05, 0.01, 0.003]             # 3 × 8k = 24k
    temps_fine =   [0.05, 0.01, 0.003, 0.001, 0.0003]  # 5 × 14k = 70k

    x_coarse = jnp.linspace(-0.25, 0.25, N_coarse)

    # Sweep around the winning region: a near [-0.10, 0.00], b near [0.18, 0.24]
    # Also include the exact sol01 winner and mirror-image variants
    # Format: (a, b, tilt_low, tilt_high, seed)
    configs = [
        # Winning region from sol01
        (-0.05, 0.22, 0.10, 0.50, 0),   # ~sol01 winner
        (-0.05, 0.22, 0.08, 0.45, 1),   # slightly different tilt
        (-0.05, 0.22, 0.15, 0.55, 2),   # stronger tilt
        (-0.05, 0.22, 0.05, 0.60, 3),   # extreme tilt
        # Shift a leftward
        (-0.08, 0.22, 0.10, 0.50, 4),
        (-0.03, 0.22, 0.10, 0.50, 5),
        # Shift b
        (-0.05, 0.20, 0.10, 0.50, 6),
        (-0.05, 0.24, 0.10, 0.50, 7),
        # Mirror variants (a=-0.22, b=0.05 was 2nd best in sol02)
        (-0.22, 0.05, 0.50, 0.10, 8),   # mirror, inverted tilt
        (-0.22, 0.05, 0.45, 0.08, 9),   # slight variation
        # Wider interval
        (-0.12, 0.22, 0.10, 0.50, 10),
        (-0.05, 0.18, 0.10, 0.50, 11),
    ]

    best_c = float('inf')
    best_raw_fine = None
    best_config = None

    for i, (a, b, tl, th, seed) in enumerate(configs):
        noise_key = jax.random.PRNGKey(seed * 131 + 17)

        raw_init = make_arcsine_init(x_coarse, a, b, tl, th, noise_key)

        # Stage 1: coarse
        raw_c = run_stage(raw_init, temps_coarse,
                          steps_per_temp=6000, peak_lr=0.012, end_lr=1e-4)

        # Stage 2: mid (warm)
        raw_m = run_stage(upsample(raw_c, N_mid), temps_mid,
                          steps_per_temp=8000, peak_lr=0.008, end_lr=5e-5)

        # Stage 3: fine (warm)
        raw_f = run_stage(upsample(raw_m, N_fine), temps_fine,
                          steps_per_temp=14000, peak_lr=0.006, end_lr=1e-5)

        f_final = jax.nn.softplus(raw_f)
        c_val = float(compute_c(f_final))
        print(f"[cfg {i:2d}: a={a:.2f} b={b:.2f} tilt={tl:.2f}→{th:.2f}] C = {c_val:.6f}  (best = {best_c:.6f})")

        if c_val < best_c:
            best_c = c_val
            best_raw_fine = raw_f
            best_config = (a, b, tl, th)

    print(f"\nBest: a={best_config[0]:.2f} b={best_config[1]:.2f} tilt={best_config[2]:.2f}→{best_config[3]:.2f} → C = {best_c:.6f}")
    return np.array(jax.nn.softplus(best_raw_fine))
