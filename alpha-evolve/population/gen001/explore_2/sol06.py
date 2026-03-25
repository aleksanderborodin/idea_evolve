# fitness: 1.5278
# Long asymmetric optimization: 70k total steps with softplus parameterization
# Key insight from sol02/sol03: asymmetric init enables C < 1.6.
# Strategy: best of 3 random asymmetric seeds (35k each), then
# continue best for 35k more = 70k total for winner.
# softplus parameterization ensures smooth positive constraint (better gradients than relu).

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax

from helper import compute_c


def run_phase(params, opt, num_steps):
    opt_state = opt.init(params)

    def objective(p):
        return compute_c(jax.nn.softplus(p))

    @jax.jit
    def train_step(p, opt_st):
        loss, grads = jax.value_and_grad(objective)(p)
        updates, opt_st = opt.update(grads, opt_st, p)
        p = optax.apply_updates(p, updates)
        return p, opt_st, loss

    for _ in range(num_steps):
        params, opt_state, loss = train_step(params, opt_state)
    return params, float(loss)


def entrypoint() -> np.ndarray:
    N = 1000
    x = jnp.linspace(-0.25, 0.25, N, endpoint=False)

    def to_params(f_raw):
        # Inverse softplus: softplus(p) = f_raw => p = log(exp(f_raw) - 1)
        f_clamped = jnp.maximum(f_raw, 1e-3)
        return jnp.log(jnp.exp(f_clamped) - 1.0 + 1e-7)

    # Three asymmetric seeds
    seeds = [
        # Seed A: ramp on right half
        jnp.where(x >= 0, 1.5 + 4.0 * x, 0.1),
        # Seed B: steep ramp on right quarter
        jnp.where(x >= 0.05, 2.0 + 3.0 * (x - 0.05), 0.05),
        # Seed C: two unequal bumps biased right
        1.8 * jnp.exp(-((x - 0.1) ** 2) / (2 * 0.06 ** 2))
        + 0.4 * jnp.exp(-((x + 0.1) ** 2) / (2 * 0.06 ** 2)) + 0.05,
    ]

    PHASE1_STEPS = 35000

    best_params = None
    best_c = float('inf')

    for seed_f in seeds:
        params = to_params(seed_f)
        opt = optax.adam(
            optax.warmup_cosine_decay_schedule(
                init_value=0.0, peak_value=0.008,
                warmup_steps=PHASE1_STEPS // 20,
                decay_steps=PHASE1_STEPS - PHASE1_STEPS // 20,
                end_value=1e-6,
            )
        )
        final_params, c_val = run_phase(params, opt, PHASE1_STEPS)
        if c_val < best_c:
            best_c = c_val
            best_params = final_params

    # Phase 2: continue best for 35k more at lower lr
    PHASE2_STEPS = 35000
    opt2 = optax.adam(
        optax.warmup_cosine_decay_schedule(
            init_value=0.0, peak_value=0.003,
            warmup_steps=PHASE2_STEPS // 20,
            decay_steps=PHASE2_STEPS - PHASE2_STEPS // 20,
            end_value=1e-6,
        )
    )
    best_params, _ = run_phase(best_params, opt2, PHASE2_STEPS)

    return np.array(jax.nn.softplus(best_params))
