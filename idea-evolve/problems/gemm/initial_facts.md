# Hardware Facts: Intel i5-1135G7 (Tiger Lake)

## fact_001: CPU Specifications
Architecture: Tiger Lake (11th Gen), Willow Cove core.
4 cores / 8 threads, 2.40 GHz base / 4.20 GHz boost.

## fact_002: Cache Hierarchy
- L1 Data: 48 KB per core, 12-way associative, 64-byte lines, 5-cycle latency
- L1 Instruction: 32 KB per core
- L2 Unified: 1.25 MB per core, 10-way, 64-byte lines, ~12-cycle latency
- L3 Shared: 8 MB, ~40-cycle latency
- Memory bandwidth: ~38 GB/s (dual-channel LPDDR4x-4266)

## fact_003: AVX-512 on Tiger Lake
Tiger Lake does NOT downclock for AVX-512 (unlike Skylake-X / Ice Lake).
Single execution unit for 512-bit ops (port 0 or port 5 depending on instruction).
32 × zmm registers (512-bit each) — double the AVX2 register file.
Available extensions: AVX512F, BW, VL, DQ, CD, VPOPCNTDQ, BITALG, VNNI, IFMA, VBMI, VBMI2.

## fact_004: Key Instruction Latencies
- `vpopcntb` (zmm, BITALG): port 5, 1c latency, 1c throughput — per-byte popcount
- `vpdpbusd` (zmm, VNNI): port 0, 5c latency, 1c throughput — int8 dot-product
- `vpshufb` (ymm/zmm): port 5, 1c latency, 1c throughput
- `vpandd`/`vpord`/`vpxord` (zmm): port 0 or 5, 1c latency, 0.5c throughput (2 per cycle)
- `vpmovzxbd` / `vpmovsxbd` (zmm): port 5, 3c latency, 1c throughput — widen 8→32
- `_mm512_set1_epi8`: 1c throughput via broadcast

## fact_005: Benchmark Sizes
| Label  | n   | m      | k_bits | k_bytes | A size | B size   | C size     |
|--------|-----|--------|--------|---------|--------|----------|------------|
| Small  | 32  | 1,024  | 16     | 2       | 128B   | 2 KB     | 128 KB     |
| Medium | 64  | 16,384 | 32     | 4       | 512B   | 64 KB    | 4 MB       |
| Large  | 128 | 65,536 | 56     | 7       | 1.8 KB | 448 KB   | 32 MB      |

k_bytes is always tiny (2-7). A always fits in L1. B-panels need L2 tiling.
C is huge for large m — consider streaming stores.
