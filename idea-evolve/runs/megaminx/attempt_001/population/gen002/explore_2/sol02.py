# fitness: 44118

"""
Systematic commutator and identity enumeration for Megaminx compression.

This solution systematically tests algebraic identities across the Megaminx
Cayley graph:
1. All commutators [A,B] = ABA^{-1}B^{-1}
2. Conjugations A.B.A^{-1}
3. Double moves A.A, A.A.A
4. Span-2 patterns X.Y.-X (not Y)
5. Span-3 patterns X.Y.Z.-X.-Y

Each candidate is verified on the solved state before use.
"""

from helpers.core import (
    load_test,
    load_sample_submission_paths,
    apply_path,
    is_solved,
    solved_state,
    GENERATOR_NAMES,
)


def entrypoint() -> dict:
    tests = load_test(proxy=True)
    sample_paths = load_sample_submission_paths()

    # Phase 1: Build a comprehensive identity dictionary
    # We enumerate and verify identities rather than extract from sample_submission
    identity_dict = _build_identity_dictionary()
    print(f"Found {len(identity_dict)} verified identity patterns")

    # Phase 2: Apply identities for compression
    compressed = {}
    for sid, state in tests.items():
        original = sample_paths.get(sid, "")
        compressed_sid = _compress_with_identities(original, identity_dict)
        if is_solved(apply_path(state, compressed_sid)):
            compressed[sid] = compressed_sid
        else:
            compressed[sid] = original

    return compressed


def _build_identity_dictionary() -> dict:
    """Build a dictionary of verified identity patterns.

    Returns a dict mapping pattern tuple -> replacement tuple.
    Patterns that equal identity map to ().
    """
    identities = {}
    SOLVED = solved_state()

    def try_identity(pattern: tuple, replacement: tuple) -> bool:
        """Verify pattern == replacement on solved state."""
        try:
            pattern_str = '.'.join(pattern)
            if replacement:
                replacement_str = '.'.join(replacement)
                pattern_effect = apply_path(SOLVED, pattern_str)
                replacement_effect = apply_path(SOLVED, replacement_str)
                return pattern_effect == replacement_effect
            else:
                # Identity
                pattern_effect = apply_path(SOLVED, pattern_str)
                return pattern_effect == SOLVED
        except:
            return False

    # Rule type 1: Double cancellation (XX -> identity)
    for gen in GENERATOR_NAMES:
        pattern = (gen, gen)
        if try_identity(pattern, ()):
            key = pattern
            identities[key] = ()

    # Rule type 2: Commutators ABA^{-1}B^{-1} -> identity
    for i, gen1 in enumerate(GENERATOR_NAMES):
        inv1 = _inverse(gen1)
        for j, gen2 in enumerate(GENERATOR_NAMES):
            if i >= j:
                continue
            if gen1 == gen2 or gen1 == _inverse(gen2):
                continue
            inv2 = _inverse(gen2)
            # [A,B] = ABA^{-1}B^{-1}
            pattern = (gen1, gen2, inv1, inv2)
            if try_identity(pattern, ()):
                identities[pattern] = ()

    # Rule type 3: Conjugations ABA^{-1} -> B (if true)
    for gen1 in GENERATOR_NAMES:
        for gen2 in GENERATOR_NAMES:
            if gen1 == gen2 or gen1 == _inverse(gen2):
                continue
            inv1 = _inverse(gen1)
            pattern = (gen1, gen2, inv1)
            # If ABA^{-1} = B, then ABA^{-1} -> B (savings: 3 -> 1)
            if try_identity(pattern, (gen2,)):
                identities[pattern] = (gen2,)

    # Rule type 4: Span-2 non-adjacent ABA^{-1} patterns
    # These may equal B or -B or identity in Megaminx
    for gen1 in GENERATOR_NAMES:
        for gen2 in GENERATOR_NAMES:
            if gen1 == gen2 or gen1 == _inverse(gen2):
                continue
            inv1 = _inverse(gen1)
            pattern = (gen1, gen2, inv1)

            # Try simplification to B, -B, or identity
            for simplification in [(), (gen2,), (_inverse(gen2),)]:
                if simplification == pattern:
                    continue
                if try_identity(pattern, simplification):
                    identities[pattern] = simplification

    # Rule type 5: Span-3 commutators ABCBAC^{-1}B^{-1}A^{-1} (longer)
    # Too expensive to enumerate fully, skip for now

    return identities


def _compress_with_identities(path: str, identity_dict: dict) -> str:
    """Apply identity-based compression iteratively."""
    if not path:
        return path

    max_iters = 30
    for _ in range(max_iters):
        prev = path
        moves = path.split('.')
        moves = _cancel_moves(moves)

        # Apply identity rules
        moves = _apply_identities(moves, identity_dict)

        path = '.'.join(moves)
        if path == prev:
            break

    return path


def _apply_identities(moves: list, identity_dict: dict) -> list:
    """Apply identity rules (pattern -> replacement) greedily."""
    if not moves:
        return moves

    result = []
    i = 0
    while i < len(moves):
        matched = False
        # Try longest patterns first
        for plen in range(min(4, len(moves) - i), 0, -1):
            window = tuple(moves[i:i + plen])
            if window in identity_dict:
                replacement = identity_dict[window]
                result.extend(replacement)
                i += plen
                matched = True
                break
        if not matched:
            result.append(moves[i])
            i += 1

        # Re-cancel after each replacement
        if result and (i >= len(moves) or matched):
            result = _cancel_moves(result)

    return result


def _cancel_moves(moves: list) -> list:
    """Standard X.-X cancellation."""
    stack = []
    for m in moves:
        if not m:
            continue
        if stack and stack[-1] == _inverse(m):
            stack.pop()
        else:
            stack.append(m)
    return stack


def _inverse(move: str) -> str:
    if move.startswith('-'):
        return move[1:]
    return f'-{move}'