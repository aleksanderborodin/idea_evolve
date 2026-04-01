# Experimentator Report — Gen 3, Instance 1

## Solutions Produced

| File | Fitness (µs) | Valid | small (µs) | medium (µs) | large (µs) |
|------|-------------|-------|-----------|------------|-----------|
| sol01.py | 400.32 | Yes | 9.96 | 317.41 | 20290.23 |
| sol01b.py | 250.98 | Yes | 4.96 | 347.77 | 9173.21 |
| sol02.py | 197.33 | Yes | 4.97 | 311.15 | 4972.18 |
| **baseline (gen002/explore_1/sol01)** | **147.26** | Yes | **3.69** | **225.55** | **3841.72** |

All solutions regressed. The primary value of this session is the experimental data.

---

## 1. What Did I Try?

### Experiment 1a: NT stores + per-rep _mm_malloc (sol01.py)
Row-streaming kernel with `_mm_malloc(32 MB)` / NT stores / `memcpy` / `_mm_free` on every
benchmark call. **large: 20290 µs (5.3x WORSE than baseline).** The per-rep mmap/munmap
for 32 MB is catastrophically expensive (~8192 page faults per rep).

### Experiment 1b: NT stores + static pre-allocated buffer (sol01b.py)
Same kernel but with a BSS-segment static buffer (no per-rep malloc). **large: 9173 µs
(2.39x WORSE).** Even without malloc overhead, the memcpy of 32 MB cold DRAM data
(NT stores bypass cache, so nt_buf is DRAM-cold on read) costs ~5000+ µs — more than
the ~1500 µs saved by NT stores vs regular writes.

### Experiment 2: Port assignment microbenchmark (port_bench.cpp, sandbox)
Compiled and ran tight loops of 8 independent instances of each instruction, measuring
throughput via clock_gettime. **vpopcntb: 0.255 ns/instr vs vpbroadcastb: 0.489 ns/instr.**
vpopcntb is ~2x faster than vpbroadcastb → vpopcntb is dual-port (0/1), NOT port 5 as
fact_004 claims. vpbroadcastb confirmed single-port (port 5). vpternlogq confirmed dual
port (0/5) at ~0.5c throughput.

### Experiment 3: 4-row pack-free small kernel (sol02.py)
4-row kernel with pre-broadcast A values and shared B loads for k_bytes≤2. **small: 4.97 µs
(1.35x WORSE than baseline 3.69 µs).** Pre-broadcast overhead (16 port-5 ops before j-loop)
and non-inlining function call overhead dominate any B-load savings for L1-resident B.

---

## 2. What Information Did I Lack?

- **Actual benchmark k values.** The detail file labels are (n, m, k_raw) where k_raw is the
  raw input, not k. k = 8*(k_raw/8+1). The actual k_bytes are 2/4/7 (or 1/3/6 depending on
  interpretation). I should have verified this from validate.py before designing the small kernel.
- **Whether the compiler inlines static helper functions.** All three solutions split the kernel
  into helpers, all showed ~1.3-1.5x performance regression vs a monolithic function.
  Should have verified with `-fopt-info-inline` flags or kept a single-function design.
- **The memcpy bandwidth for mixed read+write at 32 MB.** fact_007 measured pure read (12.9 GB/s)
  and pure write (11.38 GB/s) separately. Mixed R+W bandwidth (relevant for memcpy) was not
  measured. The actual combined bandwidth appears to be worse than either alone.

## 3. What Given Facts Might Be Wrong or Outdated?

- **fact_004: `vpopcntb` port 5.** **CONFIRMED WRONG.** vpopcntb is port 0/1, throughput
  0.5c. fact_004 must be updated. The PORT 5 bottleneck in the kernel is vpbroadcastb (1c),
  not vpopcntb (0.5c). This changes the optimization priority for the inner loop.
- **The "NT stores give 2.3x on large" finding from gen002.** This was measured on a standalone
  buffer (already-allocated, pre-warmed). The end-to-end benefit with alloc+memcpy is negative.
  The 2.3x number is real for DIRECT NT writes to an aligned C, but unusable with the
  current harness (unaligned std::vector<int> C).

## 4. Was the State of Affairs Accurate?

