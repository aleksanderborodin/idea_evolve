# fitness: 0.0
# Approach: B-spline basis parameterization, asymmetric initialization
# Smooth parameterization reduces effective dimensionality.
# Fix: correct n_basis = degree+1+n_knots_interior

import numpy as np
import jax
import jax.numpy as jnp
import optax
import sys
from scipy.interpolate import BSpline
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')
from helper import compute_c


def entrypoint() -> np.ndarray:
    N = 600
    degree = 3
    n_knots_interior = 16  # interior knots

    x_np = np.linspace(0.0, 1.0, N)

    # Clamped knot vector: (degree+1) zeros, interior knots, (degree+1) ones
    interior_knots = np.linspace(0.0, 1.0, n_knots_interior + 2)[1:-1]
    knots_np = np.concatenate([
        np.zeros(degree + 1),
        interior_knots,
        np.ones(degree + 1)
    ])

    # n_basis = len(knots) - degree - 1
    n_basis = len(knots_np) - degree - 1
    # = 2*(degree+1) + n_knots_interior - degree - 1 = degree+1+n_knots_interior = 4+16=20

    # Precompute basis matrix (N x n_basis)
    basis_matrix = np.zeros((N, n_basis))
    for j in range(n_basis):
        c = np.zeros(n_basis)
        c[j] = 1.0
        spl = BSpline(knots_np, c, degree)
        basis_matrix[:, j] = np.maximum(spl(x_np), 0.0)

    basis_jax = jnp.array(basis_matrix)  # (N, n_basis)

    def make_f(coeffs):
        return basis_jax @ jax.nn.relu(coeffs)

    def objective(coeffs):
        return compute_c(make_f(coeffs))

    # Initialize: right-biased (mass in right 2/3)
    init_coeffs = jnp.zeros(n_basis)
    right_start = n_basis // 3
    init_coeffs = init_coeffs.at[right_start:].set(1.0)
    key = jax.random.PRNGKey(99)
    init_coeffs = init_coeffs + 0.1 * jax.random.uniform(key, (n_basis,))

    num_steps = 30000
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0, peak_value=0.02,
        warmup_steps=500, decay_steps=num_steps - 500, end_value=1e-6,
    )
    optimizer = optax.adam(schedule)
    params = init_coeffs
    opt_state = optimizer.init(params)

    @jax.jit
    def train_step(p, st):
        loss, grads = jax.value_and_grad(objective)(p)
        updates, st = optimizer.update(grads, st, p)
        p = optax.apply_updates(p, updates)
        return p, st, loss

    for _ in range(num_steps):
        params, opt_state, loss = train_step(params, opt_state)

    return np.array(make_f(params))
