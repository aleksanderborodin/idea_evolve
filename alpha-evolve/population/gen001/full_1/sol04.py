# fitness: TBD
# Approach: graduated smoothing (more phases, lower final temp) + 12 restarts + N=800
# Building on sol03's success (1.5108). More restarts, lower final temp (T=0.0001),
# higher resolution (N=800), and fine-tuning phase with true max.

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax
from helper import compute_c


def make_smooth_c(temp):
    """C with log-sum-exp approximation to max."""
    def fn(raw_params):
        domain_width = 0.5
        N = len(raw_params)
        dx = domain_width / N

        f_nn = jax.nn.softplus(raw_params)
        integral_f = jnp.sum(f_nn) * dx
        integral_f_sq = jnp.maximum(integral_f**2, 1e-9)

        padded_f = jnp.pad(f_nn, (0, N))
        fft_f = jnp.fft.fft(padded_f)
        conv_f_f = jnp.fft.ifft(fft_f * fft_f).real
        scaled_conv = conv_f_f * dx

        smooth_max = temp * jax.scipy.special.logsumexp(scaled_conv / temp)
        return smooth_max / integral_f_sq
    return fn


def run_optimization(raw_init, N, temps, steps_per_phase, base_lr):
    total_steps = steps_per_phase * len(temps)
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=base_lr,
        warmup_steps=min(1000, steps_per_phase // 3),
        decay_steps=max(total_steps - 1000, 1),
        end_value=base_lr * 5e-4,
    )
    optimizer = optax.adam(learning_rate=schedule)
    raw_params = raw_init
    opt_state = optimizer.init(raw_params)

    for temp in temps:
        obj_fn = make_smooth_c(temp)

        @jax.jit
        def step(raw_p, opt_st):
            loss, grads = jax.value_and_grad(obj_fn)(raw_p)
            updates, new_opt_st = optimizer.update(grads, opt_st, raw_p)
            return optax.apply_updates(raw_p, updates), new_opt_st, loss

        for _ in range(steps_per_phase):
            raw_params, opt_state, _ = step(raw_params, opt_state)

    f_final = jax.nn.softplus(raw_params)
    return raw_params, float(compute_c(f_final))


def entrypoint() -> np.ndarray:
    N = 800
    x = jnp.linspace(-0.25, 0.25, N)

    # Extended temperature schedule: coarse → fine
    temps = [0.05, 0.02, 0.008, 0.003, 0.001, 0.0003, 0.0001]
    steps_per_phase = 12000  # 84k total per restart
    base_lr = 0.006

    best_c = float('inf')
    best_raw = None

    for seed in range(12):
        key = jax.random.PRNGKey(seed * 31 + 5)

        # Diverse initializations
        init_type = seed % 4
        if init_type == 0:
            # Centered Gaussian, random width
            width = 0.08 + 0.12 * float(jax.random.uniform(jax.random.fold_in(key, 0)))
            init_f = jnp.exp(-(x**2) / (2 * width**2))
        elif init_type == 1:
            # Off-center Gaussian
            pos = float(jax.random.uniform(jax.random.fold_in(key, 0), minval=-0.10, maxval=0.10))
            init_f = jnp.exp(-((x - pos)**2) / (2 * 0.10**2))
        elif init_type == 2:
            # Raised cosine
            width = 0.15 + 0.10 * float(jax.random.uniform(jax.random.fold_in(key, 0)))
            init_f = jnp.maximum(0.0, jnp.cos(jnp.pi * x / (2 * width)))
        else:
            # Uniform window with random extent
            hw = 0.05 + 0.15 * float(jax.random.uniform(jax.random.fold_in(key, 0)))
            init_f = jnp.where(jnp.abs(x) <= hw, 1.0, 0.05)

        # Convert to raw (softplus-inverse)
        raw_init = jnp.log(jnp.expm1(jnp.clip(init_f, 1e-4, None)))
        noise = 0.02 * jax.random.normal(jax.random.fold_in(key, 10), (N,))
        raw_init = raw_init + noise

        raw_final, c_val = run_optimization(raw_init, N, temps, steps_per_phase, base_lr)

        if c_val < best_c:
            best_c = c_val
            best_raw = raw_final

    return np.array(jax.nn.softplus(best_raw))
