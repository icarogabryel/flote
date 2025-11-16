from pathlib import Path

import flote as ft
from flote import Component, Bus, BitBusValue
BASE_DIR = Path(__file__).parent.parent.parent
TESTS_DIR = BASE_DIR / 'tests'

comp = Component(
    '@teste',
    [
        Bus(
            'xx',
            1,
            lambda: BitBusValue([True]),
            initial_value=BitBusValue([True]),
            vcd_repr_func=lambda val: ''.join(['1' if bit else '0' for bit in val.raw_value])
        ),
    ]
)


def test():
    half_adder = ft.elaborate_file(
        TESTS_DIR / 'duts' / 'HalfAdder.ft',
        hls_components=[comp]
    )
    print(half_adder)

    half_adder.update({'a': '0', 'b': '0'})
    half_adder.wait(10)

    print(half_adder)

    half_adder.update({'a': '0', 'b': '1'})
    half_adder.wait(10)

    print(half_adder)

    half_adder.update({'a': '1', 'b': '0'})
    half_adder.wait(10)

    print(half_adder)

    half_adder.update({'a': '1', 'b': '1'})
    half_adder.wait(10)

    print(half_adder)

    half_adder.save_vcd('HalfAdder.vcd')


if __name__ == '__main__':
    test()
