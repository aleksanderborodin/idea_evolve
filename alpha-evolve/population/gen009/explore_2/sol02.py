# fitness: 1.5170155936496197
# N=5000: Focused iterative LP test at epsilon_rel=1e-7 (15-30 constraints)
# Goal: determine whether few-constraint iterative LP can improve C at N=5000
# (Few-constraint LP failed at N=30k due to plateau; testing at N=5000)

import sys
import time

sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax

jax.config.update("jax_enable_x64", True)

from helpers.compute_c_f64 import compute_c_f64
from helpers.cross_convolution_f64 import autoconvolve, tight_constraint_indices
from helpers.incremental_autoconv_update import incremental_update
from helpers.lp_matrix import scipy_lp_solve


# ---- Smooth-max gradient descent (same as sol01) ----

def make_smooth_c_fn(N):
    dx = 0.5 / N
    def _fn(raw_params, temp):
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


def run_gradient_descent(N, seed, temps, steps_per_temp):
    smooth_c = make_smooth_c_fn(N)
    total_steps = steps_per_temp * len(temps)
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0, peak_value=0.005,
        warmup_steps=min(300, total_steps // 10),
        decay_steps=total_steps, end_value=1e-5)
    optimizer = optax.adam(learning_rate=schedule)

    key = jax.random.PRNGKey(seed)
    x = jnp.linspace(0, 1, N)
    raw_init = 0.5 + 0.3 * jnp.sin(jnp.pi * x) + 0.1 * jax.random.normal(key, (N,))

    @jax.jit
    def step_fn(raw_params, temp, opt_state):
        loss, grads = jax.value_and_grad(smooth_c)(raw_params, temp)
        updates, new_opt_state = optimizer.update(grads, opt_state, raw_params)
        return optax.apply_updates(raw_params, updates), new_opt_state, loss

    opt_state = optimizer.init(raw_init)
    raw_params = raw_init
    for temp in temps:
        t_jax = jnp.array(temp, dtype=jnp.float64)
        for _ in range(steps_per_temp):
            raw_params, opt_state, _ = step_fn(raw_params, t_jax, opt_state)
    return np.array(jax.nn.softplus(raw_params))


def coord_descent_pass(f, autoconv_arr, f_padded, dx, M_fft, deltas):
    N = len(f)
    integral = np.sum(f) * dx
    integral_sq = integral ** 2
    current_c = np.max(autoconv_arr) / integral_sq
    improvements = 0
    for idx in range(N):
        best_c = current_c
        best_delta = 0.0
        for delta in deltas:
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


def run_coord_descent(f_init, max_rounds=8):
    f = np.array(f_init, dtype=np.float64)
    f = np.maximum(f, 0.0)
    N = len(f)
    dx = 0.5 / N
    M_fft = 2 * N
    autoconv_arr, f_padded, _, _ = autoconvolve(f)
    f_padded = np.array(f_padded, dtype=np.float64)
    integral = np.sum(f) * dx
    current_c = np.max(autoconv_arr) / (integral ** 2)
    print(f"  [CD] Start C={current_c:.8f}")
    delta_grid = []
    for mag in [1e-2, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5, 3e-6, 1e-6]:
        delta_grid.extend([mag, -mag])
    t0 = time.time()
    for rnd in range(max_rounds):
        old_c = current_c
        f, autoconv_arr, f_padded, current_c, impr = coord_descent_pass(
            f, autoconv_arr, f_padded, dx, M_fft, delta_grid)
        print(f"  [CD] Round {rnd+1}: C={current_c:.8f}, impr={impr}, t={time.time()-t0:.1f}s")
        if impr == 0 or (old_c - current_c) < 1e-10:
            break
    return f, current_c, autoconv_arr, f_padded, dx, M_fft


# ---- Iterative LP test ----

def iterative_lp_test(f, c_val, autoconv_arr, f_padded, dx, M_fft, epsilon_rel=1e-7, max_iter=20):
    """
    Test iterative LP with tight-index re-identification after each step.
    This is the key diagnostic: does LP work when epsilon_rel is tight (15-56 constraints)?
    Returns: list of (iteration, C, tight_count, lp_improved)
    """
    print(f"\n  [ILP] Iterative LP at epsilon_rel={epsilon_rel:.0e}")
    N = len(f)
    f_curr = f.copy()
    c_curr = c_val
    ac_curr = autoconv_arr.copy()
    fp_curr = f_padded.copy()

    history = []
    t0 = time.time()

    for it in range(max_iter):
        # Re-identify tight constraints
        tight_idx = np.where(ac_curr >= np.max(ac_curr) * (1.0 - epsilon_rel))[0].astype(np.int64)
        n_tight = len(tight_idx)

        result = scipy_lp_solve(f_curr, tight_idx, ac_curr, dx=dx,
                                epsilon=1e-10, max_step=0.01)

        if result is None or result['status'] != 0:
            print(f"    iter {it+1}: LP failed (status={result['status'] if result else 'None'})")
            history.append((it+1, c_curr, n_tight, False))
            break

        delta = result['delta']

        # Line search
        best_c_ls = c_curr
        best_alpha = 0.0
        for alpha in np.logspace(-6, -1, 20):
            f_new = np.maximum(f_curr + alpha * delta, 0.0)
            try:
                new_c = compute_c_f64(f_new)
                if new_c < best_c_ls:
                    best_c_ls = new_c
                    best_alpha = alpha
            except:
                pass

        improved = best_alpha > 0 and best_c_ls < c_curr - 1e-12
        if improved:
            f_curr = np.maximum(f_curr + best_alpha * delta, 0.0)
            ac_curr, fp_curr, _, _ = autoconvolve(f_curr)
            fp_curr = np.array(fp_curr, dtype=np.float64)
            c_prev = c_curr
            c_curr = compute_c_f64(f_curr)
            print(f"    iter {it+1}: tight={n_tight}, alpha={best_alpha:.2e}, C: {c_prev:.8f} -> {c_curr:.8f} (Δ={c_curr-c_prev:.2e}), t={time.time()-t0:.1f}s")
        else:
            print(f"    iter {it+1}: tight={n_tight}, no improvement (pred={result['predicted_improvement']:.2e}), t={time.time()-t0:.1f}s")
            history.append((it+1, c_curr, n_tight, False))
            break

        history.append((it+1, c_curr, n_tight, True))

    return f_curr, c_curr, ac_curr, fp_curr, history


