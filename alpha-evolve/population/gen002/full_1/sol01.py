# fitness: TBD
# Strategy: Coarse-to-fine (N=50->N=200->N=600) + smooth-max annealing at all stages
#            + 16 restarts at coarse stage + L-BFGS-B polish + softplus reparam
# Rationale: Coarse grid finds the right basin; fine grid refines; L-BFGS polishes.
#            Smooth-max at every stage provides dense gradient signal.

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax
import scipy.optimize
from helper import compute_c

jax.config.update("jax_enable_x64", True)


def smooth_c(raw_params, temp, dx):
    """Smooth-max version of compute_c using softplus reparameterization."""
    f = jax.nn.softplus(raw_params)
    N = len(f)
    integral_f = jnp.sum(f) * dx
    integral_f_sq = jnp.maximum(integral_f ** 2, 1e-12)

    padded = jnp.pad(f, (0, N))
    fft_f = jnp.fft.fft(padded)
    conv = jnp.fft.ifft(fft_f * fft_f).real * dx

    # log-sum-exp smooth max
    smooth_max = temp * jax.scipy.special.logsumexp(conv / temp)
    return smooth_max / integral_f_sq


def run_smooth_adam(raw_init, temps, steps_per_temp, lr, clip_norm=1.0):
    """Run Adam with smooth-max objective, annealing through temperature list."""
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=lr,
        warmup_steps=max(200, steps_per_temp // 10),
        decay_steps=steps_per_temp * len(temps),
        end_value=lr * 5e-3,
    )
    optimizer = optax.chain(
        optax.clip_by_global_norm(clip_norm),
        optax.adam(learning_rate=schedule),
    )

    N = len(raw_init)
    dx = 0.5 / N
    raw = raw_init
    opt_state = optimizer.init(raw)

    for temp in temps:
        obj = lambda r: smooth_c(r, temp, dx)
        grad_fn = jax.jit(jax.value_and_grad(obj))

        for _ in range(steps_per_temp):
            loss, grads = grad_fn(raw)
            updates, opt_state = optimizer.update(grads, opt_state, raw)
            raw = optax.apply_updates(raw, updates)

    return raw


def upsample(raw_coarse, N_fine):
    """Upsample raw parameters from coarse to fine grid via linear interpolation."""
    N_coarse = len(raw_coarse)
    x_coarse = jnp.linspace(0, 1, N_coarse)
    x_fine = jnp.linspace(0, 1, N_fine)
    return jnp.interp(x_fine, x_coarse, raw_coarse)


def lbfgs_polish(raw_init, N):
    """L-BFGS-B polish on softplus-reparameterized parameters (no box constraints needed)."""
    dx = 0.5 / N

    def obj_and_grad(raw_np):
        raw_jax = jnp.array(raw_np)
        loss, grads = jax.value_and_grad(lambda r: smooth_c(r, 1e-5, dx))(raw_jax)
        return float(loss), np.array(grads)

    result = scipy.optimize.minimize(
        obj_and_grad,
        np.array(raw_init),
        method='L-BFGS-B',
        jac=True,
        options={'maxiter': 3000, 'ftol': 1e-14, 'gtol': 1e-9},
    )
    return jnp.array(result.x)


def entrypoint() -> np.ndarray:
    N_coarse = 50
    N_mid = 200
    N_fine = 600

    # Temperature schedules
    coarse_temps = [0.05, 0.01, 0.003]
    mid_temps = [0.003, 0.001]
    fine_temps = [0.001, 0.0003, 0.0001, 0.00003]

    coarse_steps = 3000   # per temp
    mid_steps = 5000
    fine_steps = 8000

    lr_coarse = 0.01
    lr_mid = 0.005
    lr_fine = 0.003

    best_coarse_c = float('inf')
    best_coarse_raw = None

    dx_coarse = 0.5 / N_coarse

    # Stage 1: 16 restarts at coarse resolution
    for seed in range(16):
        key = jax.random.PRNGKey(seed * 31 + 7)
        subkey1, subkey2 = jax.random.split(key)

        # Diverse initializations
        if seed < 6:
            # Gaussian bump at random position
            x = jnp.linspace(-0.25, 0.25, N_coarse)
            pos = jax.random.uniform(subkey1, (), minval=-0.15, maxval=0.15)
            width = jax.random.uniform(subkey2, (), minval=0.04, maxval=0.15)
            bump = jnp.exp(-((x - pos) ** 2) / (2 * width ** 2))
            raw = jnp.log(jnp.expm1(jnp.clip(bump, 1e-4, None)))
        elif seed < 10:
            # Asymmetric ramp
            x = jnp.linspace(0, 1, N_coarse)
            offset = seed * 0.07
            ramp = jnp.clip(x - offset, 0, None)
            ramp = ramp / (jnp.sum(ramp) * dx_coarse + 1e-8)
            raw = jnp.log(jnp.expm1(jnp.clip(ramp * 0.5 + 0.01, 1e-4, None)))
        else:
            # Random noise init
            raw = 0.3 * jax.random.normal(key, (N_coarse,))

        raw = run_smooth_adam(raw, coarse_temps, coarse_steps, lr_coarse)

        f_final = jax.nn.softplus(raw)
        c_val = float(compute_c(f_final))
        if c_val < best_coarse_c:
            best_coarse_c = c_val
            best_coarse_raw = raw

    # Stage 2: Upsample to mid resolution and refine
    raw_mid = upsample(best_coarse_raw, N_mid)
    raw_mid = run_smooth_adam(raw_mid, mid_temps, mid_steps, lr_mid)

    # Stage 3: Upsample to fine resolution and refine
    raw_fine = upsample(raw_mid, N_fine)
    raw_fine = run_smooth_adam(raw_fine, fine_temps, fine_steps, lr_fine)

    # Stage 4: L-BFGS-B polish
    raw_polished = lbfgs_polish(raw_fine, N_fine)

    f_out = jax.nn.softplus(raw_polished)
    return np.array(f_out)
