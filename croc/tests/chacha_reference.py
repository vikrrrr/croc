"""Reference functions and data for ChaCha quarter-round, double-round and full-rounds testing"""

__all__ = ["quarter_round", "single_round", "double_round", "rounds_finish", "chacha"]

MASK_32 = 0xFFFF_FFFF


def quarter_round(state: list[int], a: int, b: int, c: int, d: int) -> list[int]:
    """ChaCha quarter round"""

    def bit_rotate(n: int, amount: int) -> int:
        n = n & MASK_32

        return ((n << amount) & MASK_32) | (n >> (32 - amount))

    state[a] = (state[a] + state[b]) & MASK_32
    state[d] ^= state[a]
    state[d] = bit_rotate(state[d], 16)

    state[c] = (state[c] + state[d]) & MASK_32
    state[b] ^= state[c]
    state[b] = bit_rotate(state[b], 12)

    state[a] = (state[a] + state[b]) & MASK_32
    state[d] ^= state[a]
    state[d] = bit_rotate(state[d], 8)

    state[c] = (state[c] + state[d]) & MASK_32
    state[b] ^= state[c]
    state[b] = bit_rotate(state[b], 7)

    return state


def single_round(state: list[int], is_odd: bool) -> list[int]:
    """ChaCha single round

    Parameters
    ----------
    is_odd : bool
        Whether to apply an odd (is_odd=True) or an even (is_odd=False) round of ChaCha.
    """

    if is_odd:
        # diagonals
        quarter_round(state, 0, 5, 10, 15)
        quarter_round(state, 1, 6, 11, 12)
        quarter_round(state, 2, 7, 8, 13)
        quarter_round(state, 3, 4, 9, 14)
    else:
        # columns
        quarter_round(state, 0, 4, 8, 12)
        quarter_round(state, 1, 5, 9, 13)
        quarter_round(state, 2, 6, 10, 14)
        quarter_round(state, 3, 7, 11, 15)

    return state


def double_round(state: list[int]) -> list[int]:
    """ChaCha double round"""

    single_round(state, False)
    single_round(state, True)

    return state


def rounds_finish(mixed_state: list[int], old_state: list[int]) -> list[int]:
    """Finish ChaCha rounds

    Parameters
    ----------
    mixed_state : list[int]
        Post-rounds state and output state.
    old_state : list[int]
        A copy of the pre-rounds state.
    """

    for idx, n in enumerate(old_state):
        mixed_state[idx] = (mixed_state[idx] + n) & MASK_32

    return mixed_state


def chacha(state: list[int], n_rounds: int) -> list[int]:
    """ChaCha rounds function

    Parameters
    ----------
    state : list[int]
        Input and output state.
    n_rounds : int
        Amount of rounds to perform.
    """

    assert n_rounds in (8, 12, 20), f"invalid round count {n_rounds}"

    old_state = state.copy()

    for _ in range(n_rounds // 2):
        double_round(state)

    rounds_finish(state, old_state)

    return state


def int_to_state(state: int) -> list[int]:
    """Convert an integer ChaCha state to a word-wise ChaCha state"""

    ret = []

    for n in range(16):
        m = state >> ((15 - n) * 32)
        ret.append(m & MASK_32)

    return ret


def state_to_int(state: list[int]) -> int:
    """Convert an word-wise ChaCha state to an integer ChaCha state"""

    ret = 0

    for n, w in enumerate(state):
        w &= MASK_32
        ret |= w << ((15 - n) * 32)

    return ret


test_state = [n for n in range(16)]
assert int_to_state(state_to_int(test_state)) == test_state