def entrypoint() -> np.ndarray:
    """
    N=5000 focused iterative LP diagnostic.
    Tests whether few-constraint iterative LP can improve C at N=5000.
    """
    N = 5000
    t0 = time.time()
    print(f"\n{'='*60}")
    print(f"N=5000 Iterative LP Diagnostic")
    print(f"{'='*60}")

    # Quick 2-seed optimization to get near-optimal N=5000 solution
    # Use fewer steps than sol01 to save time
    temps = [0.05, 0.01, 0.003, 0.001, 0.0003]
    steps_per_temp = 12000  # ~50 seconds per seed

    best_f = None
    best_c_gd = float('inf')

    for seed in [2, 1]:  # seed 2 was best in sol01
        print(f"\n[GD] seed={seed}")
        f_gd = run_gradient_descent(N, seed, temps, steps_per_temp)
        c_gd = compute_c_f64(f_gd)
        print(f"  C = {c_gd:.6f}")
        if c_gd < best_c_gd:
            best_c_gd = c_gd
            best_f = f_gd.copy()

    print(f"\nBest GD: C={best_c_gd:.6f}, t={time.time()-t0:.1f}s")

    # Coordinate descent
    print(f"\n[Coord Descent]")
    f_cd, c_cd, autoconv_arr, f_padded, dx, M_fft = run_coord_descent(best_f, max_rounds=8)
    print(f"After CD: C={c_cd:.8f}, t={time.time()-t0:.1f}s")

    # Measure tight constraints at all epsilon levels
    print(f"\n[Tight Constraint Analysis]")
    for eps in [1e-4, 1e-5, 1e-6, 1e-7, 1e-8]:
        tc = np.where(autoconv_arr >= np.max(autoconv_arr) * (1.0 - eps))[0]
        print(f"  tight@{eps:.0e} = {len(tc)}")

    # Test iterative LP at epsilon_rel=1e-7 (most constrained)
    f_lp7, c_lp7, ac7, fp7, hist7 = iterative_lp_test(
        f_cd, c_cd, autoconv_arr, f_padded, dx, M_fft,
        epsilon_rel=1e-7, max_iter=20)

    # Test iterative LP at epsilon_rel=1e-6 if different
    f_lp6, c_lp6, ac6, fp6, hist6 = iterative_lp_test(
        f_cd, c_cd, autoconv_arr, f_padded, dx, M_fft,
        epsilon_rel=1e-6, max_iter=20)

    # Final best
    f_final = f_cd
    c_final = c_cd
    label = "coord_descent"
    if c_lp7 < c_final:
        f_final = f_lp7
        c_final = c_lp7
        label = "iter_lp_1e7"
    if c_lp6 < c_final:
        f_final = f_lp6
        c_final = c_lp6
        label = "iter_lp_1e6"

    total_t = time.time() - t0
    print(f"\n{'='*60}")
    print(f"FINAL RESULTS:")
    print(f"  N = {N}")
    print(f"  C after GD = {best_c_gd:.6f}")
    print(f"  C after CD = {c_cd:.8f}")
    print(f"  C after ILP@1e-7 = {c_lp7:.8f} ({len(hist7)} iters)")
    print(f"  C after ILP@1e-6 = {c_lp6:.8f} ({len(hist6)} iters)")
    print(f"  Best source: {label}")
    print(f"  Final C = {c_final:.8f}")
    print(f"  Total time = {total_t:.1f}s")

    # Summary for ideas
    if c_lp7 < c_cd or c_lp6 < c_cd:
        print(f"\n  -> LP WORKS at N=5000 with few constraints!")
        print(f"  -> This is evidence for LP tractability at intermediate resolution.")
    else:
        print(f"\n  -> LP did not improve C at N=5000 (same plateau problem as N=30k)")
        print(f"  -> idea_020 should be archived.")
    print(f"{'='*60}")

    return np.array(f_final, dtype=np.float64)
