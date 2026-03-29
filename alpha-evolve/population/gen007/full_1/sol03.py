# fitness: 1.5028628724712894
# LP refinement at N=30k with bounded delta_f and multiple tight constraints
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
    N = len(f)
    padded = np.zeros(2 * N, dtype=np.float64)
    padded[:N] = f
    fft_f = np.fft.fft(padded)
    conv = np.fft.ifft(fft_f * fft_f).real
    return conv * dx


def _run_lp_experiment(f, dx, tight_indices, max_delta_per_element=None):
    N = len(f)
    M_wrap = 2 * N
    f_padded = np.zeros(M_wrap, dtype=np.float64)
    f_padded[:N] = f
    k_vals = np.arange(N)
    autoconv = _compute_autoconv(f, dx)
    max_autoconv = np.max(autoconv)
    n_tight = len(tight_indices)

    A_ub = np.zeros((n_tight, N), dtype=np.float64)
    for j_idx, j in enumerate(tight_indices):
        idx = (j - k_vals) % M_wrap
        A_ub[j_idx, :] = 2.0 * f_padded[idx] * dx

    c_obj = np.zeros(N + 1)
    c_obj[-1] = 1.0

    residual = autoconv[tight_indices] - max_autoconv
    A_ineq = np.hstack([A_ub, -np.ones((n_tight, 1))])
    b_ineq = -residual

    if max_delta_per_element is None:
        bounds = [(-f[k], None) for k in range(N)] + [(None, None)]
    else:
        bounds = [(-f[k], max_delta_per_element) for k in range(N)] + [(None, None)]

    A_eq = np.zeros((1, N + 1))
    A_eq[0, :N] = 1.0
    b_eq = np.array([0.0])

    result = linprog(c_obj, A_ub=A_ineq, b_ub=b_ineq, A_eq=A_eq, b_eq=b_eq,
                     bounds=bounds, method='highs',
                     options={'time_limit': 120.0, 'disp': False})
    return result, autoconv, max_autoconv


def entrypoint():
    t_start = time.time()
    _setup_helpers()
    from helpers.compute_c_f64 import compute_c_f64

    print("Loading best 30k solution...")
    f = _load_best_solution()
    N = len(f)
    dx = 0.5 / N
    C0 = compute_c_f64(f)
    max_f = f.max()
    print(f"  N={N}, C={C0:.12f}, max(f)={max_f:.6f}")

    print("Computing autoconvolution...")
    autoconv = _compute_autoconv(f, dx)
    max_autoconv = np.max(autoconv)
    print(f"  max autoconv = {max_autoconv:.8e}")

    # Find tight constraint counts at various epsilon values
    print("\nTight constraint counts:")
    tight_by_eps = {}
    for eps_factor in [0.0, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 0.05, 0.1]:
        eps = eps_factor * max_autoconv
        cands = np.where(autoconv >= max_autoconv - eps)[0]
        tight_by_eps[eps_factor] = cands
        print(f"  epsilon={eps_factor:.0e}: {len(cands)} tight constraints")

    best_c = C0
    best_f = f.copy()

    # Experiment: various tight constraint sets x delta bounds
    tight_sets = []
    for eps_factor in [0.0, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3]:
        cands = tight_by_eps[eps_factor]
        if 1 <= len(cands) <= 500:
            tight_sets.append((eps_factor, cands))

    if not tight_sets:
        # Fall back to just argmax
        tight_sets = [(0.0, np.array([np.argmax(autoconv)]))]

    delta_bounds = [None, 0.0001 * max_f, 0.001 * max_f, 0.01 * max_f, 0.1 * max_f]

    for eps_factor, tight_indices in tight_sets:
        n_tight = len(tight_indices)
        for max_delta in delta_bounds:
            delta_str = f"{max_delta:.2e}" if max_delta is not None else "unbounded"
            print(f"\n-- eps={eps_factor:.0e}, n_tight={n_tight}, max_delta={delta_str} --")

            t0 = time.time()
            try:
                result, _, max_autoconv = _run_lp_experiment(
                    f, dx, tight_indices, max_delta)
            except Exception as e:
                print(f"  LP exception: {e}")
                continue
            t_lp = time.time() - t0

            if not result.success:
                print(f"  LP failed in {t_lp:.2f}s: {result.message}")
                continue

            t_opt = result.x[-1]
            delta_f = result.x[:N]
            print(f"  t={t_opt:.4e}, ||d||={np.linalg.norm(delta_f):.3e}, "
                  f"max_d={delta_f.max():.3e}, time={t_lp:.2f}s")

            if t_opt >= 0:
                print(f"  t >= 0, no descent direction")
                continue

            # Line search
            if max_delta is not None and max_delta < 0.01 * max_f:
                alphas = [1e-3, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]
            else:
                alphas = [1e-6, 1e-5, 1e-4, 1e-3, 0.01, 0.1, 1.0]

            found_better = False
            for alpha in alphas:
                f_trial = np.maximum(f + alpha * delta_f, 0.0)
                c_trial = compute_c_f64(f_trial)
                marker = " <-- BETTER" if c_trial < best_c else ""
                print(f"    alpha={alpha:.2e}: C={c_trial:.12f}{marker}")
                if c_trial < best_c:
                    best_c = c_trial
                    best_f = f_trial.copy()
                    found_better = True

            if found_better:
                print(f"  *** New best C={best_c:.12f} ***")
                break

        if best_c < C0 - 1e-9:
            break
        if time.time() - t_start > 200:
            print("\nTime limit reached")
            break

    print(f"\n{'='*60}")
    print(f"Final best C: {best_c:.12f}")
    print(f"Improvement: {C0 - best_c:.6e}")
    print(f"Total time: {time.time() - t_start:.1f}s")
    return best_f
