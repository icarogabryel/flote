from pathlib import Path

from flote import elaborate_file

BASE_DIR = Path(__file__).parent.parent
full_adder = elaborate_file(BASE_DIR / "sandbox" / "duts" / "FullAdder.ft")

full_adder.update({"a": "0", "b": "0", "cin": "0"})
full_adder.wait(10)

full_adder.update({"a": "0", "b": "0", "cin": "1"})
full_adder.wait(10)

full_adder.update({"a": "0", "b": "1", "cin": "0"})
full_adder.wait(10)

full_adder.update({"a": "0", "b": "1", "cin": "1"})
full_adder.wait(10)

full_adder.update({"a": "1", "b": "0", "cin": "0"})
full_adder.wait(10)

full_adder.update({"a": "1", "b": "0", "cin": "1"})
full_adder.wait(10)

full_adder.update({"a": "1", "b": "1", "cin": "0"})
full_adder.wait(10)

full_adder.update({"a": "1", "b": "1", "cin": "1"})
full_adder.wait(10)

full_adder.save_vcd("FullAdder.vcd")
