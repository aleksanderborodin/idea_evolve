# fitness: TBD
# Approach: graduated smoothing (log-sum-exp max, annealed temp) + 8 random restarts
# Key insight: jnp.max gives sparse gradient (only argmax gets signal).
# log-sum-exp with annealed temperature spreads gradient across near-max elements,
# giving richer optimization signal. Start warm (T=0.1), cool to T=0.001.

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax
from helper import compute_c


def make_smooth_compute_c(temp):
    def smooth_compute_c(f_values):
        domain_width = 0.5
        N = len(f_values)
        dx = domain_width / N

        f_nn = jax.nn.softplus(f_values)
        integral_f = jnp.sum(f_nn) * dx
        integral_f_sq = jnp.maximum(integral_f**2, 1e-9)

        padded_f = jnp.pad(f_nn, (0, N))
        fft_f = jnp.fft.fft(padded_f)
        conv_f_f = jnp.fft.ifft(fft_f * fft_f).real

        scaled_conv = conv_f_f * dx
        # Smooth max via log-sum-exp
        smooth_max = temp * jax.scipy.special.logsumexp(scaled_conv / temp)

        return smooth_max / integral_f_sq
    return smooth_compute_c


def entrypoint() -> np.ndarray:
    N = 600
    num_steps_per_phase = 15000
    # Temperature schedule: start warm, anneal in phases
    temps = [0.05, 0.01, 0.003, 0.001, 0.0003]  # 5 phases × 15k = 75k total
    base_lr = 0.005

    best_c = float('inf')
    best_raw = None

    x = jnp.linspace(-0.25, 0.25, N)

    for seed in range(8):
        key = jax.random.PRNGKey(seed * 17 + 3)

        # Random initialization: mix of gaussian bumps at random locations + noise
        pos = jax.random.uniform(key, (), minval=-0.15, maxval=0.15)
        width = jax.random.uniform(jax.random.fold_in(key, 1), (), minval=0.05, maxval=0.2)
        init_bump = jnp.exp(-((x - pos)**2) / (2 * width**2))
        noise_key = jax.random.fold_in(key, 2)
        noise = 0.05 * jax.random.normal(noise_key, (N,))
        # raw_params: in softplus space (so f = softplus(raw) > 0 always)
        # inv_softplus(y) = log(exp(y)-1) = log(expm1(y))
        raw_params = jnp.log(jnp.expm1(jnp.clip(init_bump, 1e-4, None))) + noise

        schedule = optax.warmup_cosine_decay_schedule(
            init_value=0.0,
            peak_value=base_lr,
            warmup_steps=500,
            decay_steps=num_steps_per_phase * len(temps) - 500,
            end_value=base_lr * 1e-3,
        )
        optimizer = optax.adam(learning_rate=schedule)
        opt_state = optimizer.init(raw_params)

        for temp in temps:
            smooth_obj = make_smooth_compute_c(temp)

            @jax.jit
            def train_step(raw_p, opt_st, temp=temp):
                loss, grads = jax.value_and_grad(make_smooth_compute_c(temp))(raw_p)
                updates, new_opt_st = optimizer.update(grads, opt_st, raw_p)
                new_raw_p = optax.apply_updates(raw_p, updates)
                return new_raw_p, new_opt_st, loss

            for _ in range(num_steps_per_phase):
                raw_params, opt_state, loss = train_step(raw_params, opt_state)

        f_final = jax.nn.softplus(raw_params)
        c_val = float(compute_c(f_final))

        if c_val < best_c:
            best_c = c_val
            best_raw = raw_params

    return np.array(jax.nn.softplus(best_raw))
