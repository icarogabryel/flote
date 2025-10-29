from pathlib import Path

from flote import elaborate_from_file

BASE_DIR = Path(__file__).parent.parent.parent
TESTS_DIR = BASE_DIR / 'tests'

inverter = elaborate_from_file(
    TESTS_DIR / 'duts' / 'SelInverter.ft'
)

print(inverter)

inverter.update({'a': '0', 's': '0'})
inverter.wait(10)
inverter.update({'a': '0', 's': '1'})
inverter.wait(10)
inverter.update({'a': '1', 's': '0'})
inverter.wait(10)
inverter.update({'a': '1', 's': '1'})
inverter.wait(10)

inverter.save_vcd('SelInverter.vcd')
