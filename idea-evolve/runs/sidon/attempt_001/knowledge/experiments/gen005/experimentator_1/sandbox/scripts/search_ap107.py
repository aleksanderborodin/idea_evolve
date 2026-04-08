"""
Search q=107 affine plane (ap) construction for 106-mark rulers with span <= 10000.
ap type: modulus = q^2 - 1, marks = q
q=107: modulus = 11448, marks = 107
"""
import math
import time

with open("data/modrules-ap-00") as f:
    content = f.read()

modrule_gaps = None
for line in content.strip().split('\n'):
    if line.startswith("107:"):
        parts = line.split()
        modrule_gaps = [int(x) for x in parts[1:]]
        break

if modrule_gaps is None:
    print("Could not find ap modular ruler for q=107")
    exit(1)

q = 107
mod = q * q - 1  # 11448
expected_length = q  # 107

print(f"q={q}, mod={mod}, expected marks={expected_length}")
print(f"Got {len(modrule_gaps)} gaps")

positions = []
s = 0
for g in modrule_gaps:
    positions.append(s)
    s += g
assert s == mod
assert len(positions) == expected_length

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

# Search for 106-mark sub-rulers
for target in [106, 105]:
    best_span = float('inf')
    best_mul = None
    best_ruler = None
    count = 0

    for mul in range(1, mod):
        if gcd(mul, mod) != 1:
            continue
        multiplied = sorted([(p * mul) % mod for p in positions])
        extended = multiplied + [m + mod for m in multiplied]
        for i in range(len(multiplied)):
            if i + target - 1 >= len(extended):
                break
            span = extended[i + target - 1] - extended[i]
            if span < best_span:
                best_span = span
                best_mul = mul
                best_ruler = [extended[i + j] - extended[i] for j in range(target)]
        count += 1

    print(f"\n{target} marks from ap q=107: best span={best_span}, mul={best_mul}")
    if best_span <= 10000:
        print(f"SUCCESS! {target}-mark ruler fits in [0,10000]!")
        print(f"Ruler: {best_ruler}")
    else:
        print(f"Does not fit: span {best_span} > 10000")
