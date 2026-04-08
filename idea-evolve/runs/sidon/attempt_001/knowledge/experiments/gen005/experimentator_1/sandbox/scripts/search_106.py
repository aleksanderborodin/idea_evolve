"""
Search all multipliers for q=107 (pp type) to find 106-mark rulers with span <= 10000.
Modulus = 107^2 + 107 + 1 = 11557. Modular ruler has 108 marks.
"""
import math
import time

# Read the modular ruler for q=107 from the pp file
# Format: "107: gap1 gap2 gap3 ..."
with open("data/modrules-pp-00") as f:
    content = f.read()

# Parse the modular ruler for q=107
lines = content.strip().split('\n')
modrule_gaps = None
for line in lines:
    if line.startswith("107:"):
        parts = line.split()
        # First part is "107:", rest are gaps
        modrule_gaps = [int(x) for x in parts[1:]]
        break

if modrule_gaps is None:
    print("Could not find modular ruler for q=107")
    exit(1)

q = 107
mod = q * q + q + 1  # 11557
expected_length = q + 1  # 108

print(f"q={q}, mod={mod}, expected marks={expected_length}")
print(f"Got {len(modrule_gaps)} gaps")

# Convert gaps to positions
positions = []
s = 0
for g in modrule_gaps:
    positions.append(s)
    s += g
assert s == mod, f"Sum of gaps = {s}, expected {mod}"
assert len(positions) == expected_length

print(f"Modular ruler positions (first 10): {positions[:10]}")

# For each multiplier coprime to mod, multiply positions, sort, scan for contiguous sub-rulers
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

target_marks = 106
best_span = float('inf')
best_mul = None
best_ruler = None
count = 0

start = time.time()

# Only need to check multipliers coprime to mod
# Due to symmetry, only need to check ~1/6 of them (as noted in the page)
# But let's check all for completeness
for mul in range(1, mod):
    if gcd(mul, mod) != 1:
        continue

    # Multiply and sort
    multiplied = sorted([(p * mul) % mod for p in positions])

    # Scan for contiguous sub-rulers of size target_marks
    # Extend by wrapping around
    extended = multiplied + [m + mod for m in multiplied]

    for i in range(len(multiplied)):
        span = extended[i + target_marks - 1] - extended[i]
        if span < best_span:
            best_span = span
            best_mul = mul
            best_ruler = [extended[i + j] - extended[i] for j in range(target_marks)]

    count += 1
    if count % 1000 == 0:
        elapsed = time.time() - start
        print(f"  Checked {count} multipliers, best span for {target_marks} marks: {best_span}, elapsed: {elapsed:.1f}s")

elapsed = time.time() - start
print(f"\nDone. Checked {count} multipliers in {elapsed:.1f}s")
print(f"Best {target_marks}-mark ruler: span={best_span}, multiplier={best_mul}")

if best_span <= 10000:
    print(f"SUCCESS! Found 106-mark ruler with span {best_span} <= 10000!")
    print(f"Ruler: {best_ruler}")
else:
    print(f"FAILURE: Best span {best_span} > 10000. Cannot fit 106 marks.")

# Also check for 107 marks just in case
best_span_107 = float('inf')
count = 0
for mul in range(1, mod):
    if gcd(mul, mod) != 1:
        continue
    multiplied = sorted([(p * mul) % mod for p in positions])
    extended = multiplied + [m + mod for m in multiplied]
    for i in range(len(multiplied)):
        if i + 107 - 1 >= len(extended):
            break
        span = extended[i + 107 - 1] - extended[i]
        if span < best_span_107:
            best_span_107 = span
    count += 1

print(f"\nBest 107-mark ruler: span={best_span_107}")
if best_span_107 <= 10000:
    print("107 marks fits in [0, 10000]!")
else:
    print(f"107 marks needs span {best_span_107} > 10000")

# Check 108 marks (full modular ruler)
best_span_108 = float('inf')
for mul in range(1, mod):
    if gcd(mul, mod) != 1:
        continue
    multiplied = sorted([(p * mul) % mod for p in positions])
    span = multiplied[-1] - multiplied[0]
    if span < best_span_108:
        best_span_108 = span

print(f"Best 108-mark ruler (full): span={best_span_108}")
