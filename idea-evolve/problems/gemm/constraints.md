# Constraints

## Hard Constraints

1. **Correctness**: Output must be identical to `gemmV0` (naive reference) for all test sizes:
   - (64, 64, 256), (32, 1024, 16), (64, 16384, 32), (128, 65536, 56)
   - Any mismatch → invalid solution (`is_valid: 0`)

2. **Function signature**: Must be exactly:
   ```cpp
   void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k)
   ```

3. **Must compile** with g++ 13.3.0 using these flags:
   `-O3 -std=c++17 -march=native -mavx512f -mavx512bw -mavx512vl -mavx512vpopcntdq -mavx512bitalg -mavx512vnni`

4. **Data layout**: A is ternary-encoded (2 bytes per k-byte group), B is binary-encoded
   (1 bit per element, k-dimension transposed). k is in bits, k_bytes = k/8.

5. **Must zero C** before accumulating results.

6. **No external dependencies** beyond standard C++ headers and immintrin.h.

## Soft Constraints

- **Single-thread only** — no OpenMP, no pthreads, no multi-threading
- **Target CPU: i5-1135G7 (Tiger Lake)** — may use any ISA extension this CPU supports
- May use `_mm_malloc` / `_mm_free` for aligned memory allocation
- Keep compilation time under 30 seconds
- Keep total benchmark time under 3 minutes

## Environment

- Compiler: g++ 13.3.0 (Ubuntu)
- OS: Linux 6.x
- CPU: Intel i5-1135G7 @ 2.40GHz (4C/8T, Tiger Lake)
- Available headers: `<immintrin.h>`, `<stdint.h>`, `<string.h>`, `<algorithm>`, `<cstdlib>`, standard C++ headers
