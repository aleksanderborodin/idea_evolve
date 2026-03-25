# fitness: TBD
# Basin hopping: run 5 rounds of (perturb best → re-optimize), keep global best
# Uses the sol09-style multi-start result as seed, applies medium perturbation between rounds

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


def entrypoint() -> np.ndarray:
    N1 = 600
    N2 = 2000

    # Phase 1: coarse multi-scale to get initial solution
    key = jax.random.PRNGKey(42)
    f = jnp.zeros((N1,))
    si, ei = N1 // 4, 3 * N1 // 4
    f = f.at[si:ei].set(1.0)
    f = f + 0.05 * jax.random.uniform(key, (N1,))
    f = adam_optimize(f, steps=40000, lr=0.005, warmup=2000)

    # Upsample to N2
    x_c = np.linspace(-0.25, 0.25, N1)
    x_f = np.linspace(-0.25, 0.25, N2)
    f = jnp.array(np.interp(x_f, x_c, np.array(f)))
    f = adam_optimize(f, steps=50000, lr=0.002, warmup=2000)
    best_score = float(compute_c(f))
    best_f = f

    # Basin hopping: 5 rounds of perturb + re-optimize
    noise_levels = [0.05, 0.10, 0.05, 0.08, 0.06]
    for i, noise in enumerate(noise_levels):
        key = jax.random.PRNGKey(100 + i)
        # Add medium noise and clip to non-negative
        f_perturbed = jax.nn.relu(best_f + noise * jax.random.normal(key, best_f.shape))
        # Re-optimize for 40k steps
        f_new = adam_optimize(f_perturbed, steps=40000, lr=0.002, warmup=1000)
        score = float(compute_c(f_new))
        if score < best_score:
            best_score = score
            best_f = f_new

    return np.array(best_f)
