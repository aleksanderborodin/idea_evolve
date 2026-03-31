"""
Validate and benchmark a candidate binary-ternary GEMM implementation.

Input: C++ source code as a string (returned by entrypoint()).
Process: compile → correctness check → benchmark → extract times.
Output: dict with fitness (geo-median time in µs, lower=better), per-size times, is_valid.
"""

import fcntl
import json
import math
import os
import subprocess
import uuid
from pathlib import Path

# Lock file to ensure only one benchmark runs at a time on the pinned core
BENCH_LOCK = Path("/tmp/gemm_bench.lock")

# Benchmark cores — isolated via sudo taskset (NOPASSWD configured in sudoers)
BENCH_CORES = "0,1"

# Paths
FAST_CONV = Path(__file__).resolve().parent.parent.parent / "fast-conv"
HARNESS = FAST_CONV / "bench_harness.cpp"
ENCODER = FAST_CONV / "util" / "encoder.cpp"
BASELINE_CPP = FAST_CONV / "gemm" / "baseline.cpp"

# Compiler settings — optimized for i5-1135G7 (Tiger Lake)
CXX = "g++"
CXXFLAGS = [
    "-O3", "-std=c++17", "-march=native",
    "-mavx512f", "-mavx512bw", "-mavx512vl",
    "-mavx512vpopcntdq", "-mavx512bitalg", "-mavx512vnni",
]

# Reference times from existing implementations (µs, from baseline.json)
# Agents see these so they know what to beat
REFERENCE_TIMES = {
    "V14opt": {"32x1024x9": 15.78, "64x16384x27": 911.64, "128x65536x54": 12422.36},
    "V19":    {"32x1024x9": 19.51, "64x16384x27": 1229.37, "128x65536x54": 14987.16},
}


def _parse_bench_json(json_str):
    """Parse Google Benchmark JSON output, extract median times per size."""
    data = json.loads(json_str)
    times = {}
    for b in data.get("benchmarks", []):
        if b.get("aggregate_name") == "median" and b["run_type"] == "aggregate":
            parts = b["name"].split("/")
            size_parts = []
            for p in parts[1:]:
                cleaned = p.split("_")[0]
                if cleaned.isdigit():
                    size_parts.append(cleaned)
                if len(size_parts) == 3:
                    break
            if len(size_parts) == 3:
                key = f"{size_parts[0]}x{size_parts[1]}x{size_parts[2]}"
                times[key] = b["cpu_time"]
    return times


def validate(cpp_code):
    """
    Compile, test correctness, benchmark, and return metrics.

    Args:
        cpp_code: str — complete C++ source defining gemmCandidate()

    Returns:
        dict with fitness (geo-median time µs, lower=better), per-size times, is_valid
    """
    if not isinstance(cpp_code, str) or len(cpp_code.strip()) < 50:
        raise ValueError("entrypoint() must return a C++ source string defining gemmCandidate()")

    if "gemmCandidate" not in cpp_code:
        raise ValueError("C++ code must define void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k)")

    uid = uuid.uuid4().hex[:8]
    candidate_path = f"/tmp/gemm_candidate_{uid}.cpp"
    binary_path = f"/tmp/gemm_bench_{uid}"
    detail_path = f"/tmp/bench_detail_{uid}.json"

    try:
        # Write candidate source
        with open(candidate_path, "w") as f:
            f.write(cpp_code)

        # Compile
        compile_cmd = [CXX] + CXXFLAGS + [
            candidate_path,
            str(HARNESS),
            str(ENCODER),
            str(BASELINE_CPP),
            "-lbenchmark", "-lpthread",
            "-o", binary_path,
        ]

        compile_result = subprocess.run(
            compile_cmd,
            capture_output=True, text=True, timeout=30
        )

        if compile_result.returncode != 0:
            raise ValueError(f"Compilation failed:\n{compile_result.stderr[:2000]}")

        compiler_warnings = compile_result.stderr.strip() if compile_result.stderr.strip() else None

        # Correctness check
        check = subprocess.run(
            [binary_path, "--check"],
            capture_output=True, text=True, timeout=60
        )

        if check.returncode != 0:
            error_msg = check.stderr.strip() or check.stdout.strip()
            raise ValueError(f"Correctness check failed:\n{error_msg[:1000]}")

        # Benchmark — run in isolated cpuset cgroup (cores 0-1), one at a time
        lock_fd = open(BENCH_LOCK, "w")
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX)
            bench = subprocess.run(
                ["sudo", "cgexec", "-g", "cpuset:benchmark_isolated",
                 binary_path, "--bench", "--benchmark_format=json"],
                capture_output=True, text=True, timeout=180
            )
        finally:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            lock_fd.close()

        if bench.returncode != 0:
            raise ValueError(f"Benchmark failed:\n{bench.stderr[:1000]}")

        # Parse results
        candidate_times = _parse_bench_json(bench.stdout)

        if not candidate_times:
            raise ValueError("No benchmark results parsed from output")

        # Map benchmark size keys to metric names
        size_to_metric = {
            "32x1024x9": "time_small",
            "64x16384x27": "time_medium",
            "128x65536x54": "time_large",
        }

        # Geometric median of times across sizes (lower = better)
        time_values = [candidate_times[k] for k in size_to_metric if k in candidate_times]
        geomean = math.exp(sum(math.log(t) for t in time_values) / len(time_values))
        geomean = round(geomean, 2)

        # Write detailed diagnostics to sidecar
        detail = {
            "candidate_times_us": {k: round(v, 2) for k, v in candidate_times.items()},
            "reference_times_us": REFERENCE_TIMES,
            "geomean_time_us": geomean,
            "compiler_warnings": compiler_warnings,
            "vs_V14opt": {
                k: f"{REFERENCE_TIMES['V14opt'].get(k, 0) / v:.2f}x" if v > 0 else "N/A"
                for k, v in candidate_times.items()
            },
        }
        with open(detail_path, "w") as f:
            json.dump(detail, f, indent=2)

        result = {
            "fitness": geomean,
            "is_valid": 1,
            "detail_file": detail_path,
        }
        for size_key, metric_name in size_to_metric.items():
            if size_key in candidate_times:
                result[metric_name] = round(candidate_times[size_key], 2)

        return result

    finally:
        for p in [candidate_path, binary_path]:
            try:
                os.unlink(p)
            except FileNotFoundError:
                pass
