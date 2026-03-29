"""Float64 compute_c matching validate.py exactly.

Uses numpy float64 throughout (no JAX). Precision: ~1e-15.
Use for all accept/reject decisions in optimization.
Use compute_c() (JAX float32) only for quick sanity checks or gradient computation.
"""

import numpy as np


def compute_c_f64(f_array):
    """Compute the autocorrelation constant C in float64, matching validate.py exactly.

    Uses FFT-based autoconvolution with numpy float64 arithmetic throughout.
    Returns max(f*f * dx) / (integral_f)^2, identical to validate.py's validate().

    Args:
        f_array: 1D array-like of non-negative function values on [-1/4, 1/4].
            Will be converted to numpy float64. Negative values are clamped to 0.

    Returns:
        float: C value in float64 precision.

    Raises:
        ValueError: If array is empty, contains non-finite values, or integral is ~0.

    Examples:
        >>> import numpy as np
        >>> f = np.ones(1000) * 0.1
        >>> c = compute_c_f64(f)
        >>> # c should equal 2.0 for a constant function
        >>> abs(c - 2.0) < 1e-10
        True
    """
    f_values = np.asarray(f_array, dtype=np.float64)

    if f_values.ndim != 1:
        raise ValueError(f"Expected 1D array, got shape {f_values.shape}")
    if f_values.size == 0:
        raise ValueError("Array cannot be empty")
    if not np.all(np.isfinite(f_values)):
        raise ValueError("Some values are NaN or infinite")

    domain_width = 0.5
    dx = domain_width / len(f_values)

    f_nonneg = np.maximum(f_values, 0.0)

    integral_f = np.sum(f_nonneg) * dx

    if integral_f**2 < 1e-9:
        raise ValueError("Function integral is close to zero, ratio is unstable.")

    N = len(f_values)
    padded_f = np.pad(f_nonneg, (0, N))
    fft_f = np.fft.fft(padded_f)
    conv_f_f = np.fft.ifft(fft_f * fft_f).real

    scaled_conv = conv_f_f * dx
    max_conv = np.max(scaled_conv)

    c1 = max_conv / (integral_f**2)

    return float(c1)
