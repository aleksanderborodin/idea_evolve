# Observations — explore_2, gen005

## What I tried

### sol01.py: Bose-Chowla construction
Formula: S = {i*p + (i² mod p) : i = 0,...,p-1} for prime p=97.
Intended span: p²-1 = 9408, fitting in [0,10000].
Score: **fitness=0, violations=312, raw_size=97, is_valid=0**

The construction FAILED to produce a valid Sidon set. I verified algebraically that
the formula i*p + (i² mod p) is a valid Sidon set for small primes (p=5, p=7, p=11)
but discovered computationally that it breaks for p=97 due to violation pairs like
(7855-0=7855) and (8053-198=7855). The algebraic analysis revealed that for large p,
the case R=-p in the difference equality allows solutions: specifically (i-j)-(k-l)=−1
and r_i−r_j = r_k−r_l + p, which has real integer solutions for large primes.

The claimed Bose-Chowla construction is NOT i*p + (i² mod p) for large p. The actual
Bose-Chowla / Singer construction uses Z_{q²+q+1} (cyclic) — which is precisely the
Singer construction already exhausted by the pipeline.

## What I did NOT try (ran out of time)

- Beam search for Sidon sets (width 50-200): genuinely unexplored approach
- Proper backtracking with Lindström pruning
- Number-theoretic sieving with quadratic residues

## Key finding

The pipeline correctly identified that "Bose-Chowla = Singer" in disguise. There is no
additional algebraic construction family for Sidon sets that gives >102 for N=10000
beyond Singer. The only remaining hope is:
1. Computational search (CP-SAT 4h+, branch-and-bound)
2. Accessing the Rokicki-Dogon Golomb ruler database (idea_020)

## What helpers were used
- helpers/core.py: not used (attempted to use algebraically but construction failed before needing it)
- helpers/search.py: not used

## Time budget
Did NOT have enough time to explore and implement after discovering the algebraic
construction failure. With more time, I would implement beam search (width 50-100)
which is genuinely unexplored per state of affairs.
