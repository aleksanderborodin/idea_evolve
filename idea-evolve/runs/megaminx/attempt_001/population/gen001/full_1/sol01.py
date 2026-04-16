# fitness: 46312

def entrypoint() -> dict:
    from helpers.core import (
        load_test,
        load_sample_submission_paths,
        is_solved,
        apply_path,
        cayleypy_beam_solver,
        depth_bucket,
    )

    tests = load_test(proxy=True)
    sample = load_sample_submission_paths()
    compressed_sample = {sid: _cancel_moves(path) for sid, path in sample.items()}

    BEAM_PARAMS = {
        'short': (512, 50),
        'medium': (1024, 120),
        'hard': (2048, 200),
        'very_hard': (512, 200),
    }

    out: dict = {}
    for sid, init_state in tests.items():
        bucket = depth_bucket(sid)
        fallback = compressed_sample[sid]

        # special: just use compressed sample (72-move scramble)
        if bucket == 'special':
            out[sid] = fallback
            continue

        beam_width, max_steps = BEAM_PARAMS[bucket]
        search_path = cayleypy_beam_solver(
            init_state, beam_width=beam_width, max_steps=max_steps
        )

        if search_path and is_solved(apply_path(init_state, search_path)):
            if len(search_path.split('.')) < len(fallback.split('.')):
                out[sid] = search_path
            else:
                out[sid] = fallback
        else:
            out[sid] = fallback

    return out


def _cancel_moves(path: str) -> str:
    if not path:
        return path
    moves = path.split('.')
    stack: list[str] = []
    for m in moves:
        if not m:
            continue
        if stack and stack[-1] == _inverse(m):
            stack.pop()
        else:
            stack.append(m)
    return '.'.join(stack)


def _inverse(move: str) -> str:
    if move.startswith('-'):
        return move[1:]
    return f'-{move}'