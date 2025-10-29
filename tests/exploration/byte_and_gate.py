from pathlib import Path

from flote import elaborate_from_file

BASE_DIR = Path(__file__).parent.parent.parent
TESTS_DIR = BASE_DIR / 'tests'

byte_and_gate = elaborate_from_file(
    TESTS_DIR / 'duts' / 'ByteAndGate.ft'
)

print(byte_and_gate)

byte_and_gate.update({'a': '00000000', 'b': '00000000'})
byte_and_gate.wait(10)

byte_and_gate.update({'a': '11111111', 'b': '00000000'})
byte_and_gate.wait(10)

byte_and_gate.update({'a': '11111111', 'b': '11111111'})
byte_and_gate.wait(10)
byte_and_gate.update({'a': '10101010', 'b': '11001100'})
byte_and_gate.wait(10)

byte_and_gate.save_vcd('ByteAndGate.vcd')
