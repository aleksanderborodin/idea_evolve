# fitness: TBD
# Multi-start: run 3 different seeds at N=600 (30k steps), pick best, continue at N=2000 (80k)
# Goal: find better basin of attraction by exploring with multiple random starts

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
        warmup_steps=warmup, decay_steps=steps - warmup,
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


def make_init(N, key, style='flat'):
    if style == 'flat':
        f = jnp.zeros((N,))
        si, ei = N // 4, 3 * N // 4
        f = f.at[si:ei].set(1.0)
        f = f + 0.05 * jax.random.uniform(key, (N,))
    elif style == 'triangle':
        x = jnp.linspace(0.0, 1.0, N)
        f = jnp.where(x < 0.5, 2.0 * x, 2.0 * (1.0 - x))
        f = f + 0.05 * jax.random.uniform(key, (N,))
    elif style == 'random':
        f = jax.random.uniform(key, (N,)) * 0.5 + 0.3
    return f


def entrypoint() -> np.ndarray:
    N1 = 600

    # Run 3 starts at N=600 with 30k steps each
    seeds_and_styles = [
        (42, 'flat'),
        (123, 'flat'),
        (7, 'triangle'),
    ]

    best_f1 = None
    best_score1 = float('inf')
    for seed, style in seeds_and_styles:
        key = jax.random.PRNGKey(seed)
        f_init = make_init(N1, key, style=style)
        f_opt = adam_optimize(f_init, steps=30000, lr=0.005, warmup=2000)
        score = float(compute_c(f_opt))
        if score < best_score1:
            best_score1 = score
            best_f1 = f_opt

    # Upsample best to N=2000, then refine with 80k steps
    N2 = 2000
    x_c = np.linspace(-0.25, 0.25, N1)
    x_f = np.linspace(-0.25, 0.25, N2)
    f2 = jnp.array(np.interp(x_f, x_c, np.array(best_f1)))
    f2 = adam_optimize(f2, steps=80000, lr=0.002, warmup=3000)

    return np.array(f2)