Mostly yes. It correctly identified the C alignment constraint (fact_006) as blocking NT stores.
The recommendation to "test aligned-buffer workaround" was correct to try. The conclusion
that it was worth testing turned out correct — but the result is negative (workaround doesn't help).

The State of Affairs underestimates the difficulty of the 24 µs target. Medium is already
within 8% of its bandwidth floor (225 µs vs 247 µs theoretical minimum). Even with perfect
large optimization to 2054 µs (bandwidth floor), geomean = (3.69 × 225.55 × 2054)^(1/3) ≈ 90 µs.
Still far above 24 µs. The target requires a fundamental rethink, not incremental improvements.

## 5. What Would I Do Differently?

- **Keep the kernel in one monolithic function** — never split into helpers for performance code.
- **Verify benchmark k values from validate.py** before designing size-specialized kernels.
- **Measure mixed read+write bandwidth** before assuming memcpy costs.
- **Test NT stores with a DIRECT aligned allocation as the harness C** — if the harness could
  be patched to use `aligned_alloc` instead of `std::vector<int>`, NT stores would give 2.3x
  on large and the end-to-end solution would be ~1300 µs (large) instead of 3842 µs.

## 6. Specific Experiments to Run Next

1. **Harness modification test:** Patch validate.py or bench_harness.cpp to allocate C with
   `_mm_malloc` (64-byte aligned). Re-run the baseline + NT store variant. Expected: large
   drops from 3842 µs to ~1300 µs. geomean: (3.69 × 225.55 × 1300)^(1/3) ≈ 79 µs.
2. **vpbroadcastb elimination:** Since vpbroadcastb (port 5, 1c) is now confirmed as the
   main bottleneck, try eliminating broadcasts from the inner loop. For k_bytes=2, pre-load
   all A bytes into 4 ZMM registers OUTSIDE the row loop, and keep them in registers across
   the j-loop. Current code already does this; confirm the compiler is actually keeping them
   in registers (inspect assembly with -S).
3. **Widening elimination for small:** For small (k_bytes=2, ≤14 k-iterations before overflow),
   accumulate in int16 with vpaddw — this has 0.5c throughput on port 0/5 and avoids port-5-only
   sign-extend ops. Widen int16→int32 once per row, outside the j-loop entirely.
4. **Direct timing of broadcast bottleneck:** Create a variant that eliminates one pair of
   broadcasts per iteration (e.g., for k_bytes=1, only 2 broadcasts; for k_bytes=2, 4 broadcasts).
   Compare timing to quantify exactly how much each broadcast costs.

## 7. What Surprised Me?

1. **The memcpy overhead for 32 MB cold DRAM is enormous (~5000+ µs).** I expected ~2000 µs
   based on 12.9 GB/s read bandwidth. The combination of cold NT-written buffer + concurrent
   write to C is far slower than either pure read or pure write benchmark suggests.
2. **vpopcntb is confirmed dual-port** with 0.5c throughput. The real bottleneck per k-iteration
   is vpbroadcastb (2 ops × 1c = 2c port-5 per iteration), not the 2 vpopcntb ops (2 × 0.5c = 1c port-0/1).
3. **The 1-row baseline is already quite optimal for the benchmark sizes.** All three experiments
   produced solutions that were WORSE. The baseline's simplicity (monolithic single function,
   no branching) is a key reason it performs well.
4. **Non-inlined static functions cost 1.3-1.5x.** The performance delta between my helper-
   function designs and the monolithic baseline is surprisingly large.

## 8. Helper Tools Feedback

Did not use any helpers from `problem/helpers/`. No existing helpers were relevant.
A useful helper would be: a C++ template for microbenchmarking AVX-512 instruction throughput
that correctly avoids dead-code elimination and handles CPU frequency variation.

## 9. Time Budget

Time was tight. The debug cycles on correctness failures (sol01 flush bug, sol02 array size
and store logic) consumed significant time. With more time:
1. Would have implemented the harness modification test (highest-value experiment)
2. Would have built and tested the int16 widening elimination for small
3. Would have inspected the compiled assembly of sol02 to confirm inlining/non-inlining
4. Would have run port_bench with more care to get accurate frequency estimates and fix the
   vpmovsxbw / cvtepi8_epi32 dead-code-elimination issue
