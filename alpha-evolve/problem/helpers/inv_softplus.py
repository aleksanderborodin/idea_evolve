"""Safe inverse softplus for warm-start optimization.

Converts non-negative function values to raw parameters such that
softplus(raw_params) ≈ f. Handles near-zero elements safely by clamping
to avoid log(0) and gradient vanishing, and clips output to prevent
frozen gradients at extreme values.
"""

import jax.numpy as jnp


def inv_softplus_safe(f, eps=1e-8, clip_min=-10.0, clip_max=30.0):
    """Convert non-negative function values to softplus raw_params.

    The inverse softplus formula is: raw = log(exp(f) - 1).
    For large f (> 20), uses the approximation raw ≈ f to avoid overflow.
    Near-zero values are floored to eps before computing the inverse,
    and the output is clipped to [clip_min, clip_max].

    Uses float64 internally for precision, returns same dtype as input.

    Args:
        f: Array of non-negative function values.
        eps: Floor value to prevent log(0) and gradient vanishing.
            Elements below eps are effectively mapped to clip_min.
        clip_min: Minimum output value. Default -10.0 (softplus(-10) ≈ 4.5e-5).
        clip_max: Maximum output value. Default 30.0 (softplus(30) ≈ 30.0).

    Returns:
        raw_params: Array where jax.nn.softplus(raw_params) ≈ f.

    Examples:
        >>> import jax.numpy as jnp
        >>> import jax
        >>> f = jnp.array([0.0, 0.001, 0.1, 1.0, 5.0])
        >>> raw = inv_softplus_safe(f)
        >>> reconstructed = jax.nn.softplus(raw)
        >>> # reconstructed ≈ f for elements > eps
    """
    input_dtype = f.dtype
    f64 = f.astype(jnp.float64)
    f_clipped = jnp.maximum(f64, eps)
    # For large values, exp(f) overflows; use raw ≈ f (softplus(x) ≈ x for x >> 1)
    raw = jnp.where(f_clipped > 20.0, f_clipped, jnp.log(jnp.expm1(f_clipped)))
    raw = jnp.clip(raw, clip_min, clip_max)
    return raw.astype(input_dtype)
