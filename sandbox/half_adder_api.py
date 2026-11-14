from flote import BitBus, Component, TestBench, expression

a = BitBus()
a.id = "a"
b = BitBus()
b.id = "b"

sum = BitBus()
sum.id = "sum"
sum.assignment = expression.Xor(
    expression.Ref(a, None, None), expression.Ref(b, None, None)
)
sum.influence_list = [a, b]
carry = BitBus()
carry.id = "carry"
carry.assignment = expression.And(
    expression.Ref(a, None, None), expression.Ref(b, None, None)
)
carry.influence_list = [a, b]

ha = Component("half_adder")
ha.buses = {"a": a, "b": b, "sum": sum, "carry": carry}

tb = TestBench(ha)

signals_grid = [
    {"a": "0", "b": "0"},
    {"a": "0", "b": "1"},
    {"a": "1", "b": "0"},
    {"a": "1", "b": "1"},
]

for signals in signals_grid:
    tb.update(signals)
    tb.wait(10)
    print(tb.component.get_values())
