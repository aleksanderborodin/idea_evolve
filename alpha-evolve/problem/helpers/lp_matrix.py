"""Vectorized LP constraint matrix builder for autocorrelation refinement.

Provides the core LP formulation for linearized autocorrelation constraint
refinement. The LP improves the current solution f by finding a perturbation
delta that reduces the autoconvolution maximum while preserving the integral
and non-negativity.

Background: LP Formulation
---------------------------
Given solution f with autoconvolution A = f★f and max value A_max = max(A),
define "tight" indices T = {j : A[j] ≈ A_max}. A perturbation delta must
satisfy, for all j in T:

    (f + delta) ★ (f + delta) [j]  ≤  A_max - epsilon
    ≈  A[j] + 2*(f ★ delta)[j] + O(delta^2)

Dropping the O(delta^2) term (linearized), the constraint is:
    2*(f ★ delta)[j]  ≤  A_max - A[j] - epsilon
    2 * sum_k f_padded[(j-k) % M] * delta[k] * dx  ≤  rhs[j]

This gives the constraint matrix:
    A_ub[j, k] = 2 * f_padded[(j - k) % M_fft] * dx

The LP objective is to minimize the new maximum, which requires a slack
variable formulation. See scipy_lp_solve() for the full setup.

Memory/scaling notes (from gen006 full_1 debrief):
- At N=30000: building A_ub with Python loops used 7GB RAM and 19+ minutes.
- This module uses vectorized numpy indexing: O(n_tight * N) with no Python loops.
- At N=30000, n_tight=100: A_ub is 100×30000 = 3M float64 = ~24MB. Fine.
- The LP itself (HiGHS via scipy) handles 100 constraints / 30000 variables easily.
"""

import numpy as np


def build_lp_matrix(f, tight_indices, dx=None):
    """Build linearized LP constraint matrix A_ub for autocorrelation refinement.

    Constructs A_ub[j, k] = 2 * f_padded[(j - k) % M_fft] * dx using
    vectorized numpy indexing. No Python loops — O(n_tight * N) time and space.

    The constraint matrix represents the linearized condition:
        2 * (f ★ delta)[j] * dx ≤ rhs[j]  for all tight j
    which in matrix form is: A_ub @ delta ≤ b_ub

    Args:
        f: 1D array-like of non-negative function values, length N.
            Negative values are clamped to 0 (matching validate.py convention).
        tight_indices: 1D array-like of int, shape (n_tight,). Indices j in
            [0, M_fft-1] = [0, 2N-1] where autoconvolution is near maximum.
            Typically from tight_constraint_indices() in cross_convolution_f64.py.
        dx: Grid spacing. Default: 0.5 / N.

    Returns:
        A_ub: 2D numpy float64 array, shape (n_tight, N). The LP constraint
            matrix. A_ub @ delta gives the linearized change in autoconvolution
            at each tight index j.
        M_fft: int. The FFT array length (2N), for use in incremental updates.
        f_padded: 1D float64 array of length M_fft. The zero-padded f used
            to build A_ub (needed for incremental autoconvolution updates).

    Examples:
        >>> import numpy as np
        >>> N = 100
        >>> f = np.ones(N) * 0.1
        >>> tight = np.array([N-1])  # peak of autoconvolution for constant f
        >>> A_ub, M, fp = build_lp_matrix(f, tight)
        >>> A_ub.shape == (1, N)
        True
        >>> # For constant f and j=N-1, A_ub[0, k] = 2 * f[N-1-k] * dx = 2 * 0.1 * dx
        >>> # All entries should be equal (constant f)
        >>> dx = 0.5 / N
        >>> np.allclose(A_ub[0, :], 2.0 * 0.1 * dx)
        True
    """
    f = np.asarray(f, dtype=np.float64)
    if f.ndim != 1 or len(f) == 0:
        raise ValueError("f must be a non-empty 1D array")

    f_nonneg = np.maximum(f, 0.0)
    N = len(f_nonneg)
    if dx is None:
        dx = 0.5 / N

    M_fft = 2 * N
    f_padded = np.pad(f_nonneg, (0, N))  # shape (M_fft,)

    tight_indices = np.asarray(tight_indices, dtype=np.int64)
    if tight_indices.ndim != 1:
        raise ValueError("tight_indices must be a 1D array")
    if len(tight_indices) == 0:
        return np.empty((0, N), dtype=np.float64), M_fft, f_padded

    n_tight = len(tight_indices)

    # k_arr: variable indices [0, N-1]
    k_arr = np.arange(N, dtype=np.int64)  # shape (N,)

    # Outer subtraction: indices[j, k] = (tight_indices[j] - k) % M_fft
    # Shape: (n_tight, N)
    indices = (tight_indices[:, np.newaxis] - k_arr[np.newaxis, :]) % M_fft

    # Vectorized gather: A_ub[j, k] = 2 * f_padded[(j - k) % M] * dx
    A_ub = 2.0 * f_padded[indices] * dx

    return A_ub, M_fft, f_padded


