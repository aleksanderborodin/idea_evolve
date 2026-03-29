# fitness: 1.5028628724712894
# LP-based refinement of TTT-Discover 30k array at reduced resolution N=2000
# Method: downsample → LP descent direction → upsample → line search on 30k array
import numpy as np
import importlib.util
import sys
import os
from scipy.optimize import linprog
import time


def _load_best_solution():
    sol_path = "/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen006/exploit_1/sol01.py"
    spec = importlib.util.spec_from_file_location("best_sol", sol_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return np.array(mod.entrypoint(), dtype=np.float64)


def _setup_helpers():
    """Ensure problem/helpers is on the path."""
    proj_problem = "/home/sasha/Desktop/project_alpha/alpha-evolve/problem"
    if proj_problem not in sys.path:
        sys.path.insert(0, proj_problem)


def _compute_autoconv(f, dx):
    """Compute autoconvolution matching validate.py exactly (zero-pad to 2N, full FFT)."""
    N = len(f)
    padded = np.zeros(2 * N, dtype=np.float64)
    padded[:N] = f
    fft_f = np.fft.fft(padded)
    conv = np.fft.ifft(fft_f * fft_f).real
    return conv * dx  # shape (2N,)


def entrypoint():
    t_start = time.time()
    _setup_helpers()
    from helpers.compute_c_f64 import compute_c_f64

    # ── Load best 30k solution ──────────────────────────────────────────────
    print("Loading best 30k solution...")
    f_30k = _load_best_solution()
    N_30k = len(f_30k)
    print(f"  N_30k = {N_30k}, C_30k = {compute_c_f64(f_30k):.12f}")

    x_30k = np.linspace(-0.25, 0.25, N_30k, endpoint=False)

    # ── Downsample to N=2000 ───────────────────────────────────────────────
    N_lp = 2000
    x_lp = np.linspace(-0.25, 0.25, N_lp, endpoint=False)
    f = np.interp(x_lp, x_30k, f_30k)
    f = np.maximum(f, 0.0)
    dx = 0.5 / N_lp

    integral_f = np.sum(f) * dx
    C_lp = compute_c_f64(f)
    print(f"  N_lp = {N_lp}, C_lp = {C_lp:.12f}, integral = {integral_f:.8f}")

    # ── Compute autoconvolution ─────────────────────────────────────────────
    autoconv = _compute_autoconv(f, dx)  # length 2*N_lp
    max_autoconv = np.max(autoconv)
    print(f"  max autoconv = {max_autoconv:.12f}, integral^2 = {integral_f**2:.12f}")
    print(f"  Ratio (should match C_lp): {max_autoconv / integral_f**2:.12f}")

    # ── Find tight constraints ──────────────────────────────────────────────
    n_tight = 0
    tight_indices = np.array([], dtype=int)
    for eps_factor in [1e-7, 1e-6, 1e-5, 1e-4, 5e-4, 1e-3]:
        eps = eps_factor * max_autoconv
        cands = np.where(autoconv >= max_autoconv - eps)[0]
        print(f"  epsilon={eps_factor:.0e}: {len(cands)} tight constraints")
        if 1 <= len(cands) <= 300:
            tight_indices = cands
            n_tight = len(cands)
            break

    if n_tight == 0:
        print("  WARNING: could not find bounded tight set, using top-1")
        tight_indices = np.array([np.argmax(autoconv)])
        n_tight = 1

    print(f"Using {n_tight} tight constraints at j in {tight_indices[:5]}...")

    # ── Build constraint matrix A_ub ───────────────────────────────────────
    # A_ub[j_idx, k] = 2 * f[j - k] * dx  (for k where 0 <= j-k < N_lp)
    # Use zero-padded f: f_padded[i] = f[i] for i<N_lp, 0 otherwise
    # Circular wrap % (2*N_lp) ensures negative indices map to high (zero) region
    N = N_lp
    M_wrap = 2 * N  # match the 2N padded length used in autoconv computation

    f_padded = np.zeros(M_wrap, dtype=np.float64)
    f_padded[:N] = f

    t_build = time.time()
    A_ub = np.zeros((n_tight, N), dtype=np.float64)
    k_vals = np.arange(N)
    for j_idx, j in enumerate(tight_indices):
        idx = (j - k_vals) % M_wrap  # wrap: negative → high (zero region)
        A_ub[j_idx, :] = 2.0 * f_padded[idx] * dx

    t_build_done = time.time()
    print(f"Constraint matrix built in {t_build_done - t_build:.2f}s, shape {A_ub.shape}")

    if t_build_done - t_build > 60:
        print("  Matrix construction took too long, returning best solution unchanged")
        return f_30k

    # ── Formulate LP ────────────────────────────────────────────────────────
    # Variables: [delta_f (N), t (1)]
    # Minimize t
    # Subject to:
    #   (1) A_ub @ delta_f - t <= max_autoconv - autoconv[tight]   (drive tight constraints down)
    #   (2) delta_f >= -f[k]  (non-negativity: f + delta_f >= 0)
    #   (3) sum(delta_f) = 0  (integral preservation)
    #   (4) t unbounded
    #
    # If optimal t < 0: descent direction found (tight constraints decrease)

    c_obj = np.zeros(N + 1)
    c_obj[-1] = 1.0  # minimize t

    # Inequality: A_ub @ delta_f - t <= (max_autoconv - autoconv[tight])
    residual = autoconv[tight_indices] - max_autoconv  # all <= 0
    A_ineq = np.hstack([A_ub, -np.ones((n_tight, 1))])
    b_ineq = -residual  # = max_autoconv - autoconv[tight] >= 0

    # Bounds
    bounds = [(-f[k], None) for k in range(N)] + [(None, None)]

    # Equality: integral preservation sum(delta_f) = 0
    A_eq = np.zeros((1, N + 1))
    A_eq[0, :N] = 1.0
    b_eq = np.array([0.0])

    print("Solving LP with HiGHS...")
    t_lp = time.time()
    result = linprog(c_obj, A_ub=A_ineq, b_ub=b_ineq, A_eq=A_eq, b_eq=b_eq,
                     bounds=bounds, method='highs',
                     options={'time_limit': 120.0, 'disp': False})
    t_lp_done = time.time()
    print(f"LP solved in {t_lp_done - t_lp:.2f}s")
    print(f"LP status: {result.status}, message: {result.message}")

    if not result.success:
        print("  LP failed, returning best 30k solution unchanged")
        return f_30k

    t_opt = result.x[-1]
    print(f"  LP optimal t = {t_opt:.6e}")

    if t_opt >= 0:
        print("  t >= 0: no descent direction found (LP says no improvement possible)")
        print("  Returning best 30k solution unchanged")
        return f_30k

    # ── LP succeeded: extract descent direction ─────────────────────────────
    delta_f_lp = result.x[:N]
    print(f"  Descent direction: norm={np.linalg.norm(delta_f_lp):.6f}, "
          f"max={delta_f_lp.max():.4e}, min={delta_f_lp.min():.4e}")

    # Verify at N=2000 first
    print("Line search at N=2000:")
    best_c_lp = C_lp
    best_alpha_lp = 0.0
    for alpha in [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0]:
        f_test = np.maximum(f + alpha * delta_f_lp, 0.0)
        c_test = compute_c_f64(f_test)
        marker = " <-- BETTER" if c_test < best_c_lp else ""
        print(f"  alpha={alpha:.3f}: C={c_test:.10f}{marker}")
        if c_test < best_c_lp:
            best_c_lp = c_test
            best_alpha_lp = alpha

    # ── Upsample and apply to 30k array ────────────────────────────────────
    print("\nUpsampling descent direction to N=30k...")
    delta_f_30k = np.interp(x_30k, x_lp, delta_f_lp)

    print("Line search at N=30k:")
    best_c_30k = compute_c_f64(f_30k)
    best_f_30k = f_30k.copy()
    print(f"  baseline: C={best_c_30k:.12f}")

    for alpha in [0.0001, 0.0003, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0]:
        f_trial = np.maximum(f_30k + alpha * delta_f_30k, 0.0)
        c_trial = compute_c_f64(f_trial)
        marker = " <-- BETTER" if c_trial < best_c_30k else ""
        print(f"  alpha={alpha:.4f}: C={c_trial:.12f}{marker}")
        if c_trial < best_c_30k:
            best_c_30k = c_trial
            best_f_30k = f_trial.copy()

    print(f"\nFinal best C at N=30k: {best_c_30k:.12f}")
    print(f"Improvement: {compute_c_f64(f_30k) - best_c_30k:.4e}")
    print(f"Total time: {time.time() - t_start:.1f}s")

    return best_f_30k
