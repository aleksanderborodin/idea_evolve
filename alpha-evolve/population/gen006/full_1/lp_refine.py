"""LP-based refinement of the TTT-Discover 30k array.

This script:
1. Loads the TTT-Discover array from best.py
2. Computes the autoconvolution and identifies near-tight constraints
3. Formulates a linearized LP to find descent directions
4. Iterates to improve C
5. Saves the result as a baked array in sol01.py
"""
import numpy as np
import sys
import os
import time
import importlib.util

# Add problem dir to path so we can import helpers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'problem'))

def compute_c_f64(f):
    """Compute C in float64, matching validate.py exactly."""
    N = len(f)
    dx = 0.5 / N
    padded = np.pad(f, (0, N))
    F = np.fft.fft(padded)
    autoconv = np.fft.ifft(F * F).real * dx
    integral = np.sum(f) * dx
    return float(np.max(autoconv) / (integral ** 2)), autoconv

def compute_autoconv_f64(f):
    """Compute autoconvolution in float64."""
    N = len(f)
    dx = 0.5 / N
    padded = np.pad(f, (0, N))
    F = np.fft.fft(padded)
    autoconv = np.fft.ifft(F * F).real * dx
    integral = np.sum(f) * dx
    return autoconv, integral, dx

def compute_cross_conv_via_fft(f, delta, dx):
    """Compute cross-convolution f★delta via FFT."""
    N = len(f)
    padded_f = np.pad(f, (0, N))
    padded_d = np.pad(delta, (0, N))
    F_f = np.fft.fft(padded_f)
    F_d = np.fft.fft(padded_d)
    cross = np.fft.ifft(F_f * F_d).real * dx
    return cross

def analyze_tightness(autoconv, epsilon=0.01):
    """Find near-tight constraint indices."""
    max_val = np.max(autoconv)
    threshold = max_val * (1 - epsilon)
    tight_indices = np.where(autoconv >= threshold)[0]
    return tight_indices

def lp_step_sparse(f, tight_indices, autoconv, integral, dx):
    """
    Solve linearized LP for a descent direction using sparse formulation.

    Linearization: (f+δ)★(f+δ) ≈ f★f + 2·(f★δ)

    For each tight index j:
        f★f[j] + 2·(f★δ)[j] <= t

    minimize t over delta, t
    subject to:
        f[i] + delta[i] >= 0
        sum(delta) = 0
        |delta[i]| <= max_pert
    """
    from scipy.optimize import linprog
    from scipy.sparse import csr_matrix

    N = len(f)
    max_autoconv = np.max(autoconv)

    # Only perturb elements where f > threshold
    active_mask = f > 1e-10
    active_indices = np.where(active_mask)[0]
    n_active = len(active_indices)

    if n_active > 3000:
        # Rank by contribution to peak
        peak_idx = np.argmax(autoconv)
        contributions = np.zeros(N)
        for i in active_indices:
            j = peak_idx - i
            if 0 <= j < N:
                contributions[i] = f[i] * f[j]
        top_k = 2000
        sorted_idx = np.argsort(-contributions[active_indices])[:top_k]
        active_indices = active_indices[sorted_idx]
        n_active = len(active_indices)

    n_tight = len(tight_indices)
    print(f"  LP: {n_active} variables, {n_tight} tight constraints")

    # Variables: delta[0..n_active-1], t
    n_vars = n_active + 1

    # Build constraint matrix for tight constraints:
    # For tight index j: sum_k (2 * f[j - active[k]] * dx) * delta[k] - t <= -autoconv[j]
    rows = []
    cols = []
    data = []
    b_ub = []

    for row_idx, j in enumerate(tight_indices):
        for k_idx, k in enumerate(active_indices):
            partner = j - k
            if 0 <= partner < N and f[partner] > 1e-15:
                rows.append(row_idx)
                cols.append(k_idx)
                data.append(2.0 * f[partner] * dx)
        # -t coefficient
        rows.append(row_idx)
        cols.append(n_active)  # t variable
        data.append(-1.0)
        b_ub.append(-autoconv[j])

    A_ub = csr_matrix((data, (rows, cols)), shape=(n_tight, n_vars))
    b_ub = np.array(b_ub)

    # Equality: sum(delta) = 0
    eq_data = np.ones(n_active + 1)
    eq_data[-1] = 0.0  # t not in equality
    A_eq = csr_matrix(eq_data.reshape(1, -1))
    b_eq = np.array([0.0])

    # Bounds
    max_pert = 0.005
    bounds = []
    for k_idx, k in enumerate(active_indices):
        lb = max(-f[k], -max_pert)
        bounds.append((lb, max_pert))
    bounds.append((None, None))  # t unbounded

    # Objective: minimize t
    c = np.zeros(n_vars)
    c[-1] = 1.0

    try:
        result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                        bounds=bounds, method='highs',
                        options={'time_limit': 120, 'presolve': True})

        if result.success:
            delta_active = result.x[:n_active]
            t_opt = result.x[-1]
            print(f"  LP solved: t_opt = {t_opt:.12f}, current max = {max_autoconv:.12f}")
            improvement = max_autoconv - t_opt
            print(f"  Predicted improvement in max(autoconv): {improvement:.2e}")
            print(f"  Delta norm: {np.linalg.norm(delta_active):.6e}, "
                  f"range: [{np.min(delta_active):.6e}, {np.max(delta_active):.6e}]")

            delta_full = np.zeros(N)
            delta_full[active_indices] = delta_active
            return delta_full, t_opt
        else:
            print(f"  LP failed: {result.message}")
            return None, None
    except Exception as e:
        print(f"  LP error: {e}")
        return None, None

