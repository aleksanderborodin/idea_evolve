# fitness: TBD
# Approach: N=1000, Gaussian bump init, softplus reparameterization, 80k steps, 3 restarts
# Improvements over baseline: better init, non-negativity via softplus, more steps, higher resolution

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax
from helper import compute_c


def entrypoint() -> np.ndarray:
    N = 1000
    num_steps = 80000
    warmup_steps = 3000
    base_lr = 0.01

    # Domain grid [-0.25, 0.25]
    x = jnp.linspace(-0.25, 0.25, N)

    # Gaussian bump centered at 0, sigma=0.15 — gives optimizer a head start
    sigma = 0.15
    gaussian_bump = jnp.exp(-x**2 / (2.0 * sigma**2))

    # Softplus-inverse for initialization: softplus(x) = log(1+exp(x)), inverse = log(exp(y)-1) = log(expm1(y))
    # gaussian_bump in range [~0.25, 1.0], all > 0, safe for inv_softplus
    raw_init = jnp.log(jnp.expm1(jnp.clip(gaussian_bump, 1e-4, None)))

    # Objective in raw (unconstrained) space; softplus ensures f > 0 always
    def objective(raw_params):
        f_values = jax.nn.softplus(raw_params)
        return compute_c(f_values)

    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=base_lr,
        warmup_steps=warmup_steps,
        decay_steps=num_steps - warmup_steps,
        end_value=base_lr * 1e-4,
    )
    optimizer = optax.adam(learning_rate=schedule)

    @jax.jit
    def train_step(raw_p, opt_st):
        loss, grads = jax.value_and_grad(objective)(raw_p)
        updates, new_opt_st = optimizer.update(grads, opt_st, raw_p)
        new_raw_p = optax.apply_updates(raw_p, updates)
        return new_raw_p, new_opt_st, loss

    best_c = float('inf')
    best_f = None

    seeds = [42, 123, 7]
    for seed in seeds:
        key = jax.random.PRNGKey(seed)
        noise = 0.02 * jax.random.normal(key, (N,))
        raw_params = raw_init + noise
        opt_state = optimizer.init(raw_params)

        for _ in range(num_steps):
            raw_params, opt_state, loss = train_step(raw_params, opt_state)

        f_final = jax.nn.softplus(raw_params)
        c_val = float(compute_c(f_final))

        if c_val < best_c:
            best_c = c_val
            best_f = f_final

    return np.array(best_f)
