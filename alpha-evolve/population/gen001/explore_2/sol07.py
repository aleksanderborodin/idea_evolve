# fitness: 1.5801
# Gaussian mixture parameterization — learnable bump positions, widths, and heights
# f(x) = sum_k h_k * exp(-(x - mu_k)^2 / (2*sigma_k^2))
# This allows the optimizer to discover: how many bumps, where to place them, how wide.
# Naturally positive by construction (no relu/softplus needed).
# Key: asymmetric placement (don't restrict mu_k to be symmetric around 0).

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax

from helper import compute_c


def entrypoint() -> np.ndarray:
    N = 1000
    K = 8  # number of Gaussian components
    x = jnp.linspace(-0.25, 0.25, N, endpoint=False)

    def build_f(log_h, mu, log_sigma):
        # heights are exp(log_h) (positive)
        # widths are exp(log_sigma) (positive)
        h = jnp.exp(log_h)       # (K,)
        sigma = jnp.exp(log_sigma)  # (K,)
        # f(x) = sum_k h_k * exp(-(x - mu_k)^2 / (2*sigma_k^2))
        # shape: broadcast (N, K) over x and mus
        diff = x[:, None] - mu[None, :]  # (N, K)
        gaussians = jnp.exp(-0.5 * (diff / sigma[None, :]) ** 2)  # (N, K)
        return (gaussians * h[None, :]).sum(axis=1)  # (N,)

    def objective(params):
        log_h, mu, log_sigma = params
        f = build_f(log_h, mu, log_sigma)
        return compute_c(f)

    # Asymmetric initialization: bumps biased toward right side
    key = jax.random.PRNGKey(7)
    log_h_init = jnp.zeros(K)
    # Positions: somewhat spread, biased slightly right
    mu_init = jnp.array([0.12, 0.08, 0.05, 0.15, -0.05, 0.18, -0.02, 0.1])
    log_sigma_init = jnp.full((K,), jnp.log(0.05))

    params = (log_h_init, mu_init, log_sigma_init)

    num_steps = 80000
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=0.01,
        warmup_steps=4000,
        decay_steps=num_steps - 4000,
        end_value=1e-6,
    )
    optimizer = optax.adam(learning_rate=schedule)
    opt_state = optimizer.init(params)

    @jax.jit
    def train_step(p, opt_st):
        loss, grads = jax.value_and_grad(objective)(p)
        updates, opt_st = optimizer.update(grads, opt_st, p)
        p = optax.apply_updates(p, updates)
        return p, opt_st, loss

    for _ in range(num_steps):
        params, opt_state, loss = train_step(params, opt_state)

    f_final = build_f(*params)
    return np.array(f_final)
