---
type: cluster
id: cluster_003
name: "Helper Techniques"
lifecycle: established
confidence: 0.95
first_seen: gen_01
last_updated: gen_01
last_confirmed_gen: gen_01
members: [idea_008]
best_score: null
tags: [helper, speedup, bucket, compatibility]
---

# Cluster: Helper Techniques

## Description

Performance optimizations and utility functions that enable other approaches. These are not solving approaches themselves but provide critical speedups.

## Evidence

- idea_008 (bucket compatibility): Used in all ILNS solutions and individual extension attempts. 23x speedup confirmed.

## Membership

- idea_008: Bucket-based compatibility pruning (established, confidence 0.95)

## Performance

Not a solving approach — enables ~0.2s compatibility checks on full 40320-permutation space.

## Exhausted?

**No.** Bucket structure could be applied to PGL orbits and cross-group search. The technique is general.

## For Gen 2

`fast_compatible_mask()` should be used for all PGL orbit clique experiments and the compatible-permutation count experiment.
