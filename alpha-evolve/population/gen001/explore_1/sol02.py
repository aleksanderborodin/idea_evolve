# fitness: 1.526966637203846
# Multi-scale optimization: N=200 -> N=600 -> N=1200
# Strategy: Coarse optimization first to find global shape, then upsample and refine
# Rationale: Avoids local minima at high resolution; coarse pass finds correct basin

import jax
import jax.numpy as jnp
import numpy as np
import optax
import scipy.interpolate

from helper import compute_c


def optimize_at_resolution(f_init, num_steps, lr_peak, warmup_frac=0.1):
    warmup_steps = int(num_steps * warmup_frac)
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=lr_peak,
        warmup_steps=warmup_steps,
        decay_steps=num_steps - warmup_steps,
        end_value=lr_peak * 1e-5,
    )
    optimizer = optax.adam(learning_rate=schedule)
    f_values = jnp.array(f_init)
    opt_state = optimizer.init(f_values)

    @jax.jit
    def train_step(f_vals, opt_st):
        loss, grads = jax.value_and_grad(compute_c)(f_vals)
        updates, opt_st = optimizer.update(grads, opt_st, f_vals)
        f_vals = optax.apply_updates(f_vals, updates)
        return f_vals, opt_st, loss

    for step in range(num_steps):
        f_values, opt_state, loss = train_step(f_values, opt_state)

    return np.array(jax.nn.relu(f_values))


def upsample(f_arr, new_n):
    """Upsample 1D array from len(f_arr) to new_n using cubic interpolation."""
    old_n = len(f_arr)
    xs_old = np.linspace(-0.25, 0.25, old_n)
    xs_new = np.linspace(-0.25, 0.25, new_n)
    interp = scipy.interpolate.interp1d(xs_old, f_arr, kind='cubic', fill_value='extrapolate')
    result = interp(xs_new)
    return np.maximum(result, 0.0)  # maintain non-negativity


def entrypoint() -> np.ndarray:
    key = jax.random.PRNGKey(42)

    # Stage 1: N=200, 25k steps — find general shape
    N1 = 200
    xs = np.linspace(-0.25, 0.25, N1)
    # Raised cosine init (Hann window) — smooth, concentrated at center
    f1_init = 0.5 + 0.5 * np.cos(4 * np.pi * xs)
    f1_init = np.maximum(f1_init, 0.0)
    f1 = optimize_at_resolution(f1_init, num_steps=25000, lr_peak=0.01)

    # Stage 2: N=600, 30k steps — intermediate refinement
    N2 = 600
    f2_init = upsample(f1, N2)
    f2 = optimize_at_resolution(f2_init, num_steps=30000, lr_peak=0.005)

    # Stage 3: N=1200, 25k steps — fine resolution refinement
    N3 = 1200
    f3_init = upsample(f2, N3)
    f3 = optimize_at_resolution(f3_init, num_steps=25000, lr_peak=0.002)

    return f3
