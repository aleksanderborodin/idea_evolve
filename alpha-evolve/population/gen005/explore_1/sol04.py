# fitness: 1.5418
# Approach: Gaussian mixture parameterization — represent f as sum of N_PEAKS learnable
#   Gaussian peaks with learnable positions, widths, and amplitudes.
# This is a STRUCTURAL DEPARTURE from the grid-point parameterization used in all prior solutions.
# Key insight: gradient descent can move peak positions, not just heights. This allows
#   qualitatively different function shapes to be discovered.
# Prior approach: optimize 600 grid values (high-dim, constrained to grid)
# This approach: optimize 3*N_PEAKS parameters in continuous function space
# After optimization, evaluate on N=600 grid.

import sys
import time
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax

from helpers.core import compute_c

jax.config.update("jax_enable_x64", True)


def make_gaussian_mixture_c(N_GRID=600):
    """Objective: C for Gaussian mixture parameterization."""
    domain_width = 0.5
    dx = domain_width / N_GRID
    grid = jnp.linspace(-0.25, 0.25, N_GRID)

    def eval_on_grid(params):
        """Evaluate Gaussian mixture on grid.
        params shape: (N_PEAKS, 3) — [position_raw, log_width_raw, log_amp]
        position: tanh(position_raw) * 0.24 — constrained to [-0.24, 0.24]
        width: softplus(log_width_raw) * 0.01 + 0.001 — min 0.001, typical 0.001-0.05
        amplitude: softplus(log_amp) — non-negative
        """
        positions = jnp.tanh(params[:, 0]) * 0.24
        widths = jax.nn.softplus(params[:, 1]) * 0.015 + 0.003
        amplitudes = jax.nn.softplus(params[:, 2])

        # f(x) = sum_k amp_k * exp(-(x - pos_k)^2 / (2 * width_k^2))
        # grid: (N_GRID,), positions: (N_PEAKS,)
        diffs = grid[:, None] - positions[None, :]  # (N_GRID, N_PEAKS)
        gaussians = jnp.exp(-0.5 * (diffs / widths[None, :]) ** 2)  # (N_GRID, N_PEAKS)
        f = jnp.sum(gaussians * amplitudes[None, :], axis=1)  # (N_GRID,)
        return f

    def smooth_c_gaussian(params, temp):
        f = eval_on_grid(params)
        integral_f = jnp.sum(f) * dx
        integral_f_sq = jnp.maximum(integral_f ** 2, 1e-9)
        padded_f = jnp.pad(f, (0, N_GRID))
        fft_f = jnp.fft.fft(padded_f)
        conv_f_f = jnp.fft.ifft(fft_f * fft_f).real
        scaled_conv = conv_f_f * dx
        smooth_max = temp * jax.scipy.special.logsumexp(scaled_conv / temp)
        return smooth_max / integral_f_sq

    return jax.jit(smooth_c_gaussian), eval_on_grid


