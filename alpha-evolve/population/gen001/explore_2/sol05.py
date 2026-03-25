# fitness: 1.5730
# Multi-scale coarse-to-fine optimization
# Phase 1: optimize at N=100 (fast, finds good general shape, 30k steps)
# Phase 2: upsample to N=600, refine (20k steps)
# Phase 3: upsample to N=1200, fine-tune (15k steps)
# Asymmetric initialization at each scale.
# The coarse stage explores the landscape cheaply; fine stage polishes.

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax
from scipy import interpolate

from helper import compute_c


def optimize_at_resolution(f_init, num_steps, lr_peak):
    params = f_init

    def objective(p):
        return compute_c(jax.nn.relu(p))

    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=lr_peak,
        warmup_steps=max(100, num_steps // 20),
        decay_steps=num_steps - max(100, num_steps // 20),
        end_value=lr_peak * 1e-4,
    )
    optimizer = optax.adam(learning_rate=schedule)
    opt_state = optimizer.init(params)

    @jax.jit
    def train_step(p, opt_st):
        loss, grads = jax.value_and_grad(objective)(p)
        updates, opt_st = optimizer.update(grads, opt_st, p)
        p = optax.apply_updates(p, updates)
        return p, opt_st, loss

    for _ in range(num_steps):
        params, opt_state, loss = train_step(params, opt_state)

    return jax.nn.relu(params)


def upsample(f_coarse, N_fine):
    """Upsample using cubic interpolation."""
    N_coarse = len(f_coarse)
    x_coarse = np.linspace(-0.25, 0.25, N_coarse, endpoint=False)
    x_fine = np.linspace(-0.25, 0.25, N_fine, endpoint=False)
    # Cubic interpolation
    f_np = np.array(f_coarse)
    interp = interpolate.CubicSpline(x_coarse, f_np, extrapolate=True)
    f_fine = interp(x_fine)
    f_fine = np.maximum(f_fine, 0.0)  # ensure non-negative
    return jnp.array(f_fine)


def entrypoint() -> np.ndarray:
    # Phase 1: N=100, asymmetric init, 30k steps
    N1 = 100
    x1 = jnp.linspace(-0.25, 0.25, N1, endpoint=False)
    # Asymmetric: ramp concentrated on right half
    f_init1 = jnp.where(x1 >= 0, 1.0 + 3.0 * x1, 0.05)

    f_coarse = optimize_at_resolution(f_init1, num_steps=30000, lr_peak=0.01)

    # Phase 2: upsample to N=600, refine 20k steps
    N2 = 600
    f_medium_init = upsample(f_coarse, N2)
    f_medium = optimize_at_resolution(f_medium_init, num_steps=20000, lr_peak=0.003)

    # Phase 3: upsample to N=1200, fine-tune 15k steps
    N3 = 1200
    f_fine_init = upsample(f_medium, N3)
    f_fine = optimize_at_resolution(f_fine_init, num_steps=15000, lr_peak=0.001)

    return np.array(f_fine)
