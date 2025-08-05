import flote as ft
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent


def test():
    half_adder = ft.elaborate_from_file(
        BASE_DIR / 'tests/examples/HalfAdder.ft'
    )

    half_adder.stimulate({'a': '0', 'b': '0'})
    half_adder.wait(10)

    print(half_adder)

    half_adder.stimulate({'a': '0', 'b': '1'})
    half_adder.wait(10)

    print(half_adder)

    half_adder.stimulate({'a': '1', 'b': '0'})
    half_adder.wait(10)

    print(half_adder)

    half_adder.stimulate({'a': '1', 'b': '1'})
    half_adder.wait(10)

    print(half_adder)

    # half_adder.save_vcd(FILE_DIR / 'waves/HalfAdder.vcd')


if __name__ == '__main__':
    test()
