# fitness: 1.516845435932697
# N=5000 optimization: gradient descent + coordinate descent + LP tractability study
# Phase 1: Adam + smooth-max temperature annealing at N=5000 (fresh random init)
# Phase 2: Coordinate descent with O(N) incremental updates
# Phase 3: LP tractability diagnostic

import sys
import time
import json

sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax

jax.config.update("jax_enable_x64", True)

from helpers.core import compute_c
from helpers.compute_c_f64 import compute_c_f64
from helpers.cross_convolution_f64 import autoconvolve, tight_constraint_indices
from helpers.incremental_autoconv_update import incremental_update
from helpers.lp_matrix import scipy_lp_solve


# ============================================================
# Smooth-max objective for gradient descent
# ============================================================

def make_smooth_c_fn(N):
    """Smooth-max approximation of C for gradient-based optimization at N=5000."""
    dx = 0.5 / N

    def _fn(raw_params, temp):
        # softplus ensures non-negativity
        f_nn = jax.nn.softplus(raw_params)
        integral_f = jnp.sum(f_nn) * dx
        integral_f_sq = jnp.maximum(integral_f ** 2, 1e-9)
        padded_f = jnp.pad(f_nn, (0, N))
        fft_f = jnp.fft.fft(padded_f)
        conv_f_f = jnp.fft.ifft(fft_f * fft_f).real
        scaled_conv = conv_f_f * dx
        smooth_max = temp * jax.scipy.special.logsumexp(scaled_conv / temp)
        return smooth_max / integral_f_sq

    return jax.jit(_fn)


def run_gradient_descent(N, seed, temps, steps_per_temp, peak_lr=0.005, end_lr=1e-5):
    """Run smooth-max Adam optimization from random init."""
    print(f"  [GD] Seed={seed}, N={N}, temps={temps}, steps={steps_per_temp}/phase")
    smooth_c = make_smooth_c_fn(N)

    total_steps = steps_per_temp * len(temps)
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0, peak_value=peak_lr,
        warmup_steps=min(500, total_steps // 10),
        decay_steps=total_steps, end_value=end_lr)
    optimizer = optax.adam(learning_rate=schedule)

    # Random smooth initialization: Gaussian bumps
    key = jax.random.PRNGKey(seed)
    # Use arcsine-like init: more mass at edges
    x = jnp.linspace(0, 1, N)
    # Mix of smooth init approaches
    raw_init = 0.5 + 0.3 * jnp.sin(jnp.pi * x) + 0.1 * jax.random.normal(key, (N,))

    @jax.jit
    def step_fn(raw_params, temp, opt_state):
        loss, grads = jax.value_and_grad(smooth_c)(raw_params, temp)
        updates, new_opt_state = optimizer.update(grads, opt_state, raw_params)
        return optax.apply_updates(raw_params, updates), new_opt_state, loss

    opt_state = optimizer.init(raw_init)
    raw_params = raw_init

    t0 = time.time()
    for phase_idx, temp in enumerate(temps):
        t_jax = jnp.array(temp, dtype=jnp.float64)
        for step in range(steps_per_temp):
            raw_params, opt_state, loss = step_fn(raw_params, t_jax, opt_state)
        # Check C after each phase
        f_vals = np.array(jax.nn.softplus(raw_params))
        c_val = compute_c_f64(f_vals)
        elapsed = time.time() - t0
        print(f"    Phase {phase_idx+1}/{len(temps)} (T={temp}): C={c_val:.6f}, t={elapsed:.1f}s")

    f_final = np.array(jax.nn.softplus(raw_params))
    return f_final


# ============================================================
# Coordinate descent
# ============================================================

def coord_descent_pass(f, autoconv_arr, f_padded, dx, M_fft, deltas):
    """One full pass of coordinate descent. Returns (new_f, new_autoconv, improvements)."""
    N = len(f)
    integral = np.sum(f) * dx
    integral_sq = integral ** 2
    current_c = np.max(autoconv_arr) / integral_sq

    improvements = 0
    for idx in range(N):
        best_c = current_c
        best_delta = 0.0

        for delta in deltas:
            # Non-negativity constraint
            if f[idx] + delta < 0:
                continue
            new_autoconv = incremental_update(autoconv_arr, f_padded, idx, delta, dx, M_fft)
            new_integral = integral + delta * dx
            if new_integral <= 0:
                continue
            new_c = np.max(new_autoconv) / (new_integral ** 2)
            if new_c < best_c - 1e-15:
                best_c = new_c
                best_delta = delta

        if best_delta != 0.0:
            autoconv_arr = incremental_update(autoconv_arr, f_padded, idx, best_delta, dx, M_fft)
            f_padded[idx] += best_delta
            f[idx] += best_delta
            integral += best_delta * dx
            integral_sq = integral ** 2
            current_c = best_c
            improvements += 1

    return f, autoconv_arr, f_padded, current_c, improvements


