# fitness: TBD
# Normalized optimization: project to unit L1 norm after each step (removes scale degeneracy)
# Plus multi-scale N=600 -> N=4000, high step counts

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax

from helper import compute_c


def normalized_adam_phase(f_init, steps, lr, warmup):
    """Adam with L1 normalization after each step to remove scale degeneracy."""
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0, peak_value=lr,
        warmup_steps=warmup, decay_steps=max(steps - warmup, 1),
        end_value=lr * 1e-4,
    )
    optimizer = optax.adam(learning_rate=schedule)
    # Normalize init
    dx = 0.5 / len(f_init)
    integral = jnp.sum(jax.nn.relu(f_init)) * dx
    f = f_init / jnp.maximum(integral, 1e-9)
    opt_state = optimizer.init(f)

    @jax.jit
    def step_fn(f, s):
        loss, g = jax.value_and_grad(compute_c)(f)
        upd, s = optimizer.update(g, s, f)
        f_new = optax.apply_updates(f, upd)
        # Clip and renormalize
        f_new = jax.nn.relu(f_new)
        N = len(f_new)
        dx = 0.5 / N
        integral = jnp.sum(f_new) * dx
        f_new = f_new / jnp.maximum(integral, 1e-9)
        return f_new, s, loss

    for _ in range(steps):
        f, opt_state, _ = step_fn(f, opt_state)
    return f  # already normalized and non-negative


def upsample(f, N_new):
    N_old = len(f)
    x_old = np.linspace(-0.25, 0.25, N_old)
    x_new = np.linspace(-0.25, 0.25, N_new)
    return jnp.array(np.interp(x_new, x_old, np.array(f)))


def entrypoint() -> np.ndarray:
    # Phase 1: N=600, 50k steps
    N1 = 600
    key = jax.random.PRNGKey(42)
    f = jnp.zeros((N1,))
    si, ei = N1 // 4, 3 * N1 // 4
    f = f.at[si:ei].set(1.0)
    f = f + 0.05 * jax.random.uniform(key, (N1,))
    f = normalized_adam_phase(f, steps=50000, lr=0.005, warmup=2000)

    # Phase 2: N=2000, 80k steps
    f = upsample(f, 2000)
    f = normalized_adam_phase(f, steps=80000, lr=0.002, warmup=3000)

    # Phase 3: N=4000, 50k steps
    f = upsample(f, 4000)
    f = normalized_adam_phase(f, steps=50000, lr=0.0008, warmup=2000)

    return np.array(f)
