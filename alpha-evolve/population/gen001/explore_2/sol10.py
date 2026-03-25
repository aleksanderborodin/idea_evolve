# fitness: 0.0
# Approach: Regularization-guided annealing to escape local minima
# Phase 1: Optimize C + lambda*TV(f) (smoothness penalty) for 20k steps
# Phase 2: Decay lambda to 0 over 20k steps (annealing)
# Phase 3: L-BFGS refinement of pure C(f)
# The TV penalty reshapes the loss landscape during early phases.
# N=800 for speed.

import numpy as np
import jax
import jax.numpy as jnp
import optax
from scipy.optimize import minimize
import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')
from helper import compute_c


def entrypoint() -> np.ndarray:
    N = 800

    def compute_tv(f):
        """Total variation regularizer."""
        f_pos = jax.nn.relu(f)
        diffs = f_pos[1:] - f_pos[:-1]
        return jnp.sum(jnp.abs(diffs)) * (0.5 / N)

    def regularized_obj(f, lam):
        return compute_c(f) + lam * compute_tv(f) * 10.0

    key = jax.random.PRNGKey(42)
    f_values = jnp.zeros((N,))
    f_values = f_values.at[N//4:3*N//4].set(1.0)
    f_values = f_values + 0.05 * jax.random.uniform(key, (N,))

    # Phase 1: high regularization (20k steps, lam=0.5)
    sched1 = optax.warmup_cosine_decay_schedule(
        init_value=0.0, peak_value=0.005,
        warmup_steps=1000, decay_steps=19000, end_value=0.001,
    )
    opt1 = optax.adam(sched1)
    opt_state = opt1.init(f_values)

    @jax.jit
    def step_reg(p, st, lam):
        loss, grads = jax.value_and_grad(regularized_obj)(p, lam)
        updates, st = opt1.update(grads, st, p)
        p = optax.apply_updates(p, updates)
        return p, st, loss

    lam = 0.5
    for i in range(20000):
        f_values, opt_state, _ = step_reg(f_values, opt_state, lam)

    # Phase 2: anneal lambda from 0.5 to 0 over 20k steps
    sched2 = optax.warmup_cosine_decay_schedule(
        init_value=0.001, peak_value=0.005,
        warmup_steps=500, decay_steps=19500, end_value=5e-8,
    )
    opt2 = optax.adam(sched2)
    opt_state2 = opt2.init(f_values)

    @jax.jit
    def step_anneal(p, st, lam):
        loss, grads = jax.value_and_grad(regularized_obj)(p, lam)
        updates, st = opt2.update(grads, st, p)
        p = optax.apply_updates(p, updates)
        return p, st, loss

    for i in range(20000):
        lam = 0.5 * (1 - i / 20000)
        f_values, opt_state2, _ = step_anneal(f_values, opt_state2, lam)

    # Phase 3: pure C optimization (20k Adam steps)
    sched3 = optax.warmup_cosine_decay_schedule(
        init_value=0.0, peak_value=0.002,
        warmup_steps=500, decay_steps=19500, end_value=5e-9,
    )
    opt3 = optax.adam(sched3)
    opt_state3 = opt3.init(f_values)

    @jax.jit
    def step_pure(p, st):
        loss, grads = jax.value_and_grad(compute_c)(p)
        updates, st = opt3.update(grads, st, p)
        p = optax.apply_updates(p, updates)
        return p, st, loss

    for _ in range(20000):
        f_values, opt_state3, _ = step_pure(f_values, opt_state3)

    warm = np.array(jax.nn.relu(f_values))

    # Phase 4: L-BFGS
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