def run_coord_descent(f_init, max_rounds=10, verbose=True):
    """Run coordinate descent to convergence."""
    f = np.array(f_init, dtype=np.float64)
    f = np.maximum(f, 0.0)  # ensure non-negative
    N = len(f)
    dx = 0.5 / N
    M_fft = 2 * N

    autoconv_arr, f_padded, _, _ = autoconvolve(f)
    f_padded = np.array(f_padded, dtype=np.float64)

    integral = np.sum(f) * dx
    current_c = np.max(autoconv_arr) / (integral ** 2)

    # Delta grid: coarse to fine
    delta_grid = []
    for mag in [1e-2, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5, 3e-6, 1e-6, 3e-7, 1e-7]:
        delta_grid.extend([mag, -mag])
    # Also proportional deltas
    # Zeroing each element is handled by delta = -f[idx]

    if verbose:
        print(f"  [CD] Starting C={current_c:.8f}, N={N}")

    t0 = time.time()
    for round_idx in range(max_rounds):
        f_old_c = current_c

        # Use a wider delta grid for early rounds
        if round_idx < 3:
            deltas = delta_grid
        else:
            deltas = [d for d in delta_grid if abs(d) <= 1e-4]

        # Also add zeroing deltas (set element to 0)
        # We handle zeroing by adding -f[idx] as a special delta
        f, autoconv_arr, f_padded, current_c, improvements = coord_descent_pass(
            f, autoconv_arr, f_padded, dx, M_fft, deltas)

        elapsed = time.time() - t0
        if verbose:
            print(f"    Round {round_idx+1}: C={current_c:.8f}, improvements={improvements}, t={elapsed:.1f}s")

        # Convergence check: less than 0.001% improvement
        if improvements == 0 or (f_old_c - current_c) < 1e-10:
            if verbose:
                print(f"    Converged at round {round_idx+1}")
            break

    return f, current_c


# ============================================================
# LP tractability study
# ============================================================

def lp_tractability_study(f, c_val, verbose=True):
    """Measure tight constraints and attempt LP improvement."""
    print(f"\n  [LP] C={c_val:.8f}, N={len(f)}")

    epsilon_levels = [1e-4, 1e-5, 1e-6, 1e-7]
    tight_counts = {}

    autoconv_arr, f_padded, dx, M_fft = autoconvolve(f)

    for eps in epsilon_levels:
        tight_idx = tight_constraint_indices(f, epsilon_rel=eps)
        tight_counts[eps] = len(tight_idx)
        print(f"    tight@{eps:.0e} = {len(tight_idx)}")

    # Attempt LP if tight@1e-5 < 500
    lp_result = None
    lp_improvement = None

    tight_1e5 = tight_counts[1e-5]
    if tight_1e5 < 500:
        print(f"  [LP] tight@1e-5={tight_1e5} < 500, attempting LP solve...")
        tight_idx = tight_constraint_indices(f, epsilon_rel=1e-5)

        result = scipy_lp_solve(f, tight_idx, autoconv_arr, dx=dx,
                                epsilon=1e-9, max_step=0.01)
        if result is not None and result['status'] == 0:
            lp_result = result
            print(f"    LP solved: status={result['status']}, predicted={result['predicted_improvement']:.6e}")

            # Line search with 20 log-spaced alphas
            best_c = c_val
            best_alpha = 0.0
            delta = result['delta']

            alphas = np.logspace(-6, -1, 20)
            for alpha in alphas:
                f_new = np.maximum(f + alpha * delta, 0.0)
                try:
                    new_c = compute_c_f64(f_new)
                    if new_c < best_c:
                        best_c = new_c
                        best_alpha = alpha
                except:
                    pass

            if best_alpha > 0:
                lp_improvement = c_val - best_c
                print(f"    Line search: best_alpha={best_alpha:.2e}, C_new={best_c:.8f}, improvement={lp_improvement:.6e}")
            else:
                print(f"    Line search: no improvement found")
                lp_improvement = 0.0
        else:
            print(f"    LP failed: {result}")
    else:
        print(f"  [LP] tight@1e-5={tight_1e5} >= 500, LP not attempted (plateau too large)")

    return tight_counts, lp_result, lp_improvement


