# Sidon Sets (B2 Sequences)

## Problem

Find the largest possible **Sidon set** (also called a B2 sequence) within the range {0, 1, ..., N}.

A Sidon set is a set S of non-negative integers where **all pairwise sums are distinct** — that is, if a + b = c + d with a <= b and c <= d, then a = c and b = d. Equivalently, all positive differences between elements are distinct.

## Parameters

- **N = 10,000** (elements must be in range [0, 10000])
- **Target: |S| >= 100**

## Solution Format

Your `entrypoint()` function must return a **list of distinct non-negative integers**, each in [0, 10000].

```python
def entrypoint():
    return [0, 1, 3, 7, 12, 20, ...]
```

## Scoring

- **Primary metric: `fitness`** = size of the largest valid Sidon subset (maximize)
- If the returned set has violations (repeated pairwise sums), the validator extracts the largest valid Sidon subset and scores that
- A set with zero violations scores its full size
- Invalid returns score 0 (sentinel)

## Baseline

A simple greedy algorithm (add smallest valid element) achieves **66 elements**. This is the starting point. The theoretical maximum for N=10,000 is approximately 100 elements (sqrt(N) bound).

## Helpers Available

```python
from helpers.core import is_sidon, count_violations, differences, can_add, is_prime
```

- `is_sidon(S)` — check if S is a valid Sidon set
- `count_violations(S)` — count repeated pairwise sums
- `differences(S)` — get all positive differences
- `can_add(S_sorted, used_diffs, candidate)` — check if an element can be added without conflict
- `is_prime(n)` — primality test

## Mathematical Background

For a Sidon set in {0, ..., N}, the maximum size is approximately sqrt(N). The exact optimum for N=10,000 is not known. The problem is NP-hard in general.
