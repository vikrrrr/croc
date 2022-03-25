from croc.chacha import QuarterRound, DoubleRound, StagedChaChaRounds, Rounds
from amaranth import *
from amaranth.sim import *

from .chacha_reference import (
    quarter_round,
    double_round,
    chacha,
    state_to_int,
    int_to_state,
)


def test_staged_rounds():
    TEST_DATA = [
        # TODO add more test data for the staged rounds module
        ([0 for _ in range(16)], [0 for _ in range(16)], Rounds.REDUCED_12, 2),
        (
            [n for n in range(16)],
            [
                0x48E90081,
                0xF390518D,
                0x224B1424,
                0x0E74BDBA,
                0x888688D6,
                0x108E96F9,
                0x1DE13D88,
                0x71BC3E2F,
                0x281FF78E,
                0x66900EC6,
                0xD3BFBE8C,
                0x815F33F9,
                0x665AAEC0,
                0x7485A172,
                0x61889CF5,
                0x94255E2F,
            ],
            Rounds.FULL_20,
            2,
        ),
    ]

    for input_state, expected_output, n_rounds, rounds_per_cycle in TEST_DATA:
        dut = StagedChaChaRounds(n_rounds, rounds_per_cycle)

        def process():
            yield dut.enabled_i.eq(True)
            yield dut.state_i.eq(state_to_int(input_state))

            cycles_taken = 0

            while not (yield dut.done_o):
                cycles_taken += 1
                yield Tick()

            actual_output = int_to_state((yield dut.state_o))
            reference_output = chacha(input_state.copy(), Rounds.get_n_rounds(n_rounds))

            assert cycles_taken == dut.total_stages
            assert actual_output == reference_output
            assert actual_output == expected_output

        sim = Simulator(dut)
        sim.add_clock(1e-9)
        sim.add_process(process)
        sim.run()


def test_double_round():
    TEST_DATA = [
        # TODO add more test data for the double round module
        (
            [n for n in range(16)],
            [
                0xA9295C6A,
                0xB471BE7A,
                0x38E65EC4,
                0x74348B87,
                0xF1AD76C6,
                0x7B44627B,
                0x946682B0,
                0xF12F4910,
                0xD7E22F80,
                0x3232DDD4,
                0xB5B3B74D,
                0xC0240444,
                0xC8A5DE45,
                0xE417E1D3,
                0x1A392478,
                0x983C4EBF,
            ],
        ),
    ]

    for input_state, expected_output in TEST_DATA:
        dut = DoubleRound()

        def process():
            yield dut.state_i.eq(state_to_int(input_state))
            yield Settle()

            actual_output = int_to_state((yield dut.state_o))
            reference_output = double_round(input_state.copy())

            assert actual_output == expected_output
            assert actual_output == reference_output

        sim = Simulator(dut)
        sim.add_process(process)
        sim.run()


def test_quarter_round():
    TEST_DATA = [
        # TODO add more test data for the quarter round module
        (
            [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            ],
            [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            ],
            0,
            4,
            8,
            12,
        ),
        (
            [
                0x0000_0001,
                0x0000_0002,
                0x0000_0003,
                0x0000_0004,
                0x0000_0001,
                0x0000_0002,
                0x0000_0003,
                0x0000_0004,
                0x0000_0001,
                0x0000_0002,
                0x0000_0003,
                0x0000_0004,
                0x0000_0001,
                0x0000_0002,
                0x0000_0003,
                0x0000_0004,
            ],
            [
                0x3000_0002,
                0x0000_0002,
                0x0000_0003,
                0x0000_0004,
                0x8181_1899,
                0x0000_0002,
                0x0000_0003,
                0x0000_0004,
                0x0303_0231,
                0x0000_0002,
                0x0000_0003,
                0x0000_0004,
                0x0300_0230,
                0x0000_0002,
                0x0000_0003,
                0x0000_0004,
            ],
            0,
            4,
            8,
            12,
        ),
    ]

    for input_state, expected_output, a, b, c, d in TEST_DATA:
        dut = QuarterRound(a, b, c, d)

        def process():
            yield dut.state_i.eq(state_to_int(input_state))
            yield Settle()

            actual_output = int_to_state((yield dut.state_o))
            reference_output = quarter_round(input_state.copy(), a, b, c, d)

            assert actual_output == expected_output
            assert actual_output == reference_output

        sim = Simulator(dut)
        sim.add_process(process)
        sim.run()
