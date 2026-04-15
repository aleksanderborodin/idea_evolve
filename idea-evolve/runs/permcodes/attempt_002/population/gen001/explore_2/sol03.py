# fitness: TBD
"""
Genetic Algorithm for M(8,5) permutation codes.

Track B radical exploration: NO algebraic group structure.

Key ideas:
- Population of codes (sets of permutations)
- Crossover: take union of two codes, then prune incompatibilities greedily
- Mutation: add/remove codewords
- Tournament selection based on code size
"""

import numpy as np
import sys

sys.path.insert(0, '/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes')
from helpers.compat import build_all_perms, build_bucket_ids, fast_compatible_mask

N = 8
D = 5
ALL_PERMS = None
BUCKET_IDS = None


def setup():
    global ALL_PERMS, BUCKET_IDS
    if ALL_PERMS is None:
        print("Building permutation index...", flush=True)
        ALL_PERMS = build_all_perms(N)
        BUCKET_IDS = build_bucket_ids(ALL_PERMS)
        print(f"Built {len(ALL_PERMS)} permutations, {BUCKET_IDS.shape[1]} buckets", flush=True)


def make_code_compatible(code_indices, all_perms, bucket_ids, rng):
    """Given a set of indices (possibly incompatible), greedily prune to make compatible."""
    if len(code_indices) == 0:
        return []

    code_indices = list(set(code_indices))
    rng.shuffle(code_indices)

    result = []
    for idx in code_indices:
        arr = np.array(result, dtype=np.int32) if result else np.array([], dtype=np.int32)
        mask = fast_compatible_mask(arr, bucket_ids)
        if idx not in result and mask[idx]:
            result.append(int(idx))

    return result


def crossover(parent1_indices, parent2_indices, all_perms, bucket_ids, rng):
    """Crossover: union + greedy pruning."""
    union_indices = list(set(parent1_indices) | set(parent2_indices))
    return make_code_compatible(union_indices, all_perms, bucket_ids, rng)


def mutate_add(code_indices, all_perms, bucket_ids, rng, n_tries=3):
    """Try to add random codewords to the code."""
    mask = fast_compatible_mask(np.array(code_indices), bucket_ids)
    mask[code_indices] = False
    candidates = np.where(mask)[0]

    if len(candidates) == 0:
        return code_indices

    rng.shuffle(candidates)
    added = 0
    for cand in candidates[:n_tries * 10]:
        test_code = code_indices + [cand]
        test_mask = fast_compatible_mask(np.array(test_code), bucket_ids)
        if test_mask[cand]:
            code_indices = code_indices + [cand]
            added += 1
            if added >= n_tries:
                break

    return code_indices


def mutate_remove(code_indices, rng, n_remove=1):
    """Remove random codewords."""
    if len(code_indices) <= n_remove:
        return []
    remove_set = set(rng.choice(len(code_indices), n_remove, replace=False))
    return [c for i, c in enumerate(code_indices) if i not in remove_set]


def tournament_selection(population, scores, tournament_size=3, rng=None):
    """Select individual via tournament."""
    if rng is None:
        rng = np.random.RandomState()

    indices = rng.choice(len(population), tournament_size, replace=False)
    best_idx = indices[0]
    best_score = scores[indices[0]]

    for i in indices[1:]:
        if scores[i] > best_score:
            best_score = scores[i]
            best_idx = i

    return population[best_idx]


def run_ga(seed=42, pop_size=30, n_generations=100, verbose=True):
    """Run genetic algorithm."""
    rng = np.random.RandomState(seed)

    print("Building initial population...", flush=True)
    population = []
    scores = []

    for i in range(pop_size):
        r = np.random.RandomState(seed + i * 999)
        start_idx = r.randint(len(ALL_PERMS))

        code = [start_idx]
        while True:
            mask = fast_compatible_mask(np.array(code), BUCKET_IDS)
            mask[code] = False
            candidates = np.where(mask)[0]
            if len(candidates) == 0:
                break
            next_idx = candidates[r.randint(len(candidates))]
            code.append(next_idx)

        population.append(code)
        scores.append(len(code))

        if i % 10 == 0 and verbose:
            print(f"  Init {i}: size = {len(code)}", flush=True)

    best_overall = max(population, key=len)
    best_score = len(best_overall)

    if verbose:
        print(f"Initial population: best={best_score}, avg={np.mean(scores):.1f}", flush=True)

    for gen in range(n_generations):
        new_population = []
        new_scores = []

        for i in range(pop_size):
            r = np.random.RandomState(seed + gen * 1000 + i * 17)

            parent1 = tournament_selection(population, scores, tournament_size=3, rng=r)
            parent2 = tournament_selection(population, scores, tournament_size=3, rng=r)

            if r.random() < 0.1:
                child = list(parent1)
            else:
                child = crossover(parent1, parent2, ALL_PERMS, BUCKET_IDS, r)

            if r.random() < 0.2:
                child = mutate_add(child, ALL_PERMS, BUCKET_IDS, r, n_tries=5)
            if r.random() < 0.1:
                child = mutate_remove(child, r, n_remove=max(1, len(child) // 10))

            child = mutate_add(child, ALL_PERMS, BUCKET_IDS, r, n_tries=3)

            new_population.append(child)
            new_scores.append(len(child))

        population = new_population
        scores = new_scores

        gen_best = max(population, key=len)
        if len(gen_best) > best_score:
            best_score = len(gen_best)
            best_overall = list(gen_best)
            if verbose:
                print(f"Gen {gen}: new best = {best_score}", flush=True)

        if verbose and gen % 20 == 0:
            print(f"Gen {gen}: best={best_score}, avg={np.mean(scores):.1f}", flush=True)

    return best_overall


def entrypoint():
    setup()

    print("Running Genetic Algorithm...", flush=True)

    np.random.seed(42)
    code_indices = run_ga(seed=42, pop_size=40, n_generations=120, verbose=True)

    print(f"\nGA best: {len(code_indices)} codewords", flush=True)

    result = ALL_PERMS[np.array(code_indices)]
    return result


if __name__ == "__main__":
    result = entrypoint()
    print(f"Final code size: {len(result)}")