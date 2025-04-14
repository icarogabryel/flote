import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import flote as ft

latch = ft.Component('latch')

latch.inputs = ['set', 'rst']

set = ft.BitBus()
rst = ft.BitBus()

q = ft.BitBus()
q.assignment = lambda: not (latch.bus_dict['rst'].value or latch.bus_dict['i1'].value)
q.sensitivity_list = ['rst', 'i1']

not_q = ft.BitBus()
not_q.assignment = lambda: not (latch.bus_dict['set'].value or latch.bus_dict['i2'].value)
not_q.sensitivity_list = ['set', 'i2']

i1 = ft.BitBus()
i1.assignment = lambda: latch.bus_dict['not_q'].value
i1.sensitivity_list = ['not_q']

i2 = ft.BitBus()
i2.assignment = lambda: latch.bus_dict['q'].value
i2.sensitivity_list = ['q']

latch.bus_dict = {
    'set': set,
    'rst': rst,
    'q': q,
    'not_q': not_q,
    'i1': i1,
    'i2': i2
}

latch.make_influence_list()

latch.stimulate({'set': False, 'rst': True})
latch.wait(1)
latch.stimulate({'set': False, 'rst': False})
latch.wait(1)
latch.stimulate({'set': True, 'rst': False})
latch.wait(1)
latch.stimulate({'set': False, 'rst': False})
latch.wait(1)
latch.stimulate({'set': True, 'rst': False})
latch.wait(1)
latch.stimulate({'set': False, 'rst': False})
latch.wait(1)
latch.stimulate({'set': False, 'rst': True})
latch.wait(1)
latch.stimulate({'set': False, 'rst': False})
latch.wait(1)

result = latch.dump_vcd()
print(result)

with open ('waves/RSLatch_FW.vcd', 'w') as f:
    f.write(result)

