"""
Search q=109 pp construction for 106-mark rulers with span <= 10000.
pp type: modulus = q^2 + q + 1 = 11991, marks = q+1 = 110
"""
import time

with open("data/modrules-pp-00") as f:
    content = f.read()

modrule_gaps = None
for line in content.strip().split('\n'):
    if line.startswith("109:"):
        parts = line.split()
        modrule_gaps = [int(x) for x in parts[1:]]
        break

if modrule_gaps is None:
    print("Could not find pp modular ruler for q=109")
    exit(1)

q = 109
mod = q * q + q + 1  # 11991
expected_length = q + 1  # 110

print(f"q={q}, mod={mod}, expected marks={expected_length}")

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

for target in [110, 109, 108, 107, 106]:
    best_span = float('inf')
    best_mul = None
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
        count += 1

    print(f"{target} marks from pp q=109: best span={best_span}, mul={best_mul} {'<= 10000 FITS!' if best_span <= 10000 else '> 10000'}")
    if best_span <= 10000:
        break  # Found it
