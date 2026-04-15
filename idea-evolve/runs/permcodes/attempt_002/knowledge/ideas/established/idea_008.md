---
type: idea
id: idea_008
name: "Bucket-Based Compatibility Pruning"
lifecycle: established
confidence: 0.95
first_seen: gen_01
last_updated: gen_01
last_confirmed_gen: gen_01
supported_by: [gen001_explore_2_sol01, gen001_explore_2_sol02, gen001_explore_2_sol05, gen001_explore_1_sol02]
contradicted_by: []
related_ideas: [idea_006, idea_003]
cluster: cluster_003
tags: [helper, optimization, bucket, compatibility, speedup]
---

# Bucket-Based Compatibility Pruning

## What It Is

A precomputation technique that groups permutations by their "bucket signature" — the set of positions where they differ from a reference point. This enables O(1) compatibility checking: two permutations are guaranteed incompatible if they share a bucket with the same elements in conflicting positions.

The `fast_compatible_mask()` function from `helpers/compat.py` implements this as a bitmask-based filter, reducing compatibility checking from O(n²) pairwise comparisons to near-constant time using bucket lookups.

## How It Works

1. For each permutation, compute a bucket ID based on which "bucket" it falls into (70 buckets for n=8, d=5)
2. Build a lookup table: for each bucket, which other buckets are compatible
3. `fast_compatible_mask(code_indices, bucket_ids)`: compute compatible set in O(#code × #buckets)

## Evidence

- Used in all ILNS solutions (sol01, sol02, sol05)
- Used in individual extension attempts (explore_1/sol02, full_1/sol02)
- Benchmark: 23x faster than naive pairwise Hamming distance checking
- Enables checking all 40320 permutations against a code in ~0.2 seconds

## Current Performance

This is an enabling technique, not a solving approach. It makes ILNS feasible (60-150s instead of minutes) and makes individual extension tractable.

## When It Helps

Every stochastic approach benefits. The bucket structure captures the essential incompatibility pattern of the Hamming metric without computing all pairwise distances.

## Key Implementation Notes

- `build_bucket_ids(all_perms)` → shape (40320, 70) array of bucket indices
- `fast_compatible_mask(code_indices, bucket_ids)` → boolean mask of compatible permutations
- The 70 bucket IDs exactly partition the 40320 permutations
- Two permutations in the same bucket are guaranteed to have Hamming distance < 5
