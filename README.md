# croc

ChaCha stream cipher modules written in Python, described using
[Amaranth](https://github.com/amaranth-lang/amaranth/).

## Disclaimer

Do not use unreviewed cryptographic algorithm implementations in your applications.
Croc is written as a learning project and has not gone under any reviewing process.

## Setup, tests & RTL generation

Run `setup.py` with Python 3 to install dependencies

`python3 setup.py install`

Run tests with pytest

`pytest croc/croc/tests`

List generation options

`python3 cli.py --help`

Generate RTL using the `cli.py` script

`python3 cli.py --name chacha20_2rpc --rounds 20 --rounds-per-cycle 2 generate out.v`

## Todo

Better testing & more test data, streaming & mixing logic, state initialization, ...

## License

Copyright (c) 2021 Arthur M.

Croc is licensed under the GNU General Public License version 3 or later, see
[LICENSE](./LICENSE).
