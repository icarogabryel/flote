from pathlib import Path

import flote as ft

BASE_DIR = Path(__file__).parent.parent.parent
TESTS_DIR = BASE_DIR / 'tests'


def test():
    full_adder = ft.elaborate_file(
        TESTS_DIR / 'duts' / 'FullAdder.ft',
    )
    print(full_adder)

    # Test all 8 combinations of 3 input bits
    full_adder.update({'a': '0', 'b': '0', 'cin': '0'})
    full_adder.wait(10)
    print(full_adder)

    full_adder.update({'a': '0', 'b': '0', 'cin': '1'})
    full_adder.wait(10)
    print(full_adder)

    full_adder.update({'a': '0', 'b': '1', 'cin': '0'})
    full_adder.wait(10)
    print(full_adder)

    full_adder.update({'a': '0', 'b': '1', 'cin': '1'})
    full_adder.wait(10)
    print(full_adder)

    full_adder.update({'a': '1', 'b': '0', 'cin': '0'})
    full_adder.wait(10)
    print(full_adder)

    full_adder.update({'a': '1', 'b': '0', 'cin': '1'})
    full_adder.wait(10)
    print(full_adder)

    full_adder.update({'a': '1', 'b': '1', 'cin': '0'})
    full_adder.wait(10)
    print(full_adder)

    full_adder.update({'a': '1', 'b': '1', 'cin': '1'})
    full_adder.wait(10)
    print(full_adder)

    full_adder.save_vcd('FullAdder.vcd')


if __name__ == '__main__':
    test()
