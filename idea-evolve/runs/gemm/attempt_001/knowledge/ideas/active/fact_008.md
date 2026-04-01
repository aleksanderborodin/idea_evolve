---
type: fact
id: fact_008
name: "vpopcntb is Dual-Port (0/1), NOT Port 5"
confidence: 0.9
first_seen: generation_3
verified: true
source: "experimentator_1 gen003 port throughput microbenchmark (tight loop, 8 independent instances)"
tags: [vpopcntb, port, throughput, avx512, bitalg, tiger-lake]
---

Experimentator_1 (gen003) ran instruction throughput microbenchmarks:

| Instruction | Throughput (ns) | Inferred Port | Notes |
|-------------|----------------|---------------|-------|
| vpopcntb (zmm) | 0.255 ns | port 0/1 (dual) | ~0.5c throughput |
| vpbroadcastb (zmm) | 0.489 ns | port 5 (single) | ~1c throughput |
| vpternlogq (zmm) | ~0.5 ns | port 0/5 (dual) | ~0.5c throughput |

**This corrects fact_004's claim that vpopcntb is port 5.** The earlier port
assignment was based on user-provided instruction tables that were incorrect
for Tiger Lake's Willow Cove core.

**Critical implication:** The PORT 5 bottleneck in the inner loop is from
vpbroadcastb (2 broadcasts per k-byte × 1c throughput = 2c port-5 per iteration),
NOT from vpopcntb. This changes optimization priorities:

1. Eliminating or reducing vpbroadcastb ops is higher priority than changing
   the popcount path
2. Pre-broadcasting A values outside the inner loop (already done by best solution)
   is essential — the compiler must keep them in zmm registers
3. The vpshufb alternative (idea_018) was misguided because it doesn't fix the
   actual bottleneck (port 5 broadcast)

**Verification needed:** Assembly inspection to confirm the compiler actually
keeps pre-broadcast A values in registers across the j-loop. If it spills and
re-broadcasts, the port-5 bottleneck is still present.
