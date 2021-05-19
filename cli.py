from argparse import ArgumentParser

from nmigen import *
from nmigen.cli import main_runner, main_parser

from croc.chacha import StagedChaChaRounds, Rounds


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--name", help="Output module name")
    parser.add_argument(
        "--rounds",
        type=Rounds,
        default="20",
        choices=list(Rounds),
        help="amount of total rounds to perform",
    )
    parser.add_argument(
        "--rounds-per-cycle",
        type=int,
        default="2",
        help="amount of rounds to perform per cycle (2 min, `--rounds` max, mod 2)",
    )
    main_parser(parser)

    args = parser.parse_args()

    top = StagedChaChaRounds(args.rounds, args.rounds_per_cycle)

    main_runner(
        parser,
        args,
        top,
        ports=[
            top.state_i,
            top.state_o,
            top.done_o,
        ],
        name=args.name,
    )
