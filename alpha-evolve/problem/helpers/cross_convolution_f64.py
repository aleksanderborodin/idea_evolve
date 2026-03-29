"""Float64 cross-convolution and tight-constraint helpers for LP refinement.

Provides the core building blocks for LP-based autocorrelation refinement:
1. Cross-convolution (f ★ g) via FFT in float64
2. Tight constraint index identification

Background
----------
The LP refinement approach linearizes the autoconvolution constraint around the
current solution f. The constraint matrix has the structure:
    A_ub[j, k] = 2 * (f ★ e_k)[j] * dx = 2 * f_padded[(j - k) % M] * dx
where j indexes tight constraints and k indexes variables.

This module provides the cross-convolution primitive and constraint-tightness
analysis. See lp_matrix.py for the full constraint matrix builder.
"""

import numpy as np


def cross_convolve(f, g, dx=None):
    """Compute (f ★ g)(t) via FFT in float64.

    Computes the discrete convolution (f ★ g)(n) = sum_k f[k] * g[n-k] * dx
    using zero-padded FFT. The result has length 2N-1 (linear convolution).

    Both f and g must be 1D arrays of the same length N. Uses zero-padding
    to length 2N to avoid circular aliasing.

    For autoconvolution (f ★ f), this matches compute_c_f64's internal
    computation exactly (same zero-padding, same indexing, same dx convention).

    Args:
        f: 1D array-like of real values, length N.
        g: 1D array-like of real values, length N.
        dx: Grid spacing. Default: 0.5 / N (the standard domain [-1/4, 1/4]).
            Pass dx=1.0 to get the unscaled convolution sum.

    Returns:
        conv: 1D numpy float64 array of length 2N-1. The linear convolution
            (f ★ g) scaled by dx.

    Raises:
        ValueError: If f and g have different lengths or are empty.

    Examples:
        >>> import numpy as np
        >>> N = 1000
        >>> f = np.ones(N) * 0.1
        >>> # Autoconvolution of constant function: max value = N * f[0]^2 * dx
        >>> ac = cross_convolve(f, f)
        >>> dx = 0.5 / N
        >>> # Peak at index N-1 (center), value = N * 0.01 * dx = 0.5 * 0.01 = 0.005
        >>> abs(np.max(ac) - 0.5 * 0.01) < 1e-12
        True
        >>> # cross_convolve(f, f) matches compute_c_f64's internal computation
        >>> from helpers.compute_c_f64 import compute_c_f64
        >>> f2 = np.abs(np.random.default_rng(0).standard_normal(500)) * 0.1
        >>> ac2 = cross_convolve(f2, f2)
        >>> c = compute_c_f64(f2)
        >>> integral = np.sum(np.maximum(f2, 0)) * (0.5 / 500)
        >>> abs(np.max(ac2) / integral**2 - c) < 1e-12
        True
    """
    f = np.asarray(f, dtype=np.float64)
    g = np.asarray(g, dtype=np.float64)

    if f.ndim != 1 or g.ndim != 1:
        raise ValueError("f and g must be 1D arrays")
    if len(f) != len(g):
        raise ValueError(f"f and g must have same length: {len(f)} != {len(g)}")
    if len(f) == 0:
        raise ValueError("Arrays cannot be empty")

    N = len(f)
    if dx is None:
        dx = 0.5 / N

    M = 2 * N  # FFT size: zero-pad to avoid circular aliasing

    f_padded = np.pad(f, (0, N))
    g_padded = np.pad(g, (0, N))

    fft_f = np.fft.fft(f_padded)
    fft_g = np.fft.fft(g_padded)

    conv_full = np.fft.ifft(fft_f * fft_g).real

    # Linear convolution has length 2N-1; trim last element (wrap-around artifact)
    conv = conv_full[:2 * N - 1] * dx

    return conv


