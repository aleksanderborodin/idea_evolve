# fitness: 1.5249
# Multi-start asymmetric JAX optimization — best of 5 asymmetric seeds
# Try multiple asymmetric initializations (different "chirality") and keep the best.
# Each start breaks the C>=2 symmetry constraint differently.

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax

from helper import compute_c


def run_optimization(f_init, num_steps=40000, lr=0.005):
    params = f_init  # already in logit space (raw, will apply relu)
    N = len(f_init)

    def objective(p):
        f = jax.nn.relu(p)
        return compute_c(f)

    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=lr,
        warmup_steps=2000,
        decay_steps=num_steps - 2000,
        end_value=lr * 1e-4,
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

    return jax.nn.relu(params), float(loss)


def entrypoint() -> np.ndarray:
    N = 800
    x = jnp.linspace(-0.25, 0.25, N, endpoint=False)

    # Generate 5 asymmetric initializations
    inits = []

    # Init 1: ramp up on right half
    f1 = jnp.where(x >= 0, 1.0 + 2.0 * x, 0.1)
    inits.append(f1)

    # Init 2: ramp up on left half (opposite chirality)
    f2 = jnp.where(x <= 0, 1.0 - 2.0 * x, 0.1)
    inits.append(f2)

    # Init 3: Gaussian centered at +0.1
    f3 = jnp.exp(-((x - 0.1) ** 2) / (2 * 0.07 ** 2)) + 0.1
    inits.append(f3)

    # Init 4: Gaussian centered at -0.1
    f4 = jnp.exp(-((x + 0.1) ** 2) / (2 * 0.07 ** 2)) + 0.1
    inits.append(f4)

    # Init 5: Two gaussians, unequal amplitudes (asymmetric)
    f5 = 2.0 * jnp.exp(-((x - 0.08) ** 2) / (2 * 0.05 ** 2)) + \
         0.5 * jnp.exp(-((x + 0.12) ** 2) / (2 * 0.05 ** 2)) + 0.05
    inits.append(f5)

    best_f = None
    best_c = float('inf')

    for i, f_init in enumerate(inits):
        f_opt, c_val = run_optimization(f_init, num_steps=40000, lr=0.005)
        if c_val < best_c:
            best_c = c_val
            best_f = f_opt

    return np.array(best_f)
