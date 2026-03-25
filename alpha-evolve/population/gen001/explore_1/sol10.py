# fitness: TBD
# Multi-scale Adam to N=2000 (like sol04) then L-BFGS polish from warm start
# L-BFGS can find sharper optima once Adam has found the right basin

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import scipy.optimize as opt
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


def lbfgs_polish(f_start):
    """L-BFGS polish using unconstrained params (compute_c applies relu internally)."""
    val_and_grad_fn = jax.jit(jax.value_and_grad(compute_c))

    def objective(params_np):
        params = jnp.array(params_np, dtype=jnp.float32)
        val, grad = val_and_grad_fn(params)
        return float(val), np.array(grad, dtype=np.float64)

    # Warm up JIT
    _ = objective(np.array(f_start))

    result = opt.minimize(
        objective,
        np.array(f_start, dtype=np.float64),
        method='L-BFGS-B',
        jac=True,
        bounds=[(0.0, None)] * len(f_start),  # non-negativity constraint
        options={'maxiter': 5000, 'maxfun': 30000, 'ftol': 1e-14, 'gtol': 1e-8},
    )
    return jnp.array(result.x, dtype=jnp.float32)


def entrypoint() -> np.ndarray:
    # Phase 1: coarse at N=600, 40k steps
    N1 = 600
    key = jax.random.PRNGKey(42)
    f1 = jnp.zeros((N1,))
    si, ei = N1 // 4, 3 * N1 // 4
    f1 = f1.at[si:ei].set(1.0)
    f1 = f1 + 0.05 * jax.random.uniform(key, (N1,))
    f1 = adam_phase(f1, steps=40000, lr=0.005, warmup=2000)

    # Phase 2: upsample to N=2000, 50k steps
    N2 = 2000
    x_c = np.linspace(-0.25, 0.25, N1)
    x_f = np.linspace(-0.25, 0.25, N2)
    f2 = jnp.array(np.interp(x_f, x_c, np.array(f1)))
    f2 = adam_phase(f2, steps=50000, lr=0.002, warmup=2000)

    # Phase 3: L-BFGS polish with bound constraints (non-negative)
    f3 = lbfgs_polish(f2)

    return np.array(f3)