def autoconvolve(f, dx=None):
    """Compute (f ★ f)(t) in float64, returning the full M=2N padded array.

    Unlike cross_convolve which returns length 2N-1, this returns length M=2N
    (matching compute_c_f64 and incremental_autoconv_update conventions).
    The last element (index 2N-1) is a wrap-around artifact and is nearly zero
    for properly zero-padded inputs.

    Use this when you need the autoconvolution array for:
    - Feeding into incremental_autoconv_update (requires length M=2N)
    - Computing max_conv for C computation

    For cross-convolution between two different arrays, use cross_convolve().

    Args:
        f: 1D array-like of non-negative values, length N. Negative values
            are clamped to 0 (matching validate.py behavior).
        dx: Grid spacing. Default: 0.5 / N.

    Returns:
        autoconv: 1D numpy float64 array of length 2N. The autoconvolution
            array IFFT(FFT(f_padded)^2).real * dx, same convention as
            compute_c_f64 and incremental_autoconv_update.
        f_padded: 1D numpy float64 array of length 2N. The zero-padded f
            array used for the computation (useful for incremental updates).
        dx: float. The grid spacing used.
        M_fft: int. The FFT size (2N).

    Examples:
        >>> import numpy as np
        >>> f = np.ones(1000) * 0.1
        >>> ac, fp, dx, M = autoconvolve(f)
        >>> # max should equal 0.5 * 0.01 = 0.005 (constant function)
        >>> abs(np.max(ac) - 0.005) < 1e-12
        True
    """
    f = np.asarray(f, dtype=np.float64)
    if f.ndim != 1 or len(f) == 0:
        raise ValueError("f must be a non-empty 1D array")

    f_nonneg = np.maximum(f, 0.0)
    N = len(f_nonneg)
    if dx is None:
        dx = 0.5 / N

    M = 2 * N
    f_padded = np.pad(f_nonneg, (0, N))
    fft_f = np.fft.fft(f_padded)
    autoconv = np.fft.ifft(fft_f * fft_f).real * dx

    return autoconv, f_padded, dx, M


def tight_constraint_indices(f, epsilon_rel=1e-5):
    """Find indices where autoconvolution is within epsilon of its maximum.

    Returns the set of indices j where (f★f)(j) >= (1 - epsilon_rel) * max(f★f).
    These are the "near-tight" constraints in the LP formulation — the indices
    where the inequality max(f★f) >= C*(∫f)^2 is most at risk of being violated
    by a perturbation delta.

    IMPORTANT: Uses the full length-2N autoconvolution array (M_fft convention),
    consistent with compute_c_f64 and incremental_autoconv_update. Indices are
    in [0, 2N-1].

    Practical guidance:
    - epsilon_rel=1e-6: Returns 1-3 truly tight constraints (fastest LP, smallest)
    - epsilon_rel=1e-5: Returns ~5-20 constraints (recommended starting point)
    - epsilon_rel=1e-3: Returns many constraints, LP may be slow at N=30k

    Args:
        f: 1D array-like of non-negative values, length N.
        epsilon_rel: Relative tolerance. Index j is included if
            autoconv[j] >= max_autoconv * (1 - epsilon_rel).
            Default: 1e-5.

    Returns:
        indices: 1D numpy int64 array of indices (in [0, 2N-1]) where
            autoconvolution is within epsilon of the maximum.

    Examples:
        >>> import numpy as np
        >>> # Constant function: autoconvolution is triangular, peaked at N-1
        >>> f = np.ones(1000) * 0.1
        >>> idx = tight_constraint_indices(f, epsilon_rel=1e-10)
        >>> # For constant function, peak is sharp at index N-1 = 999
        >>> len(idx) == 1
        True
        >>> idx[0] == 999
        True
    """
    f = np.asarray(f, dtype=np.float64)
    if f.ndim != 1 or len(f) == 0:
        raise ValueError("f must be a non-empty 1D array")

    autoconv, _, _, _ = autoconvolve(f)

    max_val = np.max(autoconv)
    if max_val < 1e-15:
        raise ValueError("Autoconvolution maximum is near zero — function may be trivial")

    threshold = max_val * (1.0 - epsilon_rel)
    indices = np.where(autoconv >= threshold)[0].astype(np.int64)

    return indices
