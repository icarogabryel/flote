from flote.simulation.backend.python.component import Component, Circuit
from flote.simulation.backend.python.busses import BitBus
from flote.simulation.backend.python.expr_nodes import And, Not, Or, BusRef


mux = Component()

a = BitBus()
b = BitBus()
s = BitBus()
w1 = BitBus()
w2 = BitBus()
y = BitBus()

w1.set_assignment(And(BusRef(a), Not(BusRef(s))))
w2.set_assignment(And(BusRef(b), BusRef(s)))
y.set_assignment(Or(BusRef(w1), BusRef(w2)))

mux.add_busses("mux", {
    "a": a,
    "b": b,
    "s": s,
    "w1": w1,
    "w2": w2,
    "y": y
})

inverter = Component()
a1 = BitBus()
s1 = BitBus()
y1 = BitBus()

inverter.add_component("inverter", mux)

a.set_assignment(BusRef(a1))
b.set_assignment(Not(BusRef(a1)))
s.set_assignment(BusRef(s1))
y1.set_assignment(BusRef(y))

inverter.add_busses("inverter", {
    "a1": a1,
    "s1": s1,
    "y1": y1
})

cric = Circuit(inverter.busses)
cric.inputs = ["inverter.a1", "inverter.s1"]
cric.stabilize()

print(cric)

cric.update_signals({
    "inverter.a1": "1",
    "inverter.s1": "0"
})

print(cric)
cric.update_signals({
    "inverter.a1": "0",
    "inverter.s1": "1"
})

print(cric)
cric.update_signals({
    "inverter.a1": "1",
    "inverter.s1": "1"
})

print(cric)
