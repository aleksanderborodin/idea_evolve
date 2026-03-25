# fitness: TBD
"""
Multi-restart gradient descent with higher resolution and more steps.
Key fix: relu applied only at END (like baseline) — allows negative values during
optimization so gradient can freely shape the function without constraint interference.

Improvements over baseline:
- N=1200 (vs 600)
- 80k steps (vs 40k)
- 3 restarts with different initializations, keep best
- Same LR schedule (peak 0.005) as baseline
"""
import jax
import jax.numpy as jnp
import numpy as np
import optax

from helper import compute_c


def entrypoint() -> np.ndarray:
    N = 1200
    num_steps = 80000
    warmup_steps = 2000
    peak_lr = 0.005

    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=peak_lr,
        warmup_steps=warmup_steps,
        decay_steps=num_steps - warmup_steps,
        end_value=peak_lr * 1e-4,
    )
    optimizer = optax.adam(learning_rate=schedule)

    @jax.jit
    def train_step(f_vals, opt_st):
        loss, grads = jax.value_and_grad(compute_c)(f_vals)
        updates, new_opt_st = optimizer.update(grads, opt_st, f_vals)
        f_vals = optax.apply_updates(f_vals, updates)
        # No projection during training — allow negative values so the optimizer
        # can freely explore (compute_c clips internally via relu)
        return f_vals, new_opt_st, loss

    best_c = float('inf')
    best_f = None

    # Three restarts: block center (baseline-like), wide block, tent function
    seeds = [42, 1234, 9999]
    x = jnp.linspace(-0.25, 0.25, N)

    for i, seed in enumerate(seeds):
        key = jax.random.PRNGKey(seed)
        noise = 0.05 * jax.random.uniform(key, (N,))

        if i == 0:
            # Baseline-like: block in center half of domain
            f_init = jnp.zeros((N,))
            s, e = N // 4, 3 * N // 4
            f_init = f_init.at[s:e].set(1.0)
            f_init = f_init + noise
        elif i == 1:
            # Block covering 60% of domain
            f_init = jnp.zeros((N,))
            s, e = int(N * 0.20), int(N * 0.80)
            f_init = f_init.at[s:e].set(1.0)
            f_init = f_init + noise
        else:
            # Tent function (triangular, symmetric)
            f_init = jnp.maximum(0.0, 1.0 - 4.0 * jnp.abs(x))
            f_init = f_init + noise

        opt_state = optimizer.init(f_init)
        f_values = f_init

        for _ in range(num_steps):
            f_values, opt_state, _ = train_step(f_values, opt_state)

        f_final = jax.nn.relu(f_values)
        final_c = float(compute_c(f_final))

        if final_c < best_c:
            best_c = final_c
            best_f = np.array(f_final)

    return best_f
