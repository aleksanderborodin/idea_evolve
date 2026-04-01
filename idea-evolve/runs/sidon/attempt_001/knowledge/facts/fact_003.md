---
id: fact_003
type: fact
name: "AVX-512 on Tiger Lake"
confidence: 0.8
first_seen: generation_0
verified: false
source: user-provided
tags: []
---

Tiger Lake does NOT downclock for AVX-512 (unlike Skylake-X / Ice Lake).
Single execution unit for 512-bit ops (port 0 or port 5 depending on instruction).
32 × zmm registers (512-bit each) — double the AVX2 register file.
Available extensions: AVX512F, BW, VL, DQ, CD, VPOPCNTDQ, BITALG, VNNI, IFMA, VBMI, VBMI2.
