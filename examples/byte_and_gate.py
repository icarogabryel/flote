from pathlib import Path

from flote import elaborate_file

BASE_DIR = Path(__file__).parent.parent
byte_and_gate = elaborate_file(BASE_DIR / "examples" / "ByteAndGate.ft")

byte_and_gate.update({"a": "00000000", "b": "00000000"})
byte_and_gate.wait(10)

byte_and_gate.update({"a": "11111111", "b": "00000000"})
byte_and_gate.wait(10)

byte_and_gate.update({"a": "11111111", "b": "11111111"})
byte_and_gate.wait(10)

byte_and_gate.update({"a": "10101010", "b": "11110000"})
byte_and_gate.wait(10)

byte_and_gate.save_vcd("ByteAndGate.vcd")
