# fitness: 1.517821855005561
# Multi-scale: Adam at N=600 (flat block, 40k steps) → upsample → Adam at N=2000 (50k steps)
# Beats baseline 1.5185 with coarse-to-fine strategy

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax

from helper import compute_c


def entrypoint() -> np.ndarray:
    # ---- Phase 1: coarse optimization at N=600 ----
    N_coarse = 600
    steps_coarse = 40000
    lr_coarse = 0.005
    warmup_coarse = 2000

    schedule_c = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=lr_coarse,
        warmup_steps=warmup_coarse,
        decay_steps=steps_coarse - warmup_coarse,
        end_value=lr_coarse * 1e-4,
    )
    optimizer_c = optax.adam(learning_rate=schedule_c)

    key = jax.random.PRNGKey(42)
    f_coarse = jnp.zeros((N_coarse,))
    si, ei = N_coarse // 4, 3 * N_coarse // 4
    f_coarse = f_coarse.at[si:ei].set(1.0)
    f_coarse = f_coarse + 0.05 * jax.random.uniform(key, (N_coarse,))

    opt_state_c = optimizer_c.init(f_coarse)

    @jax.jit
    def train_step_c(f, s):
        loss, g = jax.value_and_grad(compute_c)(f)
        upd, s = optimizer_c.update(g, s, f)
        f = optax.apply_updates(f, upd)
        return f, s, loss

    for _ in range(steps_coarse):
        f_coarse, opt_state_c, _ = train_step_c(f_coarse, opt_state_c)

    f_coarse = jax.nn.relu(f_coarse)

    # ---- Upsample to N=2000 via linear interpolation ----
    N_fine = 2000
    x_coarse = np.linspace(-0.25, 0.25, N_coarse)
    x_fine = np.linspace(-0.25, 0.25, N_fine)
    f_fine_np = np.interp(x_fine, x_coarse, np.array(f_coarse))
    f_fine = jnp.array(f_fine_np)

    # ---- Phase 2: fine optimization at N=2000 ----
    steps_fine = 50000
    lr_fine = 0.002
    warmup_fine = 2000

    schedule_f = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=lr_fine,
        warmup_steps=warmup_fine,
        decay_steps=steps_fine - warmup_fine,
        end_value=lr_fine * 1e-4,
    )
    optimizer_f = optax.adam(learning_rate=schedule_f)
    opt_state_f = optimizer_f.init(f_fine)

    @jax.jit
    def train_step_f(f, s):
        loss, g = jax.value_and_grad(compute_c)(f)
        upd, s = optimizer_f.update(g, s, f)
        f = optax.apply_updates(f, upd)
        return f, s, loss

    for _ in range(steps_fine):
        f_fine, opt_state_f, _ = train_step_f(f_fine, opt_state_f)

    return np.array(jax.nn.relu(f_fine))
