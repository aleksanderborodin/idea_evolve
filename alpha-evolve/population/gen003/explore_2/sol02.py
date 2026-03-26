# fitness: 1.5102
# Approach: Arcsine-family deep dive — 10 seeds with varied subinterval parameters
# Finding: sol01 arcsine seed 0 (subinterval [-0.05, 0.22]) gave C=1.508974, beating 1.5091 best.
# Now: expand arcsine family with 10 diverse subinterval configs + longer fine optimization.
# Key insight: arcsine on [a,b] creates U-shape (peaks at edges) → natural asymmetric bimodal init.
# Different [a,b] placements sweep different topological basins.

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


def make_arcsine_init(x, a, b, tilt_direction, noise_key, noise_scale=0.03):
    """Arcsine-weighted init on subinterval [a, b].
    Creates U-shaped profile (peaks at a and b) — a natural asymmetric bimodal init.
    tilt_direction: +1 → tilt toward positive x; -1 → tilt toward negative x.
    """
    eps = 1e-5
    in_interval = (x >= a) & (x <= b)
    denom = jnp.sqrt(jnp.maximum((x - a) * (b - x), eps))
    arcsine_shape = jnp.where(in_interval, 1.0 / denom, 0.0)
    # Normalize so max = 1
    arcsine_shape = arcsine_shape / (jnp.max(arcsine_shape) + 1e-8)
    # Add small positive baseline so function is non-zero everywhere
    arcsine_shape = arcsine_shape + 0.05
    # Asymmetric tilt to break left-right symmetry
    if tilt_direction > 0:
        tilt = jnp.linspace(0.05, 0.4, len(x))
    else:
        tilt = jnp.linspace(0.4, 0.05, len(x))
    f = arcsine_shape + tilt
    f = jnp.clip(f, 1e-4, None)
    noise = noise_scale * jax.random.normal(noise_key, x.shape)
    return jnp.log(jnp.expm1(f)) + noise


def entrypoint() -> np.ndarray:
    N_coarse = 80
    N_fine = 600

    # Coarse stage: warm exploration
    temps_coarse = [0.1, 0.05, 0.01, 0.003]  # 4 × 6k = 24k steps

    # Fine stage: longer warm-to-cold (MUST start warm T=0.05)
    temps_fine = [0.05, 0.01, 0.003, 0.001, 0.0003]  # 5 × 15k = 75k steps

    x_coarse = jnp.linspace(-0.25, 0.25, N_coarse)

    # 10 arcsine configurations covering different subinterval positions and tilts
    # Format: (a, b, tilt_direction, seed_key)
    configs = [
        # Positive-biased subintervals (best from sol01 was [-0.05, 0.22])
        (-0.05, 0.22,  +1, 0),   # sol01 winner
        (-0.05, 0.22,  -1, 1),   # same interval, opposite tilt
        (-0.10, 0.22,  +1, 2),   # slightly wider, shift left
        (-0.02, 0.24,  +1, 3),   # right-shifted, near boundary
        ( 0.00, 0.24,  +1, 4),   # entirely positive domain
        # Negative-biased subintervals
        (-0.22, 0.05,  -1, 5),   # mirror of best
        (-0.24, 0.02,  -1, 6),   # near left boundary
        # Wide subintervals (nearly full domain)
        (-0.20, 0.22,  +1, 7),   # wide, near-full coverage
        (-0.22, 0.20,  -1, 8),   # wide, opposite tilt
        # Asymmetric narrow (one U-lobe near center, one near edge)
        (-0.10, 0.15,  +1, 9),   # narrow, centered-right
    ]

    best_c = float('inf')
    best_raw_fine = None
    best_config_idx = None

    for i, (a, b, tilt, seed) in enumerate(configs):
        noise_key = jax.random.PRNGKey(seed * 137 + 42)

        raw_coarse_init = make_arcsine_init(x_coarse, a, b, tilt, noise_key)

        # Stage 1: coarse
        raw_coarse = run_stage(raw_coarse_init, temps_coarse,
                               steps_per_temp=6000, peak_lr=0.012, end_lr=1e-4)

        # Upsample to fine
        raw_fine_init = upsample(raw_coarse, N_fine)

        # Stage 2: fine with WARM start
        raw_fine = run_stage(raw_fine_init, temps_fine,
                             steps_per_temp=15000, peak_lr=0.006, end_lr=1e-5)

        f_final = jax.nn.softplus(raw_fine)
        c_val = float(compute_c(f_final))
        print(f"[config {i:2d}: a={a:.2f} b={b:.2f} tilt={'+'if tilt>0 else '-'}] C = {c_val:.6f}  (best = {best_c:.6f})")

        if c_val < best_c:
            best_c = c_val
            best_raw_fine = raw_fine
            best_config_idx = i

    a_best, b_best, t_best, _ = configs[best_config_idx]
    print(f"\nBest: config {best_config_idx} (a={a_best:.2f}, b={b_best:.2f}, tilt={'+'if t_best>0 else '-'}) → C = {best_c:.6f}")
    return np.array(jax.nn.softplus(best_raw_fine))
