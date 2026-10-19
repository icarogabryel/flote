from pathlib import Path

from flote import elaborate_file

BASE_DIR = Path(__file__).parent.parent
half_adder = elaborate_file(BASE_DIR / "sandbox" / "duts" / "HalfAdder.ft")

half_adder.update({"a": "0", "b": "0"})
half_adder.wait(10)

half_adder.update({"a": "0", "b": "1"})
half_adder.wait(10)

half_adder.update({"a": "1", "b": "0"})
half_adder.wait(10)

half_adder.update({"a": "1", "b": "1"})
half_adder.wait(10)

half_adder.save_vcd("HalfAdder.vcd")
