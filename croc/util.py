from collections.abc import Iterable, Sequence
from typing import TypeVar

from amaranth import *

T = TypeVar("T")


def window(seq: Sequence[T], n: int) -> Iterable[Sequence[T]]:
    """Iterate a rolling window of length `n` on `seq`"""

    from itertools import islice

    it = iter(seq)
    result = tuple(islice(it, n))

    if len(result) == n:
        yield result

    for elem in it:
        result = result[1:] + (elem,)
        yield result


# TODO: switch to built-in `rotate_left` when available
def bit_rotate(v: Value, amount: int) -> Value:
    """Bit-rotate `v` left by `amount`"""

    l = len(v)

    return Cat(v[l - amount : l], v[: l - amount])