def build_lp_rhs(autoconv, tight_indices, epsilon=0.0):
    """Build the right-hand side vector b_ub for the LP.

    b_ub[j] = A_max - autoconv[tight_indices[j]] - epsilon

    For a perturbation delta to strictly reduce the maximum, we need
    A_ub @ delta <= b_ub, where b_ub[j] ≈ 0 for the tightest constraints.
    Using epsilon > 0 forces the perturbation to strictly improve.

    Args:
        autoconv: 1D float64 array of length M_fft (from autoconvolve()).
        tight_indices: 1D int array of tight constraint indices.
        epsilon: Optional target improvement margin. Default 0.0 (allow same max).
            Use a small positive value (e.g. 1e-8) to force strict improvement.

    Returns:
        b_ub: 1D float64 array of shape (n_tight,). Right-hand side values.
        A_max: float. The maximum autoconvolution value.
    """
    autoconv = np.asarray(autoconv, dtype=np.float64)
    tight_indices = np.asarray(tight_indices, dtype=np.int64)

    A_max = np.max(autoconv)
    b_ub = A_max - autoconv[tight_indices] - epsilon

    return b_ub, A_max


def scipy_lp_solve(f, tight_indices, autoconv, dx=None, epsilon=1e-9,
                   max_step=0.1, integral_tol=1e-10):
    """Solve the linearized LP to find an improving perturbation delta.

    Formulates and solves:
        minimize    t                            (minimize new max)
        subject to  A_ub @ delta <= b_ub + t    (tight constraint slackening)
                    sum(delta) = 0               (preserve integral)
                    f + delta >= 0               (non-negativity)
                    |delta[k]| <= max_step       (step size bound)
                    t >= 0                       (slack must be non-negative improvement)

    NOTE: This solves for a REDUCTION in the maximum. The objective t is the
    amount by which the maximum changes. If the optimal t < 0, the LP found
    an improving direction.

    Practical guidance (from gen006 full_1 debrief):
    - Works well at N=1000-3000 (reduced resolution).
    - At N=30000 with n_tight~100: A_ub is ~24MB, LP should solve in seconds.
    - Use epsilon_rel=1e-6 for tight_constraint_indices to get 1-3 constraints.

    Args:
        f: 1D float64 array, length N.
        tight_indices: 1D int array from tight_constraint_indices().
        autoconv: 1D float64 array of length 2N from autoconvolve().
        dx: Grid spacing (default 0.5/N).
        epsilon: Minimum improvement target. Default 1e-9.
        max_step: Maximum absolute perturbation per element. Default 0.1.
        integral_tol: Absolute tolerance for integral-preserving constraint.

    Returns:
        result: dict with keys:
            'delta': 1D float64 array of length N. The optimal perturbation.
            'predicted_improvement': float. Expected change in max (negative = improvement).
            'status': int. 0 = optimal, 1 = infeasible, 2 = unbounded, etc.
            'message': str. Solver message.
        None if scipy.optimize.linprog is not available.
    """
    try:
        from scipy.optimize import linprog
    except ImportError:
        return None

    f = np.asarray(f, dtype=np.float64)
    N = len(f)
    if dx is None:
        dx = 0.5 / N

    A_ub, M_fft, f_padded = build_lp_matrix(f, tight_indices, dx=dx)
    b_ub_base, A_max = build_lp_rhs(autoconv, tight_indices, epsilon=epsilon)
    n_tight = len(tight_indices)

    # Variables: [delta_0, ..., delta_{N-1}, t]
    # Total variables: N + 1
    n_vars = N + 1

    # Objective: minimize t (last variable)
    c_obj = np.zeros(n_vars)
    c_obj[-1] = 1.0

    # Inequality constraints: A_ub @ delta - t <= b_ub_base
    # In matrix form: [A_ub | -1] @ [delta; t] <= b_ub_base
    A_ineq = np.hstack([A_ub, -np.ones((n_tight, 1))])
    b_ineq = b_ub_base

    # Equality constraint: sum(delta) * dx = 0 (integral preservation)
    A_eq = np.zeros((1, n_vars))
    A_eq[0, :N] = dx
    b_eq = np.zeros(1)

    # Bounds: -max_step <= delta[k] <= max_step, f[k]+delta[k] >= 0, t >= 0
    bounds = []
    for k in range(N):
        lo = max(-max_step, -f[k])   # non-negativity: delta[k] >= -f[k]
        hi = max_step
        bounds.append((lo, hi))
    bounds.append((0.0, None))  # t >= 0

    result = linprog(
        c_obj,
        A_ub=A_ineq,
        b_ub=b_ineq,
        A_eq=A_eq,
        b_eq=b_eq,
        bounds=bounds,
        method='highs',
        options={'disp': False}
    )

    if result.status == 0:
        delta = result.x[:N]
        t = result.x[-1]
        return {
            'delta': delta,
            'predicted_improvement': -t,  # negative t means improvement
            'status': result.status,
            'message': result.message
        }
    else:
        return {
            'delta': np.zeros(N),
            'predicted_improvement': 0.0,
            'status': result.status,
            'message': result.message
        }
