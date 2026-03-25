# fitness: 1.6904386774312101
# L-BFGS via scipy with JAX gradients, softplus parameterization, N=1000, Gaussian init

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import scipy.optimize as opt

from helper import compute_c


def entrypoint() -> np.ndarray:
    N = 1000

    # Build a differentiable objective using softplus to ensure non-negativity
    @jax.jit
    def objective_jax(params):
        f_values = jax.nn.softplus(params)
        return compute_c(f_values)

    val_and_grad_fn = jax.jit(jax.value_and_grad(objective_jax))

    def objective_and_grad(params_np):
        params = jnp.array(params_np, dtype=jnp.float32)
        val, grad = val_and_grad_fn(params)
        return float(val), np.array(grad, dtype=np.float64)

    # Initialize with a Gaussian centered at 0 (middle of [-1/4, 1/4])
    x = np.linspace(-0.25, 0.25, N)
    sigma = 0.08
    gaussian = np.exp(-x**2 / (2 * sigma**2))
    gaussian_clipped = np.clip(gaussian, 0.001, None)
    params0 = np.log(np.exp(gaussian_clipped) - 1.0)  # softplus_inv

    # Warm up JAX compilation
    _ = objective_and_grad(params0)

    # Run L-BFGS-B
    result = opt.minimize(
        objective_and_grad,
        params0.astype(np.float64),
        method='L-BFGS-B',
        jac=True,
        options={
            'maxiter': 3000,
            'maxfun': 15000,
            'ftol': 1e-12,
            'gtol': 1e-7,
        }
    )

    params_final = jnp.array(result.x, dtype=jnp.float32)
    f_final = jax.nn.softplus(params_final)

    return np.array(f_final)
