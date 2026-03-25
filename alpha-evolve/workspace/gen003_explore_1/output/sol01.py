# fitness: 0.0
# Approach: Coarse-scale SA (Boyer et al.) — N=40 coarse, SA basin-hopping, upsample→N=600, warm fine
# SA at coarse grid (N=40): 25 SA iters × 5k inner steps. 3 initial seeds.
# Key insight: at N=40 the landscape is smoother; SA can escape local minima.
# Fine stage starts WARM (T=0.05) — cold fine stage is a confirmed dead end.

import sys
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

import jax
import jax.numpy as jnp
import numpy as np
import optax
from helper import compute_c


def make_smooth_c(N):
    domain_width = 0.5
    dx = domain_width / N

    def _fn(raw_params, temp):
        f_nn = jax.nn.softplus(raw_params)
        integral_f = jnp.sum(f_nn) * dx
        integral_f_sq = jnp.maximum(integral_f ** 2, 1e-9)
        padded_f = jnp.pad(f_nn, (0, N))
        fft_f = jnp.fft.fft(padded_f)
        conv_f_f = jnp.fft.ifft(fft_f * fft_f).real
        scaled_conv = conv_f_f * dx
        smooth_max = temp * jax.scipy.special.logsumexp(scaled_conv / temp)
        return smooth_max / integral_f_sq
    return _fn


def run_optimizer(raw_init, temps, steps_per_temp, peak_lr=0.01, end_lr=5e-5):
    N = len(raw_init)
    smooth_c = make_smooth_c(N)
    total_steps = steps_per_temp * len(temps)
    schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0, peak_value=peak_lr,
        warmup_steps=min(200, total_steps // 15),
        decay_steps=total_steps, end_value=end_lr)
    optimizer = optax.adam(learning_rate=schedule)

    @jax.jit
    def step_fn(raw_params, temp, opt_state):
        loss, grads = jax.value_and_grad(smooth_c)(raw_params, temp)
        updates, new_opt_state = optimizer.update(grads, opt_state, raw_params)
        return optax.apply_updates(raw_params, updates), new_opt_state, loss

    opt_state = optimizer.init(raw_init)
    raw_params = raw_init
    for temp in temps:
        t = jnp.array(temp, dtype=jnp.float32)
        for _ in range(steps_per_temp):
            raw_params, opt_state, _ = step_fn(raw_params, t, opt_state)
    return raw_params


def upsample(raw_coarse, N_fine):
    N_coarse = len(raw_coarse)
    x_coarse = jnp.linspace(0, 1, N_coarse)
    x_fine = jnp.linspace(0, 1, N_fine)
    return jnp.interp(x_fine, x_coarse, raw_coarse)


def get_c_from_raw(raw_params, N):
    f_vals = jax.nn.softplus(raw_params)
    return float(compute_c(f_vals))


def make_random_init(key, N):
    x = jnp.linspace(-0.25, 0.25, N)
    pos1 = jax.random.uniform(key, (), minval=-0.18, maxval=0.18)
    w1 = jax.random.uniform(jax.random.fold_in(key, 1), (), minval=0.04, maxval=0.18)
    bump1 = jnp.exp(-((x - pos1) ** 2) / (2 * w1 ** 2))

    pos2 = jax.random.uniform(jax.random.fold_in(key, 3), (), minval=-0.23, maxval=0.23)
    w2 = jax.random.uniform(jax.random.fold_in(key, 4), (), minval=0.02, maxval=0.1)
    amp2 = jax.random.uniform(jax.random.fold_in(key, 5), (), minval=0.2, maxval=1.0)
    bump2 = amp2 * jnp.exp(-((x - pos2) ** 2) / (2 * w2 ** 2))

    noise = 0.05 * jax.random.normal(jax.random.fold_in(key, 2), (N,))
    init_f = jnp.clip(bump1 + bump2, 1e-4, None)
    return jnp.log(jnp.expm1(init_f)) + noise


