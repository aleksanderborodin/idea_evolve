# fitness: 1.5176833982700835
# Extended multi-scale: N=600 (50k) → N=2000 (80k), more steps both phases
# Also tries different seeds to find better basin

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax

from helper import compute_c


def run_adam_phase(f_init, steps, lr, warmup, optimizer=None):
    """Run Adam optimization for a given number of steps."""
    if optimizer is None:
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


def entrypoint() -> np.ndarray:
    # Phase 1: coarse at N=600
    N_coarse = 600
    key = jax.random.PRNGKey(42)
    f_coarse = jnp.zeros((N_coarse,))
    si, ei = N_coarse // 4, 3 * N_coarse // 4
    f_coarse = f_coarse.at[si:ei].set(1.0)
    f_coarse = f_coarse + 0.05 * jax.random.uniform(key, (N_coarse,))

    f_coarse = run_adam_phase(f_coarse, steps=50000, lr=0.005, warmup=2000)

    # Phase 2: upsample to N=2000
    N_fine = 2000
    x_c = np.linspace(-0.25, 0.25, N_coarse)
    x_f = np.linspace(-0.25, 0.25, N_fine)
    f_fine = jnp.array(np.interp(x_f, x_c, np.array(f_coarse)))

    f_fine = run_adam_phase(f_fine, steps=80000, lr=0.0015, warmup=3000)

    return np.array(f_fine)
