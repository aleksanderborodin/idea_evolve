# fitness: 1.5176334625524102
# Three-phase multi-scale: N=600 (40k) → N=2000 (60k) → N=4000 (40k)
# AdamW with weight decay at each phase, multiple restarts pick best

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax

from helper import compute_c


def adam_phase(f_init, steps, lr, warmup):
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


def upsample(f, N_new):
    N_old = len(f)
    x_old = np.linspace(-0.25, 0.25, N_old)
    x_new = np.linspace(-0.25, 0.25, N_new)
    return jnp.array(np.interp(x_new, x_old, np.array(f)))


def entrypoint() -> np.ndarray:
    # Phase 1: coarse at N=600, 40k steps
    N1 = 600
    key = jax.random.PRNGKey(42)
    f1 = jnp.zeros((N1,))
    si, ei = N1 // 4, 3 * N1 // 4
    f1 = f1.at[si:ei].set(1.0)
    f1 = f1 + 0.05 * jax.random.uniform(key, (N1,))
    f1 = adam_phase(f1, steps=40000, lr=0.005, warmup=2000)

    # Phase 2: upsample to N=2000, 60k steps
    N2 = 2000
    f2 = upsample(f1, N2)
    f2 = adam_phase(f2, steps=60000, lr=0.002, warmup=2000)

    # Phase 3: upsample to N=4000, 40k steps (fine-grained refinement)
    N3 = 4000
    f3 = upsample(f2, N3)
    f3 = adam_phase(f3, steps=40000, lr=0.0008, warmup=2000)

    return np.array(f3)
