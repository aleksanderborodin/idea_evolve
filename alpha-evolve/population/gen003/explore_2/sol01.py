# fitness: 1.5090
# Approach: Diverse coarse initialization comparison — 3 families × 2 seeds each
# Hypothesis: Gaussian-bump inits all converge to same ~1.509 basin.
# Comb / step / arcsine inits may find different basins via coarse-to-fine + warm smooth-max.
# Families: (A) Comb (narrow asymmetric peaks), (B) Step function, (C) Arcsine-weighted
# 6 total seeds → upsample best to N=600 → warm fine-tuning (starts T=0.05)

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


def make_comb_init(x, seed_offset, noise_key):
    """Comb: 4-5 narrow peaks at evenly-spaced positions, deliberately asymmetric amplitudes."""
    n_peaks = 4
    positions = jnp.linspace(-0.20, 0.20, n_peaks)
    # Asymmetric: amplitudes monotonically increasing (seed_offset=0) or random (seed_offset=1)
    if seed_offset == 0:
        amps = jnp.array([0.2, 0.5, 0.8, 1.5])
    else:
        amps = jnp.array([1.5, 0.3, 1.0, 0.6])
    width = 0.025
    f = jnp.zeros_like(x)
    for i in range(n_peaks):
        f = f + amps[i] * jnp.exp(-((x - positions[i]) ** 2) / (2 * width ** 2))
    # Add asymmetric baseline tilt
    tilt = jnp.linspace(0.05, 0.3, len(x)) if seed_offset == 0 else jnp.linspace(0.3, 0.05, len(x))
    f = f + tilt
    noise = 0.03 * jax.random.normal(noise_key, x.shape)
    f = jnp.clip(f, 1e-4, None)
    return jnp.log(jnp.expm1(f)) + noise


def make_step_init(x, seed_offset, noise_key):
    """Step function: piecewise constant with 8 segments, random heights — strongly asymmetric."""
    n_steps = 8
    # Different height profiles for the two seeds
    if seed_offset == 0:
        # Ramping step: increasing heights toward right
        heights = jnp.array([0.05, 0.1, 0.3, 0.8, 1.5, 1.0, 0.4, 0.15])
    else:
        # Bimodal step: two tall regions with valley in middle
        heights = jnp.array([0.8, 1.2, 0.2, 0.05, 0.05, 0.3, 1.5, 0.9])
    step_width = 0.5 / n_steps  # total domain = 0.5
    x_min = -0.25
    f = jnp.zeros_like(x)
    for i in range(n_steps):
        left = x_min + i * step_width
        right = left + step_width
        mask = (x >= left) & (x < right)
        f = f + heights[i] * mask.astype(jnp.float32)
    # Smooth slightly (avoid sharp steps causing init issues)
    f = jnp.clip(f, 1e-4, None)
    noise = 0.04 * jax.random.normal(noise_key, x.shape)
    return jnp.log(jnp.expm1(f)) + noise


def make_arcsine_init(x, seed_offset, noise_key):
    """Arcsine-weighted: high mass near edges of a subinterval, low in the middle.
    Approximates the arcsin distribution on [a, b] ⊂ [-0.25, 0.25].
    This is the equilibrium measure for Chebyshev-type problems — may have special properties.
    """
    if seed_offset == 0:
        # Subinterval biased toward positive x (asymmetric)
        a, b = -0.05, 0.22
    else:
        # Subinterval biased toward negative x
        a, b = -0.20, 0.08
    eps = 1e-4
    # f ~ 1/sqrt((x-a)(b-x)) on [a,b], 0 outside — clipped for positivity
    in_interval = (x >= a) & (x <= b)
    denom = jnp.sqrt(jnp.maximum((x - a) * (b - x), eps))
    arcsine_shape = jnp.where(in_interval, 1.0 / denom, 0.0)
    # Normalize to have max ~1 and add small baseline
    arcsine_shape = arcsine_shape / (jnp.max(arcsine_shape) + 1e-8) + 0.05
    # The shape is symmetric within its subinterval — break symmetry with tilt
    if seed_offset == 0:
        tilt = jnp.linspace(0.1, 0.5, len(x))
    else:
        tilt = jnp.linspace(0.5, 0.1, len(x))
    f = arcsine_shape + tilt
    f = jnp.clip(f, 1e-4, None)
    noise = 0.03 * jax.random.normal(noise_key, x.shape)
    return jnp.log(jnp.expm1(f)) + noise


def entrypoint() -> np.ndarray:
    N_coarse = 80
    N_fine = 600

    # Coarse stage: warm exploration (cheap at N=80)
    temps_coarse = [0.1, 0.05, 0.01, 0.003]  # 4 temps × 6k = 24k steps

    # Fine stage: warm-to-cold annealing (MUST start warm T=0.05)
    temps_fine = [0.05, 0.01, 0.003, 0.001, 0.0003]  # 5 temps × 12k = 60k steps

    x_coarse = jnp.linspace(-0.25, 0.25, N_coarse)

    families = [
        ('comb', make_comb_init),
        ('step', make_step_init),
        ('arcsine', make_arcsine_init),
    ]

    best_c = float('inf')
    best_raw_fine = None
    best_family = None

    family_results = {}

    for family_name, init_fn in families:
        family_best_c = float('inf')
        for seed_offset in range(2):
            key = jax.random.PRNGKey(seed_offset * 100 + hash(family_name) % 97)
            noise_key = jax.random.fold_in(key, 999)

            raw_coarse_init = init_fn(x_coarse, seed_offset, noise_key)

            # Stage 1: coarse optimization
            raw_coarse = run_stage(raw_coarse_init, temps_coarse,
                                   steps_per_temp=6000, peak_lr=0.012, end_lr=1e-4)

            # Upsample to fine
            raw_fine_init = upsample(raw_coarse, N_fine)

            # Stage 2: fine with WARM start
            raw_fine = run_stage(raw_fine_init, temps_fine,
                                 steps_per_temp=12000, peak_lr=0.006, end_lr=1e-5)

            f_final = jax.nn.softplus(raw_fine)
            c_val = float(compute_c(f_final))
            print(f"[{family_name} seed {seed_offset}] C = {c_val:.6f}  (global best = {best_c:.6f})")

            if c_val < family_best_c:
                family_best_c = c_val

            if c_val < best_c:
                best_c = c_val
                best_raw_fine = raw_fine
                best_family = family_name

        family_results[family_name] = family_best_c
        print(f"  >> {family_name} family best: {family_best_c:.6f}")

    print(f"\nFamily summary:")
    for name, score in sorted(family_results.items(), key=lambda x: x[1]):
        print(f"  {name}: {score:.6f}")
    print(f"Overall best: C = {best_c:.6f} from {best_family}")

    return np.array(jax.nn.softplus(best_raw_fine))
