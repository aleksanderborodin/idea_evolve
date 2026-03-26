# fitness: 1.5092
# Approach: Basin-hopping at coarse scale + diverse inits — 25 coarse seeds, top-5 → fine
# Hypothesis: 8-12 seeds at coarse stage is underpowered. With 25 diverse seeds,
#   we cast a wider net over the N=80 basin landscape.
# Strategy: 25 short coarse runs (arcsine + Gaussian + comb variants), keep top-5,
#   run full 3-stage warm fine on each of the 5.

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


def make_arcsine_init(x, a, b, tilt_low, tilt_high, key):
    eps = 1e-5
    in_interval = (x >= a) & (x <= b)
    denom = jnp.sqrt(jnp.maximum((x - a) * (b - x), eps))
    shape = jnp.where(in_interval, 1.0 / denom, 0.0)
    shape = shape / (jnp.max(shape) + 1e-8) + 0.05
    tilt = jnp.linspace(tilt_low, tilt_high, len(x))
    f = jnp.clip(shape + tilt, 1e-4, None)
    noise = 0.03 * jax.random.normal(key, x.shape)
    return jnp.log(jnp.expm1(f)) + noise


def make_gaussian_init(x, key):
    pos1 = jax.random.uniform(key, (), minval=-0.18, maxval=0.18)
    w1 = jax.random.uniform(jax.random.fold_in(key, 1), (), minval=0.03, maxval=0.18)
    bump1 = jnp.exp(-((x - pos1) ** 2) / (2 * w1 ** 2))
    pos2 = jax.random.uniform(jax.random.fold_in(key, 3), (), minval=-0.23, maxval=0.23)
    w2 = jax.random.uniform(jax.random.fold_in(key, 4), (), minval=0.02, maxval=0.12)
    amp2 = jax.random.uniform(jax.random.fold_in(key, 5), (), minval=0.15, maxval=1.0)
    bump2 = amp2 * jnp.exp(-((x - pos2) ** 2) / (2 * w2 ** 2))
    noise = 0.04 * jax.random.normal(jax.random.fold_in(key, 2), x.shape)
    f = jnp.clip(bump1 + bump2, 1e-4, None)
    return jnp.log(jnp.expm1(f)) + noise


def make_comb_init(x, n_peaks, amps, width, tilt_dir, key):
    positions = jnp.linspace(-0.20, 0.20, n_peaks)
    f = jnp.zeros_like(x)
    for i in range(n_peaks):
        f = f + amps[i] * jnp.exp(-((x - positions[i]) ** 2) / (2 * width ** 2))
    tilt = jnp.linspace(0.05, 0.3, len(x)) if tilt_dir > 0 else jnp.linspace(0.3, 0.05, len(x))
    f = jnp.clip(f + tilt, 1e-4, None)
    noise = 0.03 * jax.random.normal(key, x.shape)
    return jnp.log(jnp.expm1(f)) + noise


def entrypoint() -> np.ndarray:
    N_coarse = 80
    N_fine = 600

    # Short coarse runs: 4 temps × 4k = 16k steps each (fast exploration)
    temps_coarse_short = [0.1, 0.05, 0.01, 0.003]

    # Full fine stage: 5 temps × 15k = 75k steps (warm start mandatory)
    temps_fine = [0.05, 0.01, 0.003, 0.001, 0.0003]

    x_coarse = jnp.linspace(-0.25, 0.25, N_coarse)

    # 25 diverse coarse seeds
    coarse_inits = []

    # Arcsine family: 12 seeds exploring the [-0.05, 0.22] basin neighborhood
    arcsine_configs = [
        (-0.05, 0.22, 0.10, 0.50),
        (-0.05, 0.22, 0.08, 0.42),
        (-0.05, 0.22, 0.12, 0.55),
        (-0.05, 0.22, 0.05, 0.65),
        (-0.05, 0.22, 0.20, 0.60),
        (-0.07, 0.22, 0.10, 0.50),
        (-0.03, 0.22, 0.10, 0.50),
        (-0.05, 0.21, 0.10, 0.50),
        (-0.05, 0.23, 0.10, 0.50),
        (-0.22, 0.05, 0.50, 0.10),  # mirror variants
        (-0.22, 0.05, 0.42, 0.08),
        (-0.22, 0.05, 0.55, 0.12),
    ]
    for s, (a, b, tl, th) in enumerate(arcsine_configs):
        key = jax.random.PRNGKey(s * 97 + 13)
        coarse_inits.append(('arcsine', make_arcsine_init(x_coarse, a, b, tl, th, key)))

    # Gaussian family: 8 random seeds
    for s in range(8):
        key = jax.random.PRNGKey(s * 31 + 77)
        coarse_inits.append(('gauss', make_gaussian_init(x_coarse, key)))

    # Comb family: 5 variants
    comb_configs = [
        (4, [0.2, 0.5, 0.8, 1.5], 0.025, +1),
        (4, [1.5, 0.8, 0.5, 0.2], 0.025, -1),
        (4, [0.3, 0.4, 1.2, 1.0], 0.030, +1),
        (5, [0.2, 0.6, 1.4, 0.8, 0.3], 0.020, +1),
        (3, [1.5, 0.4, 0.8], 0.040, -1),
    ]
    for s, (n_peaks, amps, width, tilt_dir) in enumerate(comb_configs):
        key = jax.random.PRNGKey(s * 53 + 29)
        coarse_inits.append(('comb', make_comb_init(x_coarse, n_peaks, jnp.array(amps), width, tilt_dir, key)))

    print(f"Running {len(coarse_inits)} coarse seeds...")

    # Phase 1: Short coarse optimization for all 25 seeds
    coarse_results = []
    for i, (family, raw_init) in enumerate(coarse_inits):
        raw_c = run_stage(raw_init, temps_coarse_short,
                          steps_per_temp=4000, peak_lr=0.012, end_lr=1e-4)
        f_coarse = jax.nn.softplus(raw_c)
        c_coarse = float(compute_c(f_coarse))
        coarse_results.append((c_coarse, raw_c, family, i))
        if i % 5 == 0:
            print(f"  Coarse {i+1}/{len(coarse_inits)}: C={c_coarse:.4f} ({family})")

    # Sort and keep top-5 coarse solutions
    coarse_results.sort(key=lambda x: x[0])
    top5 = coarse_results[:5]
    print(f"\nTop-5 coarse solutions:")
    for rank, (c_c, _, fam, idx) in enumerate(top5):
        print(f"  rank {rank+1}: C={c_c:.6f} ({fam}, seed {idx})")

    # Phase 2: Full fine optimization on top-5
    best_c = float('inf')
    best_raw_fine = None

    for rank, (c_coarse, raw_c, family, idx) in enumerate(top5):
        raw_fine_init = upsample(raw_c, N_fine)
        raw_f = run_stage(raw_fine_init, temps_fine,
                          steps_per_temp=15000, peak_lr=0.006, end_lr=1e-5)
        f_final = jax.nn.softplus(raw_f)
        c_val = float(compute_c(f_final))
        print(f"[fine rank {rank+1}: {family} seed {idx}] coarse={c_coarse:.4f} → fine C={c_val:.6f}  (best={best_c:.6f})")

        if c_val < best_c:
            best_c = c_val
            best_raw_fine = raw_f

    print(f"\nFinal best: C = {best_c:.6f}")
    return np.array(jax.nn.softplus(best_raw_fine))
