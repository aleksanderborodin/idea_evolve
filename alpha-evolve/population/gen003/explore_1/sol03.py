# fitness: 1.5169
# Approach: Coarse-scale SA at N=30 with perturbation in FUNCTION VALUE space
# Key fix from sol01/sol02: perturb softplus(raw) values directly, not raw_params
# At N=30 (Boyer et al. scale), fewer local minima, SA can hop basins.
# 4 seeds × 35 SA iters × 5k inner steps each. Fine-tune best result.
#
# sol02 problem: sigma=0.4*std(raw_params) was enormous (15-25).
# Fix: perturb f_values directly, then re-encode as raw_params.

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


def inv_softplus(y):
    """Inverse softplus: x = log(exp(y) - 1) = log1p(-exp(-y)) + log(y) approx"""
    # Stable version: x = log(exp(y) - 1) = y + log(1 - exp(-y))
    # For large y: x ≈ y. For small y: x ≈ log(y).
    return jnp.where(y > 20.0, y, jnp.log(jnp.expm1(jnp.clip(y, 1e-6, 20.0))))


def get_c_from_raw(raw_params):
    f_vals = jax.nn.softplus(raw_params)
    return float(compute_c(f_vals))


def make_random_init(key, N):
    x = jnp.linspace(-0.25, 0.25, N)
    pos1 = jax.random.uniform(key, (), minval=-0.18, maxval=0.18)
    w1 = jax.random.uniform(jax.random.fold_in(key, 1), (), minval=0.05, maxval=0.2)
    bump1 = jnp.exp(-((x - pos1) ** 2) / (2 * w1 ** 2))

    pos2 = jax.random.uniform(jax.random.fold_in(key, 3), (), minval=-0.22, maxval=0.22)
    w2 = jax.random.uniform(jax.random.fold_in(key, 4), (), minval=0.03, maxval=0.12)
    amp2 = jax.random.uniform(jax.random.fold_in(key, 5), (), minval=0.2, maxval=1.0)
    bump2 = amp2 * jnp.exp(-((x - pos2) ** 2) / (2 * w2 ** 2))

    noise = 0.05 * jax.random.normal(jax.random.fold_in(key, 2), (N,))
    init_f = jnp.clip(bump1 + bump2, 1e-4, None)
    return jnp.log(jnp.expm1(init_f)) + noise


def perturb_in_function_space(raw_params, sigma, key):
    """Perturb in softplus(raw) space, return new raw_params."""
    f_vals = jax.nn.softplus(raw_params)
    noise = sigma * jax.random.normal(key, f_vals.shape)
    f_perturbed = jnp.clip(f_vals + noise, 1e-4, None)
    return inv_softplus(f_perturbed)


def entrypoint() -> np.ndarray:
    N_coarse = 30     # Boyer et al. scale: very coarse, smoother landscape
    N_fine = 600
    num_seeds = 4

    # Initial coarse convergence: strong (same schedule as best gen002 solutions)
    temps_coarse_init = [0.1, 0.05, 0.02, 0.005, 0.001]  # 5 × 6k = 30k steps
    coarse_init_steps = 6000

    # SA parameters
    n_sa_iters = 35
    # Inner: warm, converge properly from perturbed state
    sa_inner_temps = [0.05, 0.01, 0.003]  # 3 × 5k = 15k inner steps
    sa_inner_steps = 5000
    # Metropolis temperature: coarse C diffs are ~0.001-0.005 at N=30
    # Target 20-40% acceptance: exp(-0.003/T) = 0.3 → T ≈ 0.0025
    sa_metro_temp_0 = 0.004
    sa_metro_decay = 0.90
    # Perturbation: in function value space, sigma relative to mean function value
    sa_sigma_frac = 0.35  # sigma = fraction * mean(softplus(raw))

    # Fine-tuning: WARM start, full annealing
    temps_fine = [0.05, 0.01, 0.003, 0.001, 0.0003]  # 5 × 15k = 75k
    fine_steps = 15000

    best_c_global = float('inf')
    best_raw_coarse = None

    for seed_idx in range(num_seeds):
        key = jax.random.PRNGKey(seed_idx * 41 + 17)

        # Initial convergence
        raw_init = make_random_init(key, N_coarse)
        raw_coarse = run_optimizer(raw_init, temps_coarse_init,
                                   steps_per_temp=coarse_init_steps,
                                   peak_lr=0.01, end_lr=5e-5)

        c_init = get_c_from_raw(raw_coarse)
        print(f"\n[seed {seed_idx}] Initial coarse C = {c_init:.6f}")

        current_raw = raw_coarse
        current_c = c_init
        best_raw_this_seed = raw_coarse
        best_c_this_seed = c_init

        accepted = 0
        for sa_iter in range(n_sa_iters):
            metro_temp = sa_metro_temp_0 * (sa_metro_decay ** sa_iter)

            # Perturbation in function value space (scale-correct)
            f_current = jax.nn.softplus(current_raw)
            sigma = sa_sigma_frac * float(jnp.mean(f_current))

            pert_key = jax.random.PRNGKey(seed_idx * 10000 + sa_iter * 100 + 7)
            raw_perturbed = perturb_in_function_space(current_raw, sigma, pert_key)

            # Warm inner re-optimization
            raw_candidate = run_optimizer(raw_perturbed, sa_inner_temps,
                                          steps_per_temp=sa_inner_steps,
                                          peak_lr=0.008, end_lr=5e-5)

            c_candidate = get_c_from_raw(raw_candidate)

            # Metropolis
            delta_c = c_candidate - current_c
            if delta_c < 0:
                accept = True
            else:
                accept_prob = float(jnp.exp(-delta_c / max(metro_temp, 1e-8)))
                u_key = jax.random.PRNGKey(seed_idx * 10000 + sa_iter * 100 + 99)
                accept = float(jax.random.uniform(u_key)) < accept_prob

            if accept:
                current_raw = raw_candidate
                current_c = c_candidate
                accepted += 1

            if c_candidate < best_c_this_seed:
                best_c_this_seed = c_candidate
                best_raw_this_seed = raw_candidate

            if (sa_iter + 1) % 7 == 0:
                acc_rate = accepted / (sa_iter + 1)
                print(f"  SA iter {sa_iter+1}/{n_sa_iters}: current={current_c:.6f}, "
                      f"best_seed={best_c_this_seed:.6f}, accept_rate={acc_rate:.2f}, "
                      f"sigma={sigma:.4f}, metro_T={metro_temp:.5f}")

        print(f"[seed {seed_idx}] SA done: best_seed C = {best_c_this_seed:.6f}")

        if best_c_this_seed < best_c_global:
            best_c_global = best_c_this_seed
            best_raw_coarse = best_raw_this_seed

    print(f"\nBest coarse C (N={N_coarse}) = {best_c_global:.6f}")

    # Upsample and warm fine-tuning
    raw_fine_init = upsample(best_raw_coarse, N_fine)
    print(f"Running warm fine-tuning at N={N_fine}...")
    raw_fine = run_optimizer(raw_fine_init, temps_fine,
                             steps_per_temp=fine_steps,
                             peak_lr=0.005, end_lr=1e-5)

    f_final = jax.nn.softplus(raw_fine)
    c_final = float(compute_c(f_final))
    print(f"Final C after fine-tuning: {c_final:.6f}")

    return np.array(f_final)