def entrypoint() -> np.ndarray:
    N_coarse = 40
    N_fine = 600
    num_seeds = 4        # initial diverse seeds
    n_sa_iters = 25      # SA iterations per seed
    sa_inner_steps = 5000  # inner Adam steps per SA iteration
    sa_inner_temps = [0.05, 0.01]  # 2 temps × 5k = 10k inner steps

    # SA temperature schedule (Metropolis temperature, not smooth-max temp)
    sa_temp_0 = 0.008    # initial SA acceptance temperature
    sa_temp_decay = 0.94  # decay per SA iteration

    # Coarse init: strong convergence so SA starts from a good local minimum
    temps_coarse_init = [0.1, 0.05, 0.01, 0.003]  # 4 temps × 5k = 20k steps
    coarse_init_steps = 5000

    # Fine stage: WARM start, full annealing
    temps_fine = [0.05, 0.01, 0.003, 0.001, 0.0003]  # 5 temps × 15k = 75k steps
    fine_steps = 15000

    best_c_global = float('inf')
    best_raw_coarse = None

    for seed_idx in range(num_seeds):
        key = jax.random.PRNGKey(seed_idx * 37 + 13)

        # Initial coarse optimization to find a good starting basin
        raw_init = make_random_init(key, N_coarse)
        raw_coarse = run_optimizer(raw_init, temps_coarse_init,
                                   steps_per_temp=coarse_init_steps,
                                   peak_lr=0.01, end_lr=1e-4)

        c_init = get_c_from_raw(raw_coarse, N_coarse)
        print(f"\n[seed {seed_idx}] Initial coarse C = {c_init:.6f}")

        # SA loop at coarse grid
        current_raw = raw_coarse
        current_c = c_init
        best_raw_this_seed = raw_coarse
        best_c_this_seed = c_init

        accepted = 0
        for sa_iter in range(n_sa_iters):
            sa_temp = sa_temp_0 * (sa_temp_decay ** sa_iter)

            # Perturbation: Gaussian noise proportional to std of current f
            f_current = jax.nn.softplus(current_raw)
            sigma = 0.3 * float(jnp.mean(jnp.abs(f_current)))
            noise_key = jax.random.PRNGKey(seed_idx * 10000 + sa_iter * 100 + 7)
            perturbation = sigma * jax.random.normal(noise_key, current_raw.shape)
            raw_perturbed = current_raw + perturbation

            # Re-optimize perturbed solution (warm inner optimizer)
            raw_candidate = run_optimizer(raw_perturbed, sa_inner_temps,
                                          steps_per_temp=sa_inner_steps,
                                          peak_lr=0.008, end_lr=1e-4)

            c_candidate = get_c_from_raw(raw_candidate, N_coarse)

            # Metropolis acceptance
            delta_c = c_candidate - current_c
            if delta_c < 0:
                accept = True
            else:
                accept_prob = float(jnp.exp(-delta_c / sa_temp))
                u_key = jax.random.PRNGKey(seed_idx * 10000 + sa_iter * 100 + 99)
                accept = float(jax.random.uniform(u_key)) < accept_prob

            if accept:
                current_raw = raw_candidate
                current_c = c_candidate
                accepted += 1

            if c_candidate < best_c_this_seed:
                best_c_this_seed = c_candidate
                best_raw_this_seed = raw_candidate

            if (sa_iter + 1) % 5 == 0:
                acc_rate = accepted / (sa_iter + 1)
                print(f"  SA iter {sa_iter+1}/{n_sa_iters}: current={current_c:.6f}, "
                      f"best_seed={best_c_this_seed:.6f}, accept_rate={acc_rate:.2f}")

        print(f"[seed {seed_idx}] SA done: best_seed C = {best_c_this_seed:.6f}")

        if best_c_this_seed < best_c_global:
            best_c_global = best_c_this_seed
            best_raw_coarse = best_raw_this_seed

    print(f"\nBest coarse C across all seeds: {best_c_global:.6f}")

    # Upsample to fine grid and run warm fine-tuning
    raw_fine_init = upsample(best_raw_coarse, N_fine)
    print(f"Upsampled to N={N_fine}, running warm fine-tuning...")

    raw_fine = run_optimizer(raw_fine_init, temps_fine,
                             steps_per_temp=fine_steps,
                             peak_lr=0.005, end_lr=1e-5)

    f_final = jax.nn.softplus(raw_fine)
    c_final = float(compute_c(f_final))
    print(f"Final C after fine-tuning: {c_final:.6f}")

    return np.array(f_final)
