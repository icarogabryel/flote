from pathlib import Path

from flote import elaborate_file

BASE_DIR = Path(__file__).parent.parent
rs_latch = elaborate_file(BASE_DIR / "sandbox" / "duts" / "RsLatch.ft")

rs_latch.update({"set": "0", "rst": "1"})
rs_latch.wait(1)

rs_latch.update({"set": "0", "rst": "0"})
rs_latch.wait(1)

rs_latch.update({"set": "1", "rst": "0"})
rs_latch.wait(1)

rs_latch.update({"set": "0", "rst": "0"})
rs_latch.wait(1)

rs_latch.update({"set": "1", "rst": "0"})
rs_latch.wait(1)

rs_latch.update({"set": "0", "rst": "0"})
rs_latch.wait(1)

rs_latch.update({"set": "0", "rst": "1"})
rs_latch.wait(1)

rs_latch.update({"set": "0", "rst": "0"})
rs_latch.wait(1)

rs_latch.update({"set": "1", "rst": "0"})
rs_latch.wait(1)

rs_latch.update({"set": "0", "rst": "0"})
rs_latch.wait(1)

rs_latch.update({"set": "0", "rst": "1"})
rs_latch.wait(1)

rs_latch.update({"set": "0", "rst": "0"})
rs_latch.wait(1)

rs_latch.save_vcd("RsLatch.vcd")
