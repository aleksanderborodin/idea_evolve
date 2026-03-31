"""
Helper utilities for the binary-ternary GEMM optimization problem.

Import: from helpers.core import compile_and_test, read_baseline_times
"""

import json
import os
import subprocess
import tempfile
import uuid
from pathlib import Path

FAST_CONV = Path(__file__).resolve().parent.parent.parent.parent / "fast-conv"
BASELINE_JSON = FAST_CONV / "baseline.json"

CXX = "g++"
CXXFLAGS = [
    "-O3", "-std=c++17", "-march=native",
    "-mavx512f", "-mavx512bw", "-mavx512vl",
    "-mavx512vpopcntdq", "-mavx512bitalg", "-mavx512vnni",
]


def compile_and_test(cpp_code: str) -> dict:
    """
    Quick compile + correctness check only (no benchmark).
    Returns {"ok": True} or {"ok": False, "error": "..."}.
    """
    uid = uuid.uuid4().hex[:8]
    candidate_path = f"/tmp/gemm_test_{uid}.cpp"
    binary_path = f"/tmp/gemm_test_{uid}"

    try:
        with open(candidate_path, "w") as f:
            f.write(cpp_code)

        result = subprocess.run(
            [CXX] + CXXFLAGS + [
                candidate_path,
                str(FAST_CONV / "bench_harness.cpp"),
                str(FAST_CONV / "util" / "encoder.cpp"),
                str(FAST_CONV / "gemm" / "baseline.cpp"),
                "-lbenchmark", "-lpthread",
                "-o", binary_path,
            ],
            capture_output=True, text=True, timeout=30,
        )

        if result.returncode != 0:
            return {"ok": False, "error": f"Compilation failed:\n{result.stderr[:1500]}"}

        check = subprocess.run(
            [binary_path, "--check"],
            capture_output=True, text=True, timeout=60,
        )

        if check.returncode != 0:
            return {"ok": False, "error": f"Correctness failed:\n{check.stderr[:1000]}"}

        return {"ok": True}

    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Timeout during compile or test"}
    finally:
        for p in [candidate_path, binary_path]:
            try:
                os.unlink(p)
            except FileNotFoundError:
                pass


def read_baseline_times() -> dict:
    """
    Returns baseline V14opt times in microseconds per benchmark size.
    Example: {"32x1024x9": 15.78, "64x16384x27": 911.64, "128x65536x54": 12422.36}
    """
    if not BASELINE_JSON.exists():
        return {}

    data = json.loads(BASELINE_JSON.read_text())
    times = {}

    for b in data["benchmarks"]:
        if (b.get("aggregate_name") == "mean"
                and b["run_type"] == "aggregate"
                and "gemmV14_BLIS_SingleThread_Optimized" in b.get("run_name", "")):
            parts = b["run_name"].split("/")
            size_parts = []
            for p in parts[1:]:
                cleaned = p.split("_")[0]
                if cleaned.isdigit():
                    size_parts.append(cleaned)
                if len(size_parts) == 3:
                    break
            if len(size_parts) == 3:
                key = f"{size_parts[0]}x{size_parts[1]}x{size_parts[2]}"
                times[key] = round(b["cpu_time"], 2)

    return times
