"""Sensitivity analysis for autocorrelation solutions.

Computes the gradient dC/df[i] for each element of a solution array.
Supports two modes:
- Float32 JAX autodiff (default): fast, differentiable, ~1e-6 precision
- Float64 finite differences: slow, not differentiable, ~1e-8 precision

Use float64 mode for well-optimized solutions (C < 1.505) where float32
gradient rankings are unreliable (see pattern_008).
"""

import numpy as np


def sensitivity_map(f_array, use_float64=False):
    """Compute dC/df[i] for all elements.

    Args:
        f_array: 1D JAX or NumPy array of non-negative function values.
        use_float64: If True, use numpy float64 finite differences with
            compute_c_f64. If False (default), use JAX float32 autodiff
            with compute_c. Float64 mode is ~N times slower but essential
            for micro-optimization below C~1.505.

    Returns:
        gradients: Array of same shape, where gradients[i] = dC/df[i].
            Returns numpy float64 array if use_float64=True, JAX float32
            array if use_float64=False.

    Examples:
        >>> import numpy as np
        >>> f = np.ones(1000) * 0.1
        >>> grads_f32 = sensitivity_map(f, use_float64=False)
        >>> grads_f64 = sensitivity_map(f, use_float64=True)
        >>> # For well-optimized solutions, top-20 elements may differ
    """
    if use_float64:
        return _sensitivity_f64(f_array)
    else:
        return _sensitivity_f32(f_array)


def _sensitivity_f32(f_array):
    """Float32 JAX autodiff sensitivity (original implementation)."""
    import jax
    import jax.numpy as jnp
    from helpers.core import compute_c

    f_jax = jnp.asarray(f_array, dtype=jnp.float32)
    grad_fn = jax.grad(lambda x: compute_c(x).astype(jnp.float32))
    return grad_fn(f_jax)


def _sensitivity_f64(f_array, delta=1e-8):
    """Float64 central finite differences using compute_c_f64."""
    from helpers.compute_c_f64 import compute_c_f64

    f = np.asarray(f_array, dtype=np.float64)
    n = len(f)
    grads = np.empty(n, dtype=np.float64)

    for i in range(n):
        f_plus = f.copy()
        f_minus = f.copy()
        f_plus[i] += delta
        f_minus[i] -= delta
        # Clamp to non-negative after perturbation
        f_minus[i] = max(f_minus[i], 0.0)
        c_plus = compute_c_f64(f_plus)
        c_minus = compute_c_f64(f_minus)
        actual_delta = f_plus[i] - f_minus[i]
        if actual_delta > 0:
            grads[i] = (c_plus - c_minus) / actual_delta
        else:
            grads[i] = 0.0

    return grads
