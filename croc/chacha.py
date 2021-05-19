from functools import partial
from enum import Enum, unique

from nmigen import *
from nmigen.build import Platform

from .util import bit_rotate, window

__all__ = [
    "ChaChaState",
    "Rounds",
    "StagedChaChaRounds",
    "DoubleRound",
    "QuarterRound",
    "RoundsFinish",
]

# The amount of 32-bit words in the ChaCha state.
STATE_WORDS = 16
# Bit size of a word
WORD_SIZE = 32

ChaChaState = partial(Signal, STATE_WORDS * WORD_SIZE, reset=0)


def _w(state: ChaChaState, idx: int) -> Value:
    """Returns the 32-bit word at index `idx` in the ChaCha state"""

    return state.word_select(15 - idx, WORD_SIZE)


@unique
class Rounds(Enum):
    REDUCED_8 = "8"
    REDUCED_12 = "12"
    FULL_20 = "20"

    def __str__(self):
        return self.value

    @staticmethod
    def get_n_rounds(self):
        if self is Rounds.REDUCED_8:
            return 8
        elif self is Rounds.REDUCED_12:
            return 12
        elif self is Rounds.FULL_20:
            return 20


class StagedChaChaRounds(Elaboratable):
    """Multi-cycle staged ChaCha"""

    def __init__(self, rounds: Rounds, rounds_per_cycle: int = 2):
        n_rounds = Rounds.get_n_rounds(rounds)

        assert n_rounds >= rounds_per_cycle > 0, "rounds per cycle is not in range"
        assert (
            n_rounds % rounds_per_cycle == 0
        ), "round count must be mod rounds per cycle"
        assert rounds_per_cycle % 2 == 0, "rounds per cycle must be mod 2"

        self.n_rounds = n_rounds
        self.rounds_per_cycle = rounds_per_cycle
        self.total_stages = self.n_rounds // self.rounds_per_cycle

        # Enable module
        self.enabled_i = Signal()
        # Input ChaCha state
        self.state_i = ChaChaState()
        # Output ChaCha state
        self.state_o = ChaChaState()
        # Encryption done output
        self.done_o = Signal()

    def elaborate(self, _: Platform) -> Module:
        m = Module()

        # Current stage
        stage_r = Signal(range(self.total_stages))
        # Intermediate state used between stages
        intermediate_r = ChaChaState()
        # Pre-rounds state
        previous_state_r = ChaChaState()

        is_first_stage = stage_r == 0
        is_last_stage = stage_r == self.total_stages - 1

        # ChaCha double-round units
        double_rounds = [DoubleRound() for n in range(self.rounds_per_cycle // 2)]
        m.submodules += double_rounds

        rounds_finish = m.submodules.rounds_finish = RoundsFinish()

        m.d.comb += [
            [
                right.state_i.eq(left.state_o)
                for [left, right] in window(double_rounds, 2)
            ],
            rounds_finish.old_state_i.eq(previous_state_r),
            rounds_finish.new_state_i.eq(double_rounds[-1].state_o),
        ]

        m.d.comb += [
            double_rounds[0].state_i.eq(
                Mux(is_first_stage, self.state_i, intermediate_r)
            ),
            self.done_o.eq(is_last_stage),
            self.state_o.eq(Mux(is_last_stage, rounds_finish.state_o, 0)),
        ]

        with m.If(self.enabled_i):
            with m.If(is_first_stage):
                m.d.sync += previous_state_r.eq(self.state_i)

            with m.If(~is_last_stage):
                m.d.sync += [
                    intermediate_r.eq(double_rounds[-1].state_o),
                    stage_r.eq(stage_r + 1),
                ]

        return m


class DoubleRound(Elaboratable):
    """ChaCha double-round as combinational logic"""

    def __init__(self):
        # Input ChaCha state
        self.state_i = ChaChaState()
        # Output ChaCha state
        self.state_o = ChaChaState()

    def elaborate(self, _: Platform) -> Module:
        m = Module()

        quarter_rounds = [
            QuarterRound(0, 4, 8, 12),
            QuarterRound(1, 5, 9, 13),
            QuarterRound(2, 6, 10, 14),
            QuarterRound(3, 7, 11, 15),
            QuarterRound(0, 5, 10, 15),
            QuarterRound(1, 6, 11, 12),
            QuarterRound(2, 7, 8, 13),
            QuarterRound(3, 4, 9, 14),
        ]
        m.submodules += quarter_rounds

        m.d.comb += [
            self.state_o.eq(quarter_rounds[-1].state_o),
            [
                right.state_i.eq(left.state_o)
                for [left, right] in window(quarter_rounds, 2)
            ],
            quarter_rounds[0].state_i.eq(self.state_i),
        ]

        return m


class QuarterRound(Elaboratable):
    """ChaCha quarter-round as combinational logic"""

    def __init__(self, a: int, b: int, c: int, d: int):
        assert all(
            STATE_WORDS >= x >= 0 for x in [a, b, c, d]
        ), "invalid quarter-round parameters"

        self.abcd = a, b, c, d

        # Input ChaCha state
        self.state_i = ChaChaState()
        # Output ChaCha state
        self.state_o = ChaChaState()

    def elaborate(self, _: Platform) -> Module:
        m = Module()

        a, b, c, d = self.abcd

        # the following variables are named after the parameters of the quarter-round
        a0 = (_w(self.state_i, a) + _w(self.state_i, b))[0:32]
        d0 = _w(self.state_i, d) ^ a0
        d1 = bit_rotate(d0, 16)

        c0 = (_w(self.state_i, c) + d1)[0:32]
        b0 = _w(self.state_i, b) ^ c0
        b1 = bit_rotate(b0, 12)

        a1 = (a0 + b1)[0:32]
        d2 = d1 ^ a1
        d3 = bit_rotate(d2, 8)

        c1 = (c0 + d3)[0:32]
        b2 = b1 ^ c1
        b3 = bit_rotate(b2, 7)

        m.d.comb += [
            self.state_o.eq(self.state_i),
            _w(self.state_o, a).eq(a1),
            _w(self.state_o, b).eq(b3),
            _w(self.state_o, c).eq(c1),
            _w(self.state_o, d).eq(d3),
        ]

        return m


class RoundsFinish(Elaboratable):
    """Finishes a ChaCha round"""

    def __init__(self):
        # Previous ChaCha state
        self.old_state_i = ChaChaState()
        # New ChaCha state after rounds
        self.new_state_i = ChaChaState()
        # Output ChaCha state
        self.state_o = ChaChaState()

    def elaborate(self, _: Platform) -> Module:
        m = Module()

        m.d.comb += [
            _w(self.state_o, n).eq(_w(self.old_state_i, n) + _w(self.new_state_i, n))
            for n in range(STATE_WORDS)
        ]

        return m
