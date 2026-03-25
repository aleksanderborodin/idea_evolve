# fitness: 1.5729
# Asymmetric box initialization + JAX gradient descent
# Key insight: symmetric f forces (f*f)(0) = ||f||_2^2 >= 2(integral f)^2, so C >= 2.
# Breaking symmetry allows (f*f)(0) to be small while the max shifts to some t != 0,
# potentially achieving C < 2 and approaching the target 1.5053.
# Start with mass concentrated on [0, 1/4] (right half only) instead of the centered box.

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax

from helper import compute_c


def entrypoint() -> np.ndarray:
    N = 800
    learning_rate = 0.005
    num_steps = 50000
    warmup_steps = 2000

    # Asymmetric initialization: box on right half [0, 1/4]
    # This starts the optimizer in the asymmetric regime where C < 2 is accessible
    x = jnp.linspace(-0.25, 0.25, N, endpoint=False)
    # Ramp that peaks near x = 1/8
    f_init = jnp.where(x >= 0.0, 1.0 + x * 4.0, 0.01)  # linear ramp on right side, small value on left
    f_init = jax.nn.softplus(f_init - 0.5)  # smooth to positive values

    def objective(params):
        f = jax.nn.softplus(params)
        return compute_c(f)

    params = jnp.log(jnp.exp(f_init) - 1.0 + 1e-6)  # inverse softplus

    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=learning_rate,
        warmup_steps=warmup_steps,
        decay_steps=num_steps - warmup_steps,
        end_value=learning_rate * 1e-4,
    )
    optimizer = optax.adam(learning_rate=schedule)
    opt_state = optimizer.init(params)

    @jax.jit
    def train_step(p, opt_st):
        loss, grads = jax.value_and_grad(objective)(p)
        updates, opt_st = optimizer.update(grads, opt_st, p)
        p = optax.apply_updates(p, updates)
        return p, opt_st, loss

    for step in range(num_steps):
        params, opt_state, loss = train_step(params, opt_state)

    f_final = jax.nn.softplus(params)
    return np.array(f_final)
