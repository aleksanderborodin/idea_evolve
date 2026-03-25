# fitness: TBD
"""
Multi-restart gradient descent with symmetry enforcement and inline relu projection.
Improvements over baseline:
- Resolution N=1000 (vs 600)
- 80k steps (vs 40k)
- Lower peak LR 0.002 (vs 0.005)
- Relu projection after each step (keeps optimizer in feasible region throughout)
- Symmetry enforcement: f[i] = f[N-1-i] (optimal function should be symmetric)
- 3 restarts with different initializations, keep best result
"""
import jax
import jax.numpy as jnp
import numpy as np
import optax

from helper import compute_c


def entrypoint() -> np.ndarray:
    N = 1000
    num_steps = 80000
    warmup_steps = 3000
    peak_lr = 0.002

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
        # Project to non-negative feasible region after each step
        f_vals = jax.nn.relu(f_vals)
        # Enforce symmetry f(x) = f(-x) — optimal function should be symmetric
        f_vals = (f_vals + f_vals[::-1]) / 2.0
        return f_vals, new_opt_st, loss

    best_c = float('inf')
    best_f = None

    # Three restarts with different initializations
    restart_configs = [
        # (seed, init_type)
        (42, 'block'),       # Block in center (like baseline)
        (123, 'triangle'),   # Triangular / tent function (symmetric)
        (777, 'gaussian'),   # Gaussian bump (symmetric)
    ]

    for seed, init_type in restart_configs:
        key = jax.random.PRNGKey(seed)
        noise = 0.05 * jax.random.uniform(key, (N,))
        x = jnp.linspace(-0.25, 0.25, N)

        if init_type == 'block':
            f_init = jnp.zeros((N,))
            s, e = N // 4, 3 * N // 4
            f_init = f_init.at[s:e].set(1.0)
            f_init = f_init + noise
        elif init_type == 'triangle':
            # Tent function centered at 0
            f_init = jnp.maximum(0.0, 1.0 - 4.0 * jnp.abs(x))
            f_init = f_init + noise
        else:  # gaussian
            # Gaussian centered at 0
            f_init = jnp.exp(-50.0 * x ** 2)
            f_init = f_init + noise

        # Start in feasible (non-negative) region and enforce symmetry
        f_values = jax.nn.relu(f_init)
        f_values = (f_values + f_values[::-1]) / 2.0

        opt_state = optimizer.init(f_values)

        for _ in range(num_steps):
            f_values, opt_state, _ = train_step(f_values, opt_state)

        final_c = float(compute_c(f_values))

        if final_c < best_c:
            best_c = final_c
            best_f = np.array(f_values)

    return best_f
