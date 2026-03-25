# fitness: 1.811140785998411
# L-BFGS via scipy with JAX gradients, flat block init (like baseline), N=600
# RESULT: L-BFGS converges to worse local minimum (1.81) vs Adam (1.52)
# Lesson: Adam's adaptive noise helps escape bad minima; softplus changes landscape unfavorably

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import scipy.optimize as opt

from helper import compute_c


def entrypoint() -> np.ndarray:
    N = 600

    val_and_grad_fn = jax.jit(jax.value_and_grad(lambda p: compute_c(jax.nn.softplus(p))))

    def objective_and_grad(params_np):
        params = jnp.array(params_np, dtype=jnp.float32)
        val, grad = val_and_grad_fn(params)
        return float(val), np.array(grad, dtype=np.float64)

    key = jax.random.PRNGKey(42)
    f_init = jnp.zeros((N,))
    start_idx, end_idx = N // 4, 3 * N // 4
    f_init = f_init.at[start_idx:end_idx].set(1.0)
    f_init = f_init + 0.05 * jax.random.uniform(key, (N,))
    f_init = jax.nn.relu(f_init)

    f_np = np.array(f_init)
    f_np = np.clip(f_np, 0.001, None)
    params0 = np.log(np.exp(f_np) - 1.0)

    _ = objective_and_grad(params0)

    result = opt.minimize(
        objective_and_grad,
        params0.astype(np.float64),
        method='L-BFGS-B',
        jac=True,
        options={'maxiter': 5000, 'maxfun': 25000, 'ftol': 1e-14, 'gtol': 1e-8}
    )

    params_final = jnp.array(result.x, dtype=jnp.float32)
    f_final = jax.nn.softplus(params_final)

    return np.array(f_final)
