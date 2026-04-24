# Manifest Reasoning - Generation 1

## Situation Assessment
This is a cold start. `knowledge/state_of_affairs.md` says no generations have run, there are no clusters, no coverage matrix, no score history, and no previous reports. The only population member is `population/gen000/baseline/sol01.py`, but its `.score` sidecar is invalid with sentinel fitness 100000.00 because the evaluator could not find the `fast-conv` harness files. The header comment's historical 770 us claim is useful context, but not an authoritative score.

The problem itself is clear: minimize geometric median time for binary-ternary GEMM on Tiger Lake, with tiny `k_bytes` values and huge `m`. The target of 24 us is far beyond incremental BLIS tuning, so generation 1 needs both a reliable valid candidate and orthogonal kernel bets.

## Agent Mix
The generation 1 rule requires exactly 2 explore, 1 full, and 1 research. I followed that rule and did not include exploit, genetic, or experimentator agents because there is no valid high-performing population to refine or cross.

`explore_1` owns the most direct high-probability speedup: AVX-512 BITALG popcount, 64 columns per vector, no KC tiling, and hand-unrolled `k_bytes` dispatch.

`explore_2` owns the radical alternative: VNNI or byte dot-product reformulation. This is intentionally separated from `explore_1` so the generation does not collapse into several versions of the same popcount kernel.

`full_1` is tasked with producing the first dependable valid solution. It can borrow baseline edge handling but should simplify and modernize the kernel rather than chase a risky formulation.

`research_1` surveys untried domain approaches and diagnoses the invalid baseline anomaly. That report should give the next Architect concrete directions beyond the current active idea list.

## Scheduling
`metrics.yaml` sets `concurrency: 0`, so all four agents are in one parallel group. Splitting would waste wall-clock time and add unnecessary light-evaluator phases in a cold-start setting where no later agent depends on an earlier helper.

## Timeouts
There is no prior timing data. I set both explore agents to 1800s because C++ SIMD kernels need compile/evaluate iteration time. The full agent gets 2100s to handle correctness, tails, and benchmarking. The research agent gets 900s because its deliverable is analysis and implementation guidance, not broad candidate iteration.

## Deliberately Not Chosen
No exploit agent: there is no valid best solution.

No genetic agent: there are no parents with trustworthy scores.

No experimentator: the system has no repeated helper request or unresolved empirical question yet. If generation 1 agents repeatedly struggle with test harness setup, a generation 2 experimentator/helper task may be justified.

No serial grouping: unlimited eval concurrency makes one group the right schedule.

## Risks and Contingencies
The largest risk is environmental: the current baseline failed because required harness files were missing. If all agents see the same failure, the System Critic should treat this as infrastructure breakage rather than algorithmic failure.

The second risk is validity. AVX-512 bit operations over packed ternary/binary layouts are easy to get subtly wrong, especially tails and signed contribution logic. `full_1` is scoped conservatively to protect against a generation with only invalid prototypes.

If VNNI proves too costly because packed B must be expanded, `explore_2` should still return a useful negative result with a clear cost model.