def lp_refine_iterative(f_init, n_iters=20):
    """Run LP refinement iteratively."""
    f = f_init.copy()
    N = len(f)

    autoconv, integral, dx = compute_autoconv_f64(f)
    C_init = np.max(autoconv) / (integral ** 2)
    print(f"Initial C = {C_init:.12f}")

    best_f = f.copy()
    best_C = C_init

    epsilon_values = [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.02, 0.05, 0.1]

    for iteration in range(n_iters):
        print(f"\n=== LP Iteration {iteration + 1}/{n_iters} ===")

        autoconv, integral, dx = compute_autoconv_f64(f)
        C_current = np.max(autoconv) / (integral ** 2)
        print(f"Current C = {C_current:.12f}")

        improved = False
        for eps in epsilon_values:
            tight_indices = analyze_tightness(autoconv, epsilon=eps)

            if len(tight_indices) < 2:
                continue

            delta, t_opt = lp_step_sparse(f, tight_indices, autoconv, integral, dx)

            if delta is None:
                continue

            # Try different step sizes
            for alpha in [1.0, 0.5, 0.2, 0.1, 0.05, 0.01, 0.005, 0.001]:
                f_new = f + alpha * delta
                f_new = np.maximum(f_new, 0)

                autoconv_new, integral_new, _ = compute_autoconv_f64(f_new)
                C_new = np.max(autoconv_new) / (integral_new ** 2)

                if C_new < best_C:
                    print(f"  *** IMPROVEMENT: eps={eps}, alpha={alpha}, C = {C_new:.12f} (delta = {C_new - best_C:.2e})")
                    best_f = f_new.copy()
                    best_C = C_new
                    f = f_new.copy()
                    improved = True
                    break

            if improved:
                break

        if not improved:
            print(f"  No improvement found at iteration {iteration + 1}")
            # Try also allowing zero elements to become nonzero
            print("  Trying with expanded variable set (including zero elements)...")
            improved2 = try_expanded_lp(f, autoconv, integral, dx)
            if improved2 is not None:
                f_new, C_new = improved2
                if C_new < best_C:
                    print(f"  *** IMPROVEMENT from expanded LP: C = {C_new:.12f}")
                    best_f = f_new.copy()
                    best_C = C_new
                    f = f_new.copy()
                    improved = True

        if not improved:
            print("  Stopping: no improvement possible")
            break

    print(f"\nFinal C = {best_C:.12f} (improvement: {C_init - best_C:.2e})")
    return best_f, best_C

