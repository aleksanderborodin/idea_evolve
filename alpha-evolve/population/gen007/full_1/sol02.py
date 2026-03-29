# fitness: 1.5028628724712894
# LP-based refinement directly at N=30k with minimal tight constraints
# Method: full-resolution LP with 1-20 tight constraints → vectorized A_ub construction
# Root cause of gen6 failure was Python loops over N; this uses vectorized numpy.
import numpy as np
import importlib.util
import sys
import time
from scipy.optimize import linprog


def _load_best_solution():
    sol_path = "/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen006/exploit_1/sol01.py"
    spec = importlib.util.spec_from_file_location("best_sol", sol_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return np.array(mod.entrypoint(), dtype=np.float64)


def _setup_helpers():
    proj_problem = "/home/sasha/Desktop/project_alpha/alpha-evolve/problem"
    if proj_problem not in sys.path:
        sys.path.insert(0, proj_problem)


def _compute_autoconv(f, dx):
    """Compute autoconvolution matching validate.py exactly."""
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
    f = _load_best_solution()
    N = len(f)
    dx = 0.5 / N
    C0 = compute_c_f64(f)
    print(f"  N = {N}, C = {C0:.12f}")

    # ── Compute autoconvolution at N=30k ────────────────────────────────────
    print("Computing autoconvolution...")
    t0 = time.time()
    autoconv = _compute_autoconv(f, dx)  # length 2N
    M_wrap = 2 * N
    max_autoconv = np.max(autoconv)
    print(f"  max autoconv = {max_autoconv:.12e}, took {time.time()-t0:.2f}s")

    # ── Find tight constraints ──────────────────────────────────────────────
    n_tight = 0
    tight_indices = np.array([], dtype=int)
    for eps_factor in [0.0, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4]:
        eps = eps_factor * max_autoconv
        cands = np.where(autoconv >= max_autoconv - eps)[0]
        print(f"  epsilon={eps_factor:.0e}: {len(cands)} tight constraints")
        if 1 <= len(cands) <= 50:
            tight_indices = cands
            n_tight = len(cands)
            break

    if n_tight == 0:
        print("  Using just the argmax as single tight constraint")
        tight_indices = np.array([np.argmax(autoconv)])
        n_tight = 1

    print(f"Using {n_tight} tight constraints")

    # ── Build constraint matrix using vectorized numpy ──────────────────────
    # A_ub[j_idx, k] = 2 * f[j - k] * dx  (f_padded circular wrap for safety)
    # Shape: (n_tight, N) = e.g. (5, 30000) → trivial memory and time
    print("Building constraint matrix (vectorized)...")
    t0 = time.time()

    f_padded = np.zeros(M_wrap, dtype=np.float64)
    f_padded[:N] = f
    k_vals = np.arange(N)

    A_ub = np.zeros((n_tight, N), dtype=np.float64)
    for j_idx, j in enumerate(tight_indices):
        idx = (j - k_vals) % M_wrap
        A_ub[j_idx, :] = 2.0 * f_padded[idx] * dx

    t_build = time.time() - t0
    print(f"  Built {A_ub.shape} in {t_build:.3f}s, {A_ub.nbytes / 1e6:.1f} MB")

    if t_build > 60:
        print("  Matrix construction too slow, aborting")
        return f

    # ── Formulate LP ────────────────────────────────────────────────────────
    # Variables: [delta_f (N), t (1)]
    # Minimize t  (t is the max change in autoconv at tight points)
    # Constraints:
    #   A_ub @ delta_f - t <= max_autoconv - autoconv[tight]   → push tight pts down
    #   delta_f >= -f[k]   (f + delta_f >= 0)
    #   sum(delta_f) = 0   (integral preservation)
    #
    # If optimal t < 0 → descent direction exists

    c_obj = np.zeros(N + 1)
    c_obj[-1] = 1.0

    residual = autoconv[tight_indices] - max_autoconv  # all <= 0
    A_ineq = np.hstack([A_ub, -np.ones((n_tight, 1))])
    b_ineq = -residual  # >= 0

    bounds = [(-f[k], None) for k in range(N)] + [(None, None)]

    A_eq = np.zeros((1, N + 1))
    A_eq[0, :N] = 1.0
    b_eq = np.array([0.0])

    print(f"Solving LP: {N+1} vars, {n_tight} ineq constraints, 1 eq constraint...")
    t0 = time.time()
    result = linprog(c_obj, A_ub=A_ineq, b_ub=b_ineq, A_eq=A_eq, b_eq=b_eq,
                     bounds=bounds, method='highs',
                     options={'time_limit': 120.0, 'disp': False})
    t_lp = time.time() - t0
    print(f"LP solved in {t_lp:.2f}s")
    print(f"LP status: {result.status}, message: {result.message}")

    if not result.success:
        print("LP failed, returning best solution unchanged")
        return f

    t_opt = result.x[-1]
    print(f"LP optimal t = {t_opt:.6e}")

    if t_opt >= 0:
        print("t >= 0: no descent direction (LP says tight constraints cannot be reduced)")
        print("This is expected if the solution is at a local LP optimum")
        print("Returning best solution unchanged")
        return f

    # ── LP succeeded: descent direction found ──────────────────────────────
    delta_f = result.x[:N]
    print(f"\nDescent direction: norm={np.linalg.norm(delta_f):.6e}, "
          f"nnz={np.sum(np.abs(delta_f) > 1e-15)}/{N}")
    print(f"Descent direction: max={delta_f.max():.4e}, min={delta_f.min():.4e}")

    # ── Line search ─────────────────────────────────────────────────────────
    print("\nLine search at N=30k:")
    best_c = C0
    best_f = f.copy()
    print(f"  baseline: C={best_c:.12f}")

    # Try wide range of step sizes
    alphas = [1e-6, 3e-6, 1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 0.1, 0.3, 1.0]
    for alpha in alphas:
        f_trial = np.maximum(f + alpha * delta_f, 0.0)
        c_trial = compute_c_f64(f_trial)
        marker = " <-- BETTER" if c_trial < best_c else ""
        print(f"  alpha={alpha:.2e}: C={c_trial:.12f}{marker}")
        if c_trial < best_c:
            best_c = c_trial
            best_f = f_trial.copy()

    # Refine around best alpha
    if best_c < C0:
        best_alpha = alphas[[i for i, a in enumerate(alphas) if np.maximum(f + a * delta_f, 0).sum() > 0
                              and compute_c_f64(np.maximum(f + a * delta_f, 0)) == best_c][0]]
        print(f"\nRefining around best alpha={best_alpha:.2e}...")
        for alpha in [best_alpha * 0.3, best_alpha * 0.5, best_alpha * 0.7,
                      best_alpha * 1.5, best_alpha * 2.0, best_alpha * 3.0]:
            f_trial = np.maximum(f + alpha * delta_f, 0.0)
            c_trial = compute_c_f64(f_trial)
            marker = " <-- BETTER" if c_trial < best_c else ""
            print(f"  alpha={alpha:.2e}: C={c_trial:.12f}{marker}")
            if c_trial < best_c:
                best_c = c_trial
                best_f = f_trial.copy()

    print(f"\nFinal best C: {best_c:.12f}")
    print(f"Improvement over baseline: {C0 - best_c:.6e}")
    print(f"Total time: {time.time() - t_start:.1f}s")

    return best_f
