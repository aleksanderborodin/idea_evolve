# fitness: TBD
# Approach: scipy L-BFGS-B with bounds [0, inf], JAX gradients, N=800
# L-BFGS-B is much more efficient than Adam for smooth bound-constrained problems.
# Use JAX for autodiff, scipy for optimizer.

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import scipy.optimize
from helper import compute_c


def entrypoint() -> np.ndarray:
    N = 800

    x_np = np.linspace(-0.25, 0.25, N)

    # JAX objective and gradient
    def obj_and_grad(f_np):
        f_jax = jnp.array(f_np, dtype=jnp.float32)
        val, grad = jax.value_and_grad(compute_c)(f_jax)
        return float(val), np.array(grad, dtype=np.float64)

    # Try multiple initializations and keep the best
    best_c = float('inf')
    best_f = None

    inits = {
        'gaussian_narrow': np.exp(-x_np**2 / (2 * 0.10**2)),
        'gaussian_wide': np.exp(-x_np**2 / (2 * 0.15**2)),
        'flat_window': np.where(np.abs(x_np) <= 0.125, 1.0, 0.01),
        'raised_cosine': np.maximum(0, np.cos(np.pi * x_np / 0.5)),
        'triangle': np.maximum(0, 1.0 - np.abs(x_np) / 0.25),
    }

    bounds = [(0.0, None)] * N  # non-negativity constraint

    for name, f0 in inits.items():
        f0 = f0.astype(np.float64)
        result = scipy.optimize.minimize(
            fun=obj_and_grad,
            x0=f0,
            method='L-BFGS-B',
            jac=True,
            bounds=bounds,
            options={'maxiter': 5000, 'ftol': 1e-15, 'gtol': 1e-9},
        )
        f_final = np.maximum(result.x, 0.0)
        c_val = float(result.fun)
        if c_val < best_c:
            best_c = c_val
            best_f = f_final

    return best_f
