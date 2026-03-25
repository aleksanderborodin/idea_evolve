# fitness: TBD
# Multi-start with diverse initializations: flat-block variants, narrow, wide, two-bump
# 5 starts at N=600 (25k steps each) → pick best → refine at N=2000 (100k steps)

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax

from helper import compute_c


def adam_optimize(f_init, steps, lr, warmup):
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0, peak_value=lr,
        warmup_steps=warmup, decay_steps=max(steps - warmup, 1),
        end_value=lr * 1e-4,
    )
    optimizer = optax.adam(learning_rate=schedule)
    opt_state = optimizer.init(f_init)
    f = f_init

    @jax.jit
    def step_fn(f, s):
        loss, g = jax.value_and_grad(compute_c)(f)
        upd, s = optimizer.update(g, s, f)
        return optax.apply_updates(f, upd), s, loss

    for _ in range(steps):
        f, opt_state, _ = step_fn(f, opt_state)
    return jax.nn.relu(f)


def make_inits(N):
    """Generate diverse initializations."""
    inits = []

    # 1. Standard flat block (baseline-style)
    key = jax.random.PRNGKey(42)
    f = jnp.zeros((N,))
    si, ei = N // 4, 3 * N // 4
    f = f.at[si:ei].set(1.0)
    f = f + 0.05 * jax.random.uniform(key, (N,))
    inits.append(f)

    # 2. Narrow block (middle third only)
    key = jax.random.PRNGKey(7)
    f = jnp.zeros((N,))
    si, ei = N * 5 // 12, N * 7 // 12
    f = f.at[si:ei].set(1.0)
    f = f + 0.05 * jax.random.uniform(key, (N,))
    inits.append(f)

    # 3. Wide block (full interval)
    key = jax.random.PRNGKey(99)
    f = jnp.ones((N,))
    f = f + 0.05 * jax.random.uniform(key, (N,))
    inits.append(f)

    # 4. Two bumps separated
    key = jax.random.PRNGKey(13)
    x = jnp.linspace(-0.25, 0.25, N)
    f = jnp.exp(-((x + 0.1)**2) / (2 * 0.06**2)) + jnp.exp(-((x - 0.1)**2) / (2 * 0.06**2))
    f = f + 0.05 * jax.random.uniform(key, (N,))
    inits.append(f)

    # 5. Triangular peak at center
    key = jax.random.PRNGKey(55)
    x = jnp.linspace(-0.25, 0.25, N)
    f = jnp.maximum(0.0, 1.0 - jnp.abs(x) / 0.15)
    f = f + 0.05 * jax.random.uniform(key, (N,))
    inits.append(f)

    return inits


def entrypoint() -> np.ndarray:
    N1 = 600
    inits = make_inits(N1)

    # Phase 1: run each init for 25k steps
    best_f1 = None
    best_score1 = float('inf')
    for f_init in inits:
        f_opt = adam_optimize(f_init, steps=25000, lr=0.005, warmup=1500)
        score = float(compute_c(f_opt))
        if score < best_score1:
            best_score1 = score
            best_f1 = f_opt

    # Phase 2: upsample to N=2000, refine for 100k steps
    N2 = 2000
    x_c = np.linspace(-0.25, 0.25, N1)
    x_f = np.linspace(-0.25, 0.25, N2)
    f2 = jnp.array(np.interp(x_f, x_c, np.array(best_f1)))
    f2 = adam_optimize(f2, steps=100000, lr=0.002, warmup=3000)

    return np.array(f2)
