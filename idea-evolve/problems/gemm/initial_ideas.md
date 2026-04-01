# Initial Ideas for Binary-Ternary GEMM Optimization

## idea_001: AVX-512 Micro-Kernel with Hardware Popcount
Replace the 6-instruction LUT-based popcount (`vpshufb` + masks) with a single
`_mm512_popcnt_epi8()` instruction (AVX512_BITALG). Process 64 bytes of B per
iteration instead of 32 (AVX2). Micro-kernel shape becomes 4x64 (4 rows of A,
64 columns of B). This alone could give ~1.5-2x speedup in the micro-kernel.

## idea_002: Fully Unrolled k-Loop
k_bytes is always 2, 4, or 7 for our benchmark sizes. Instead of a generic loop,
create specialized versions for each k value. With k=2, the entire inner product
is just 2 iterations — the loop overhead dominates. Template specialization or
`switch(k_bytes)` dispatch to hand-unrolled code.

## idea_003: VNNI for Accumulation
`_mm512_dpbusd_epi32` computes a dot product of int8 values and accumulates into
int32, all in one instruction (1 cycle throughput). The binary-ternary multiply
might be reformulatable as a VNNI operation since element values are {-1,0,+1}
and {-1,+1}. This could eliminate the popcount step entirely.

## idea_004: int16 Accumulation
The diff per byte (popcount_pos - popcount_neg) is at most ±8. For k_bytes ≤ 15,
the accumulated sum fits in int16 (max ±120). Accumulate in 16-bit, widen to 32-bit
only at the end. This doubles the number of elements processed per register.

## idea_005: Re-tune BLIS Tile Sizes for Tiger Lake
Current: MC=64, KC=128, NC=256 (tuned for AVX2).
Tiger Lake has L1d=48KB, L2=1.25MB. With AVX-512 (64-byte wide ops):
- NC should be larger (more columns per B-panel, amortize B-packing)
- MC could stay at 64 (L1 fits 64 × 7 × 2 = 896 bytes of packed A easily)
- KC is irrelevant since k_bytes ≤ 7 always fits

## idea_006: Streaming Stores for Large m
For m=65536, each output row is 256KB — doesn't fit in L2. The output won't be
re-read soon. Use `_mm512_stream_si512` to bypass cache on stores, freeing cache
capacity for B data.

## idea_007: SIMD Packing
Current pack_A and pack_B are scalar byte-by-byte loops. Use SIMD loads/stores
for the copy. For pack_B with AVX-512: load 64 bytes from B with `_mm512_loadu_si512`,
store directly to B_packed.

## idea_008: Skip Tiling for Small k
When k_bytes ≤ 7, the entire k-dimension fits in registers. The KC loop always
has exactly one iteration. Remove the KC-tiling overhead entirely — just iterate
over m-tiles and n-tiles directly.

## idea_009: Wider Micro-Kernel 8x64
With 32 zmm registers (AVX-512), we can afford 8 rows × 1 zmm accumulator per row
= 8 registers for accumulators, plus a few for B data and temporaries. Process 8
rows of A at once instead of 4, halving the number of micro-kernel calls.
