# Debrief Report — gen007_explore_1 (Explore, Track B)

## Solution Summary

| File   | Approach | Fitness | Is Valid |
|--------|----------|---------|----------|
| sol01.py | Ruzsa-Lindstrom primitive root p=71 (2p-scaled) + VLNS k=3-15, 90s | **74** | Yes |
| sol02.py | Multi-seed random greedy (best of 20) + aggressive VLNS k=10-40, 110s | **65** | Yes |
| sol03.py | Ruzsa p=61 + p=71 multi-start, fast blocked-set VLNS, 90s | **75** | Yes |

Best solution: **sol03.py, fitness=75**

## 1. What did I try?

**Construction research (before writing any code):**
- Verified that {xp + g^x mod p} (naive primitive root, p=97) is NOT a valid Sidon set (264 violations). The integer arithmetic causes carry-induced sum collisions that the modular-group structure doesn't catch.
- Proved that {x*2p + g^x mod p} (2p-scaled primitive root) IS a valid Sidon set. The 2p spacing ensures high-part variation (2p) > max low-part variation (p-1), preventing carries.
- Verified both constructions computationally for p=61, 67, 71, 73.

**sol01:** Ruzsa primitive root p=71 (71 elements, max=9941) + greedy extension (→73) + VLNS k=3-15 for 90s. Result: **74**.

**sol02:** 20 random-order greedy starting sets (best had 62 elements) + aggressive VLNS k=10-40 for 110s. Result: **65**.

**sol03:** Multi-start: Ruzsa p=61 (61→68→70 with VLNS 30s) + Ruzsa p=71 (71→73→75 with VLNS 30s) + final extension from best. Result: **75**.

## 2. What information did I lack?

- **F₂(10000)**: The exact maximum size of a Sidon set in {0,...,10000} is unknown. Knowing this would tell us if 106 is achievable at all. State of affairs says this is in OEIS A003022 and rokicki_data.py but I was instructed not to use those.
- **CP-SAT formulation**: `helpers/cpsat.py` has been requested for 3 consecutive generations but doesn't exist. Without it, I can't use exact optimization to find if 76+ elements exist.
- **How many distinct "basins" exist for this N**: All algebraic constructions with p~71 seem to converge to the same 75-ceiling basin. I don't know if there are higher basins unreachable from these starts.

## 3. What given facts might be wrong or outdated?

- **idea_025** claims {x*p + g^x mod p} "produces a p-element Sidon set in {0,...,p²-1}". This is WRONG for integer arithmetic. It may be correct in Z_{p²} (cyclic group). The idea file should be corrected.
- **State of affairs** says "Ruzsa-Lindström: 0 trials". I now confirm the Ruzsa-Lindstrom (2p-scaled primitive root) basin ceiling is **75**, same as ET(71). The hypothesis of "different basin" appears FALSE.

## 4. Was the State of Affairs accurate?

Yes. The state of affairs was accurate:
- ET(71)+1-opt ceiling 75 is confirmed (my sol03=75 matches).
- All greedy variants ceiling ~70 confirmed (random greedy gives 62-66, VLNS gets to 65).
- The 105-mark set is correctly identified as requiring algebraic/CP-SAT methods, not local search from small seeds.

**One addition**: The state of affairs should note that the Ruzsa-Lindstrom construction is in the SAME basin as ET(71), not a different one.

## 5. What would I do differently with more context?

- I would have skipped the Ruzsa basin exploration entirely once I confirmed the primitive root construction is not a valid Sidon set.
- I would have focused time on implementing a correct CP-SAT solver formulation to directly search for 106+ element sets.
- I would have read `helpers/rokicki_data.py` to understand the true state of the art before deciding on an approach.

## 6. Specific experiments to run next

1. **Fix VLNS formulation**: The state of affairs mentions a formulation bug in the VLNS. Fix the abs-equality domain issue and retry 50+ removal patterns from the 105-mark set. This is the highest-priority next step.
2. **CP-SAT maximize formulation**: Implement `helpers/cpsat.py` with a maximize-k formulation instead of decision k=106. This is more solver-friendly and should be attempted with a 4h+ time budget.
3. **Swap-then-fill tabu search from 75**: Systematic tabu search starting from the 75-element set found here. Different from VLNS in that it's deterministic and avoids revisiting configurations. May push to 76-77.
4. **Large-k removal from 75**: VLNS with k=30-40 from the 75-element set, allowing reconstruction from a 35-45 element base. This explores much larger neighborhoods than k=3-15.

## 7. What surprised me?

- The naive primitive root construction {xp + g^x mod p} has 264 violations. I expected it to be a valid Sidon set based on idea_025, but integer arithmetic is fundamentally different from cyclic group arithmetic.
- The fast blocked-set VLNS is actually SLOWER per iteration than the naive VLNS (100 vs 155 iters/sec), but produces comparable results because it's smarter about candidate selection.
- Both algebraic constructions (quadratic ET and primitive root) with the same p give the SAME ceiling (~75) under VLNS. This strongly suggests they're in the same basin.

## 8. Helper tools feedback

- **helpers/core.py**: Correct and useful. `is_sidon`, `count_violations` were essential for verifying construction validity.
- **helpers/search.py**: `greedy_sidon` exists but only builds from scratch, not from an existing partial set. A `greedy_extend(base, N)` helper would have been very useful.
- **helpers/extend.py**: Referenced in the brief but DOES NOT EXIST. The brief says `from helpers.extend import greedy_extend` but this file is missing. I had to implement greedy extension inline.
- **MISSING**: `helpers/cpsat.py` — needed for exact optimization. Requested 3+ generations.
- **MISSING**: `helpers/vlns.py` — a correct VLNS implementation with the fixed abs-equality domain would be very useful.

## 9. Time budget

I had enough time for 3 solutions (each ~90-110s due to VLNS time limits). The main constraint was the per-solution evaluation time. With more time, I would have:
1. Implemented a proper swap-then-fill tabu search
2. Tried very large k (k=30-40) VLNS from the 75-element result
3. Attempted a CP-SAT formulation from scratch (without the helper)

The 75 ceiling appears robust. Breaking through likely requires exact methods, not local search.
