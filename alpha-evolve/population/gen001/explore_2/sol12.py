# fitness: 0.0
# Approach: High learning rate + restarts to escape local minima
# Key idea: baseline gets stuck at C~1.518 with LR=0.005.
# Higher LR (0.02) with restarts explores wider basin landscape.
# Cyclic LR schedule: multiple cosine cycles, each resetting.
# N=1000 for quality.

import numpy as np
import jax
import jax.numpy as jnp
import optax
from scipy.optimize import minimize
import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')
from helper import compute_c


def entrypoint() -> np.ndarray:
    N = 1000

    key = jax.random.PRNGKey(42)
    f_values = jnp.zeros((N,))
    f_values = f_values.at[N//4:3*N//4].set(1.0)
    f_values = f_values + 0.05 * jax.random.uniform(key, (N,))

    # Phase 1: Aggressive cosine cycles (3 cycles × 15k steps, LR 0.02→0.001)
    # Each restart gives the optimizer a fresh momentum state from current position
    for cycle in range(3):
        lr_peak = 0.02 / (2 ** cycle)  # 0.02, 0.01, 0.005
        sched = optax.warmup_cosine_decay_schedule(
            init_value=0.0, peak_value=lr_peak,
            warmup_steps=500, decay_steps=14500, end_value=lr_peak * 0.01,
        )
        opt = optax.adam(sched)
        state = opt.init(f_values)

        @jax.jit
        def step(p, st):
            loss, grads = jax.value_and_grad(compute_c)(p)
            updates, st = opt.update(grads, st, p)
            return optax.apply_updates(p, updates), st, loss

        for _ in range(15000):
            f_values, state, _ = step(f_values, state)

    # Phase 2: Fine-tune with small LR (10k steps)
    sched_fine = optax.warmup_cosine_decay_schedule(
        init_value=0.0, peak_value=0.001,
        warmup_steps=200, decay_steps=9800, end_value=1e-7,
    )
    opt_fine = optax.adam(sched_fine)
    state_fine = opt_fine.init(f_values)

    @jax.jit
    def step_fine(p, st):
        loss, grads = jax.value_and_grad(compute_c)(p)
        updates, st = opt_fine.update(grads, st, p)
        return optax.apply_updates(p, updates), st, loss

    for _ in range(10000):
        f_values, state_fine, _ = step_fine(f_values, state_fine)

    warm = np.array(jax.nn.relu(f_values))

    # Phase 3: L-BFGS
    val_and_grad = jax.jit(jax.value_and_grad(compute_c))

    def scipy_obj(x):
        x_jax = jnp.array(x.astype(np.float32))
        val, g = val_and_grad(x_jax)
        return float(val), np.array(g, dtype=np.float64)

    result = minimize(
        scipy_obj,
        warm.astype(np.float64),
        method='L-BFGS-B',
        jac=True,
        bounds=[(0, None)] * N,
        options={'maxiter': 5000, 'ftol': 1e-15, 'gtol': 1e-9}
    )

    return np.maximum(result.x, 0.0).astype(np.float32)
