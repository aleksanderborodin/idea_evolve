"""Baseline: simple greedy Sidon set construction."""


def entrypoint():
    S = [0]
    diffs = set()
    for candidate in range(1, 10001):
        new_diffs = set()
        conflict = False
        for existing in S:
            d = candidate - existing
            if d in diffs:
                conflict = True
                break
            new_diffs.add(d)
        if not conflict:
            S.append(candidate)
            diffs.update(new_diffs)
    return S