def make_init_params(N_PEAKS, seed):
    """Initialize Gaussian mixture parameters."""
    rng = np.random.RandomState(seed)

    # Diversely positioned peaks — asymmetric arrangement
    if seed == 0:
        # Gradually increasing positions and amplitudes (like arcsine family)
        positions = np.linspace(-0.22, 0.22, N_PEAKS)
        amplitudes = np.exp(np.linspace(0.0, 1.5, N_PEAKS))  # monotone increase
        widths = np.ones(N_PEAKS) * 0.025  # uniform narrow
    elif seed == 1:
        # Clustered: two groups of peaks
        positions = np.concatenate([
            np.linspace(-0.22, -0.05, N_PEAKS // 2),
            np.linspace(0.05, 0.22, N_PEAKS - N_PEAKS // 2)
        ])
        amplitudes = np.ones(N_PEAKS)
        amplitudes[:N_PEAKS // 2] *= 0.5
        amplitudes[N_PEAKS // 2:] *= 1.5  # asymmetric clusters
        widths = np.ones(N_PEAKS) * 0.02
    elif seed == 2:
        # Random diverse
        positions = rng.uniform(-0.22, 0.22, N_PEAKS)
        amplitudes = rng.exponential(1.0, N_PEAKS)
        widths = rng.uniform(0.01, 0.04, N_PEAKS)
    else:
        # Heavy-tailed: few dominant peaks
        positions = rng.uniform(-0.22, 0.22, N_PEAKS)
        amplitudes = rng.pareto(1.5, N_PEAKS) + 0.1
        widths = rng.uniform(0.005, 0.03, N_PEAKS)

    # Convert to raw parameters
    pos_raw = np.arctanh(np.clip(positions / 0.24, -0.99, 0.99))
    width_raw = np.log(np.expm1(np.maximum(widths / 0.015 - 0.003 / 0.015, 1e-6)))
    amp_raw = np.log(np.expm1(np.maximum(amplitudes, 1e-6)))

    params = np.stack([pos_raw, width_raw, amp_raw], axis=1)
    return jnp.array(params, dtype=jnp.float64)


def entrypoint():
    N_PEAKS = 15
    N_GRID = 600
    N_SEEDS = 4
    TOTAL_STEPS = 60000
    TEMPS = [0.05, 0.01, 0.003, 0.001, 0.0003]
    STEPS_PER_TEMP = TOTAL_STEPS // len(TEMPS)

    # ---- TIMING BENCHMARK ----
    print("=== TIMING BENCHMARK ===")
    smooth_c_fn, eval_on_grid = make_gaussian_mixture_c(N_GRID)
    bench_params = make_init_params(N_PEAKS, 0)
    bench_opt = optax.adam(1e-3)
    bench_state = bench_opt.init(bench_params)

    @jax.jit
    def bench_step(params, state):
        loss, grads = jax.value_and_grad(smooth_c_fn)(params, jnp.array(0.05, dtype=jnp.float64))
        updates, new_state = bench_opt.update(grads, state, params)
        return optax.apply_updates(params, updates), new_state, loss

    bench_params, bench_state, _ = bench_step(bench_params, bench_state)  # warmup
    t0 = time.time()
    for _ in range(100):
        bench_params, bench_state, _ = bench_step(bench_params, bench_state)
    step_time_ms = (time.time() - t0) / 100 * 1000
    print(f"Gaussian mixture step time: {step_time_ms:.3f}ms per step ({N_PEAKS} peaks, N={N_GRID})")

    est_time = N_SEEDS * TOTAL_STEPS * step_time_ms / 1000
    print(f"Estimated total time: {est_time:.1f}s ({N_SEEDS} seeds × {TOTAL_STEPS} steps)")
    if est_time > 350:
        # Reduce to fit
        TOTAL_STEPS = int(350 / (N_SEEDS * step_time_ms / 1000))
        STEPS_PER_TEMP = TOTAL_STEPS // len(TEMPS)
        print(f"  Reduced to {TOTAL_STEPS} steps/seed")

    # ---- OPTIMIZATION ----
    print("\n=== GAUSSIAN MIXTURE OPTIMIZATION ===")

    total_steps = STEPS_PER_TEMP * len(TEMPS)
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0, peak_value=0.01,
        warmup_steps=min(500, total_steps // 10),
        decay_steps=total_steps, end_value=1e-5)
    optimizer = optax.adam(learning_rate=schedule)

    @jax.jit
    def step_fn(params, temp, opt_state):
        loss, grads = jax.value_and_grad(smooth_c_fn)(params, temp)
        updates, new_opt_state = optimizer.update(grads, opt_state, params)
        return optax.apply_updates(params, updates), new_opt_state, loss

    best_params = None
    best_c = float('inf')

    for seed in range(N_SEEDS):
        params = make_init_params(N_PEAKS, seed)
        opt_state = optimizer.init(params)

        for temp in TEMPS:
            t = jnp.array(temp, dtype=jnp.float64)
            for step in range(STEPS_PER_TEMP):
                params, opt_state, loss = step_fn(params, t, opt_state)

        # Evaluate final C
        f = eval_on_grid(params)
        c = float(compute_c(f))
        print(f"  Seed {seed}: C = {c:.6f}")

        if c < best_c:
            best_c = c
            best_params = params

    print(f"\nBest Gaussian mixture C: {best_c:.6f}")

    # Return best solution
    f_final = eval_on_grid(best_params)
    f_np = np.array(jnp.maximum(f_final, 0.0))
    print(f"Array shape: {f_np.shape}, min={f_np.min():.6f}, max={f_np.max():.6f}")
    return f_np
