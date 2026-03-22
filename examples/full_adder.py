from pathlib import Path

from flote import elaborate_file

BASE_DIR = Path(__file__).parent.parent


def test():
    full_adder = elaborate_file(
        BASE_DIR / 'examples' / 'FullAdder.ft',
    )

    # Test all 8 combinations of 3 input bits
    full_adder.update({'a': '0', 'b': '0', 'cin': '0'})
    full_adder.wait(10)

    full_adder.update({'a': '0', 'b': '0', 'cin': '1'})
    full_adder.wait(10)

    full_adder.update({'a': '0', 'b': '1', 'cin': '0'})
    full_adder.wait(10)

    full_adder.update({'a': '0', 'b': '1', 'cin': '1'})
    full_adder.wait(10)

    full_adder.update({'a': '1', 'b': '0', 'cin': '0'})
    full_adder.wait(10)

    full_adder.update({'a': '1', 'b': '0', 'cin': '1'})
    full_adder.wait(10)

    full_adder.update({'a': '1', 'b': '1', 'cin': '0'})
    full_adder.wait(10)

    full_adder.update({'a': '1', 'b': '1', 'cin': '1'})
    full_adder.wait(10)

    full_adder.save_vcd('FullAdder.vcd')


if __name__ == '__main__':
    test()