def try_expanded_lp(f, autoconv, integral, dx):
    """Try LP with expanded variable set including some zero elements near nonzero ones."""
    from scipy.optimize import linprog
    from scipy.sparse import csr_matrix

    N = len(f)
    max_autoconv = np.max(autoconv)

    # Include all nonzero elements plus neighbors of nonzero elements
    nonzero_mask = f > 1e-10
    expanded_mask = nonzero_mask.copy()
    # Add neighbors
    for shift in [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5]:
        shifted = np.roll(nonzero_mask, shift)
        expanded_mask |= shifted

    active_indices = np.where(expanded_mask)[0]
    n_active = len(active_indices)

    if n_active > 4000:
        # Limit
        # Prioritize nonzero elements and their immediate neighbors
        near_mask = nonzero_mask.copy()
        for shift in [-2, -1, 1, 2]:
            shifted = np.roll(nonzero_mask, shift)
            near_mask |= shifted
        active_indices = np.where(near_mask)[0]
        n_active = len(active_indices)

    # Use moderate tightness
    tight_indices = analyze_tightness(autoconv, epsilon=0.01)
    n_tight = len(tight_indices)

    if n_tight < 2:
        return None

    print(f"  Expanded LP: {n_active} variables, {n_tight} tight constraints")

    n_vars = n_active + 1
    rows = []
    cols = []
    data = []
    b_ub = []

    for row_idx, j in enumerate(tight_indices):
        for k_idx, k in enumerate(active_indices):
            partner = j - k
            if 0 <= partner < N and f[partner] > 1e-15:
                rows.append(row_idx)
                cols.append(k_idx)
                data.append(2.0 * f[partner] * dx)
        rows.append(row_idx)
        cols.append(n_active)
        data.append(-1.0)
        b_ub.append(-autoconv[j])

    A_ub = csr_matrix((data, (rows, cols)), shape=(n_tight, n_vars))
    b_ub = np.array(b_ub)

    eq_data = np.ones(n_active + 1)
    eq_data[-1] = 0.0
    A_eq = csr_matrix(eq_data.reshape(1, -1))
    b_eq = np.array([0.0])

    max_pert = 0.005
    bounds = []
    for k_idx, k in enumerate(active_indices):
        lb = max(-f[k], -max_pert)
        bounds.append((lb, max_pert))
    bounds.append((None, None))

    c = np.zeros(n_vars)
    c[-1] = 1.0

    try:
        result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                        bounds=bounds, method='highs',
                        options={'time_limit': 120, 'presolve': True})

        if result.success:
            delta_active = result.x[:n_active]
            delta_full = np.zeros(N)
            delta_full[active_indices] = delta_active

            for alpha in [1.0, 0.5, 0.1, 0.01]:
                f_new = f + alpha * delta_full
                f_new = np.maximum(f_new, 0)
                autoconv_new, integral_new, _ = compute_autoconv_f64(f_new)
                C_new = np.max(autoconv_new) / (integral_new ** 2)
                if C_new < np.max(autoconv) / (integral ** 2):
                    return f_new, C_new
        return None
    except:
        return None

def main():
    print("Loading TTT-Discover array from best.py...")
    best_path = '/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen004/research_1/sol01.py'
    spec = importlib.util.spec_from_file_location("best", best_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    f = mod.entrypoint()
    f = np.asarray(f, dtype=np.float64)

    print(f"Array shape: {f.shape}")
    print(f"Non-zero elements (>1e-8): {np.sum(f > 1e-8)}")
    print(f"Non-zero elements (>1e-4): {np.sum(f > 1e-4)}")

    # Initial analysis
    autoconv, integral, dx = compute_autoconv_f64(f)
    C_init = np.max(autoconv) / (integral ** 2)
    peak_idx = np.argmax(autoconv)
    print(f"Initial C = {C_init:.12f}")
    print(f"Autoconv peak at index {peak_idx}, value = {np.max(autoconv):.12f}")
    print(f"Integral = {integral:.10f}")
    print(f"dx = {dx:.10e}")

    # Analyze tightness at different epsilons
    print("\nTightness analysis:")
    for eps in [1e-6, 1e-5, 1e-4, 0.001, 0.01, 0.05, 0.1]:
        tight = analyze_tightness(autoconv, epsilon=eps)
        print(f"  eps={eps:.0e}: {len(tight)} near-tight constraints")

    # Analyze the peak and nearby values
    print(f"\nAutoconv around peak (index {peak_idx}):")
    for offset in range(-5, 6):
        idx = peak_idx + offset
        if 0 <= idx < len(autoconv):
            ratio = autoconv[idx] / np.max(autoconv)
            print(f"  [{idx}] = {autoconv[idx]:.12f}  (ratio to peak: {ratio:.10f})")

    # Run LP refinement
    t0 = time.time()
    best_f, best_C = lp_refine_iterative(f, n_iters=15)
    elapsed = time.time() - t0
    print(f"\nTotal LP refinement time: {elapsed:.1f}s")

    # Save the optimized array
    out_path = os.path.join(os.path.dirname(__file__), 'sol01.py')
    print(f"\nSaving array (C = {best_C:.12f})")
    save_baked_solution(best_f, best_C, out_path)

def save_baked_solution(f, C_val, path):
    """Save the array as a baked solution."""
    lines = [
        f"# fitness: {C_val}",
        "# LP-refined TTT-Discover 30k array",
        "# Method: Linearized LP with near-tight constraint relaxation",
        "import numpy as np",
        "",
        "def entrypoint():",
        "    return np.array([",
    ]

    vals = f.tolist()
    for i in range(0, len(vals), 5):
        chunk = vals[i:i+5]
        line = "        " + ", ".join(f"{v:.17e}" for v in chunk) + ","
        lines.append(line)

    lines.append("    ])")

    with open(path, 'w') as fout:
        fout.write('\n'.join(lines) + '\n')
    print(f"Saved to {path}")

if __name__ == '__main__':
    main()