# ============================================================
# Main entrypoint
# ============================================================

def entrypoint() -> np.ndarray:
    """
    N=5000 LP tractability study.
    Phase 1: Gradient descent with smooth-max annealing
    Phase 2: Coordinate descent
    Phase 3: LP tractability measurement
    Returns the best solution found.
    """
    N = 5000
    t_total = time.time()

    print(f"\n{'='*60}")
    print(f"N=5000 LP Tractability Study")
    print(f"{'='*60}")

    # ---- Phase 1: Gradient descent from multiple seeds ----
    temps = [0.05, 0.01, 0.003, 0.001, 0.0003]
    steps_per_temp = 15000  # 15k steps per phase = 75k total per seed

    best_f_gd = None
    best_c_gd = float('inf')

    for seed in range(4):  # 4 seeds
        print(f"\n[Phase 1] Gradient descent, seed={seed}")
        f_gd = run_gradient_descent(N, seed, temps, steps_per_temp)
        c_gd = compute_c_f64(f_gd)
        print(f"  Seed {seed} final C = {c_gd:.6f}")
        if c_gd < best_c_gd:
            best_c_gd = c_gd
            best_f_gd = f_gd.copy()

    print(f"\n[Phase 1 Complete] Best C from gradient descent: {best_c_gd:.6f}")
    print(f"  Elapsed: {time.time()-t_total:.1f}s")

    # ---- Phase 2: Coordinate descent ----
    print(f"\n[Phase 2] Coordinate descent on best GD result (C={best_c_gd:.6f})")
    f_cd, c_cd = run_coord_descent(best_f_gd, max_rounds=15)
    print(f"\n[Phase 2 Complete] C after coord descent: {c_cd:.8f}")
    print(f"  Elapsed: {time.time()-t_total:.1f}s")

    # ---- Phase 3: LP tractability study ----
    print(f"\n[Phase 3] LP tractability study")
    tight_counts, lp_result, lp_improvement = lp_tractability_study(f_cd, c_cd)

    # Apply LP improvement if found
    f_final = f_cd
    c_final = c_cd
    if lp_result is not None and lp_improvement and lp_improvement > 0:
        # Apply best LP step
        delta = lp_result['delta']
        best_alpha = 0.0
        best_c = c_cd
        for alpha in np.logspace(-6, -1, 20):
            f_new = np.maximum(f_cd + alpha * delta, 0.0)
            try:
                new_c = compute_c_f64(f_new)
                if new_c < best_c:
                    best_c = new_c
                    best_alpha = alpha
            except:
                pass
        if best_alpha > 0:
            f_final = np.maximum(f_cd + best_alpha * delta, 0.0)
            c_final = compute_c_f64(f_final)
            print(f"\n[LP applied] C improved: {c_cd:.8f} -> {c_final:.8f}")

    total_elapsed = time.time() - t_total
    print(f"\n{'='*60}")
    print(f"FINAL RESULTS:")
    print(f"  N = {N}")
    print(f"  C after GD = {best_c_gd:.6f}")
    print(f"  C after CD = {c_cd:.8f}")
    print(f"  C final    = {c_final:.8f}")
    print(f"  tight@1e-4 = {tight_counts.get(1e-4, 'N/A')}")
    print(f"  tight@1e-5 = {tight_counts.get(1e-5, 'N/A')}")
    print(f"  tight@1e-6 = {tight_counts.get(1e-6, 'N/A')}")
    print(f"  tight@1e-7 = {tight_counts.get(1e-7, 'N/A')}")
    if lp_improvement is not None:
        print(f"  LP improvement = {lp_improvement:.6e}")
    print(f"  Total time = {total_elapsed:.1f}s")
    print(f"{'='*60}")

    return np.array(f_final, dtype=np.float64)


if __name__ == '__main__':
    f = entrypoint()
    from helpers.compute_c_f64 import compute_c_f64
    c = compute_c_f64(f)
    print(f"Final C = {c:.10f}")
