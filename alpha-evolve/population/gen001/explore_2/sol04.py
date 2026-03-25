# fitness: 1.5294
# Fourier-basis parameterization + JAX optimization
# Represent f(x) = sum_k c_k * phi_k(x) where phi_k are Fourier basis functions.
# Non-negativity enforced via relu at evaluation time.
# The autoconvolution in Fourier space is squaring the transform — this gives
# a structured parameterization that may navigate the optimization landscape differently.
# Use BOTH cosine and sine modes to allow asymmetric functions.

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax

from helper import compute_c


def entrypoint() -> np.ndarray:
    N = 1000        # output resolution
    K = 30          # number of Fourier modes (0..K-1)
    num_steps = 60000
    lr = 0.01

    x = jnp.linspace(-0.25, 0.25, N, endpoint=False)
    # Fourier basis on [-1/4, 1/4]: frequencies k/(0.5) = 2k Hz
    # phi_0 = 1 (DC)
    # phi_k = cos(2pi * 2k * x) for k=1..K (even/cosine modes)
    # psi_k = sin(2pi * 2k * x) for k=1..K (odd/sine modes — these break symmetry)

    def build_basis():
        """Returns basis matrix of shape (2K+1, N)"""
        basis = [jnp.ones(N) / jnp.sqrt(float(N))]  # DC mode
        for k in range(1, K + 1):
            freq = 2.0 * k * 2.0 * jnp.pi * x  # 2pi * freq * x where freq = 2k
            basis.append(jnp.cos(freq) * jnp.sqrt(2.0 / N))
            basis.append(jnp.sin(freq) * jnp.sqrt(2.0 / N))
        return jnp.stack(basis, axis=0)  # shape (2K+1, N)

    basis = build_basis()  # (2K+1, N)
    n_basis = 2 * K + 1

    def reconstruct(coeffs):
        """Reconstruct non-negative f from Fourier coefficients."""
        f_raw = coeffs @ basis  # (N,)
        return jax.nn.relu(f_raw)

    def objective(coeffs):
        f = reconstruct(coeffs)
        return compute_c(f)

    # Initialize with asymmetric shape: DC + slight asymmetry via sine modes
    key = jax.random.PRNGKey(42)
    # Start with mostly DC (flat), with small random perturbation
    coeffs_init = jnp.zeros(n_basis)
    coeffs_init = coeffs_init.at[0].set(10.0)  # large DC component
    # Add small sine mode to break symmetry
    coeffs_init = coeffs_init.at[2].set(2.0)   # first sine mode (asymmetric)
    coeffs_init = coeffs_init + 0.1 * jax.random.normal(key, (n_basis,))

    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=lr,
        warmup_steps=3000,
        decay_steps=num_steps - 3000,
        end_value=lr * 1e-4,
    )
    optimizer = optax.adam(learning_rate=schedule)
    opt_state = optimizer.init(coeffs_init)
    params = coeffs_init

    @jax.jit
    def train_step(p, opt_st):
        loss, grads = jax.value_and_grad(objective)(p)
        updates, opt_st = optimizer.update(grads, opt_st, p)
        p = optax.apply_updates(p, updates)
        return p, opt_st, loss

    for step in range(num_steps):
        params, opt_state, loss = train_step(params, opt_state)

    f_final = reconstruct(params)
    return np.array(f_final)
