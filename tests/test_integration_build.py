"""This file test de constructions of a RS Latch using the Flote library."""
from flote.model.component import Component, BitBus
from pathlib import Path


FILE_DIR = Path(__file__).resolve().parent


latch = Component('latch')

set = BitBus()
rst = BitBus()

q = BitBus()
q.assignment = lambda: not (
    latch.bus_dict['rst'].value or latch.bus_dict['i1'].value
)
q.sensitivity_list = ['rst', 'i1']

not_q = BitBus()
not_q.assignment = lambda: not (
    latch.bus_dict['set'].value or latch.bus_dict['i2'].value
)
not_q.sensitivity_list = ['set', 'i2']

i1 = BitBus()
i1.assignment = lambda: latch.bus_dict['not_q'].value
i1.sensitivity_list = ['not_q']

i2 = BitBus()
i2.assignment = lambda: latch.bus_dict['q'].value
i2.sensitivity_list = ['q']

latch.inputs = ['set', 'rst']

latch.bus_dict = {
    'set': set,
    'rst': rst,
    'q': q,
    'not_q': not_q,
    'i1': i1,
    'i2': i2
}

latch.make_influence_list()

latch.stimulate({'set': '0', 'rst': '1'})
latch.wait(1)
latch.stimulate({'set': '0', 'rst': '0'})
latch.wait(1)
latch.stimulate({'set': '1', 'rst': '0'})
latch.wait(1)
latch.stimulate({'set': '0', 'rst': '0'})
latch.wait(1)
latch.stimulate({'set': '1', 'rst': '0'})
latch.wait(1)
latch.stimulate({'set': '0', 'rst': '0'})
latch.wait(1)
latch.stimulate({'set': '0', 'rst': '1'})
latch.wait(1)
latch.stimulate({'set': '0', 'rst': '0'})
latch.wait(1)

latch.save_vcd(FILE_DIR / 'waves/RsLatch (fw).vcd')
