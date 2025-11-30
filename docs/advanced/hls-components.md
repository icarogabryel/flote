# HLS Components

**HLS (High-Level Synthesis) Components** allow you to define circuit behavior using Python instead of gate-level Flote code. This is useful for complex logic that would be tedious to implement with basic gates.

## What is HLS?

HLS lets you:

- Define components in Python with complex logic
- Use Python's control flow (if/else, loops)
- Perform arithmetic and data manipulation
- Integrate Python functions into Flote circuits

## When to Use HLS

**Use HLS when:**

- Logic is complex and tedious in gates (counters, ALUs, state machines)
- You need arithmetic operations
- You want to use Python libraries
- Prototyping complex behavior quickly

**Use native Flote when:**

- Circuit is simple (basic gates, multiplexers)
- You want to see gate-level structure
- Teaching/learning digital design
- Performance is critical

## HLS API Overview

Two main classes define HLS components:

### Bus Class

Represents a signal (input, output, or internal):

```python
from flote.hls import Bus

bus = Bus(
    id_="signal_name",        # Signal name
    size=8,                    # Bit width
    assignment=None,           # Logic expression (optional)
    initial_value=0,           # Initial value
    is_input=False,            # Is this an input?
    influence_list=[],         # Signals this depends on
    vcd_repr_func=lambda x: str(x)  # VCD representation
)
```

### Component Class

Groups buses into a reusable component:

```python
from flote.hls import Component

component = Component(
    id_="@ComponentName",      # Must start with @
    buses=[bus1, bus2, bus3]   # List of Bus objects
)
```

## Creating an HLS Component

### Step 1: Import HLS Module

```python
from flote.hls import Bus, Component
```

### Step 2: Define Logic Function

Create a function that implements the component's behavior:

```python
def counter_logic(buses, clock, reset):
    """Increment counter on clock edge, reset to 0 on reset."""
    count = buses['count']

    if reset == '1':
        return 0
    elif clock == '1':
        return (count.value + 1) % (2 ** count.size)
    else:
        return count.value
```

### Step 3: Create Buses

Define input and output buses:

```python
# Inputs
clock = Bus(
    id_="clock",
    size=1,
    is_input=True
)

reset = Bus(
    id_="reset",
    size=1,
    is_input=True
)

# Output with logic
count = Bus(
    id_="count",
    size=8,
    assignment=counter_logic,
    initial_value=0,
    influence_list=[clock, reset]
)
```

### Step 4: Create Component

Bundle buses into a component:

```python
counter_component = Component(
    id_="@Counter",
    buses=[clock, reset, count]
)
```

## Complete Example: 4-bit Counter

```python
# counter.py
from flote.hls import Bus, Component

def counter_logic(buses, clock, reset):
    """4-bit counter with reset."""
    count = buses['count']

    if reset == '1':
        return 0
    elif clock == '1':
        # Increment and wrap at 16 (2^4)
        return (count.value + 1) % 16
    else:
        return count.value

# Create buses
clock = Bus(id_="clock", size=1, is_input=True)
reset = Bus(id_="reset", size=1, is_input=True)
count = Bus(
    id_="count",
    size=4,
    assignment=counter_logic,
    initial_value=0,
    influence_list=[clock, reset]
)

# Create component
Counter = Component(id_="@Counter", buses=[clock, reset, count])
```

## Using HLS Components in Flote

### Step 1: Create Flote File

```flote
// top.ft
main comp Top {
    in bit clk;
    in bit rst;
    out bit count[4];

    sub @Counter as cnt;

    cnt.clock = clk;
    cnt.reset = rst;
    count = cnt.count;
}
```

### Step 2: Load Python Component

```python
# simulate.py
import flote as ft
from counter import Counter

# Elaborate with HLS component
top = ft.elaborate_file('top.ft', hls_components=[Counter])

# Simulate
top.update({'clk': '0', 'rst': '1'})
top.wait(10)  # Reset

top.update({'rst': '0'})  # Release reset

for i in range(20):
    top.update({'clk': '1'})
    top.wait(10)
    top.update({'clk': '0'})
    top.wait(10)

    print(f"Count: {top.read('count')}")

top.save_vcd('counter.vcd')
```

## Bus Properties

### Essential Properties

```python
bus = Bus(
    id_="name",           # Required: signal identifier
    size=8,               # Required: bit width
    assignment=func,      # Optional: logic function
    initial_value=0,      # Optional: starting value
    is_input=False,       # Optional: input flag
    influence_list=[],    # Optional: dependencies
    vcd_repr_func=str     # Optional: VCD formatting
)
```

### id_ (Identifier)

The signal name as it appears in Flote code:

```python
clock = Bus(id_="clock", size=1, is_input=True)
# In Flote: cnt.clock
```

### size (Bit Width)

Number of bits in the signal:

```python
bit_signal = Bus(id_="bit", size=1, ...)
byte_signal = Bus(id_="byte", size=8, ...)
word_signal = Bus(id_="word", size=32, ...)
```

### assignment (Logic Function)

Function that computes the signal's value:

```python
def my_logic(buses, input1, input2):
    return input1 & input2  # AND operation

output = Bus(
    id_="output",
    size=1,
    assignment=my_logic,
    influence_list=[input1_bus, input2_bus]
)
```

**Function signature:**
- First parameter: `buses` dictionary
- Remaining parameters: values of influence_list buses
- Return: integer value for the bus

### initial_value

Starting value before any updates:

```python
counter = Bus(
    id_="counter",
    size=8,
    initial_value=0,  # Starts at 0
    ...
)
```

### is_input

Mark as input (values provided externally):

```python
input_bus = Bus(id_="input", size=1, is_input=True)
```

Inputs don't have assignment functions.

### influence_list

Buses that this signal depends on:

```python
sum_bus = Bus(
    id_="sum",
    size=8,
    assignment=add_logic,
    influence_list=[a_bus, b_bus]  # sum depends on a and b
)
```

The simulator calls `assignment` when any influence changes.

### vcd_repr_func

Custom formatting for VCD output:

```python
# Default: decimal string
Bus(id_="count", size=8, vcd_repr_func=lambda x: str(x))

# Hexadecimal
Bus(id_="addr", size=16, vcd_repr_func=lambda x: hex(x))

# Binary
Bus(id_="flags", size=4, vcd_repr_func=lambda x: bin(x)[2:].zfill(4))
```

## Logic Functions

### Function Signature

```python
def logic_function(buses, *influence_values):
    # buses: dict mapping id_ -> Bus object
    # influence_values: current values of influence_list buses
    # return: new integer value
    pass
```

### Accessing Bus Values

```python
def example_logic(buses, input1_val, input2_val):
    # Access by dictionary
    my_bus = buses['my_bus']
    current_value = my_bus.value

    # Use influence values (recommended)
    result = input1_val & input2_val

    return result
```

### State Management

HLS functions can maintain state using bus values:

```python
def stateful_logic(buses, trigger):
    state_bus = buses['state']

    if trigger == 1:
        # Transition to next state
        return (state_bus.value + 1) % 4
    else:
        # Keep current state
        return state_bus.value
```

## Advanced Example: ALU

```python
# alu.py
from flote.hls import Bus, Component

def alu_logic(buses, a, b, op):
    """4-bit ALU with multiple operations."""
    # op: 00=ADD, 01=SUB, 10=AND, 11=OR

    if op == 0b00:  # ADD
        return (a + b) % 16
    elif op == 0b01:  # SUB
        return (a - b) % 16
    elif op == 0b10:  # AND
        return a & b
    else:  # OR
        return a | b

# Create buses
a = Bus(id_="a", size=4, is_input=True)
b = Bus(id_="b", size=4, is_input=True)
op = Bus(id_="op", size=2, is_input=True)

result = Bus(
    id_="result",
    size=4,
    assignment=alu_logic,
    influence_list=[a, b, op]
)

ALU = Component(id_="@ALU", buses=[a, b, op, result])
```

**Using the ALU:**

```python
import flote as ft
from alu import ALU

# Flote file using ALU
top = ft.elaborate_file('top.ft', hls_components=[ALU])

# Test ADD
top.update({'a': '0101', 'b': '0011', 'op': '00'})
top.wait(10)
print(f"5 + 3 = {int(top.read('result'), 2)}")  # 8

# Test AND
top.update({'op': '10'})
top.wait(10)
print(f"5 & 3 = {int(top.read('result'), 2)}")  # 1
```

## Best Practices

### Naming Conventions

```python
# Component names start with @
Counter = Component(id_="@Counter", ...)
ALU = Component(id_="@ALU", ...)

# Bus names match Flote conventions
clock = Bus(id_="clock", ...)
data_in = Bus(id_="data_in", ...)
```

### Influence Lists

Always include all dependencies:

```python
# Wrong - missing dependency
result = Bus(
    id_="result",
    assignment=lambda buses, a: a & buses['b'].value,  # Uses b
    influence_list=[a_bus]  # But b not in list!
)

# Correct
result = Bus(
    id_="result",
    assignment=lambda buses, a, b: a & b,
    influence_list=[a_bus, b_bus]  # Both listed
)
```

### Error Handling

Handle edge cases in logic functions:

```python
def safe_divider(buses, dividend, divisor):
    if divisor == 0:
        return 0  # Or raise error
    return dividend // divisor
```

### Testing

Test HLS components standalone before integrating:

```python
# test_counter.py
from counter import Counter

# Create test instance
from flote.backend.python.core import Bus as SimBus

test_buses = {
    'clock': SimBus(Counter.buses[0]),
    'reset': SimBus(Counter.buses[1]),
    'count': SimBus(Counter.buses[2])
}

# Test logic directly
result = counter_logic(test_buses, 1, 0)  # clock=1, reset=0
assert result == 1
```

## Limitations

### No Combinational Loops

HLS components can't create combinational loops:

```python
# Wrong - circular dependency
a = Bus(id_="a", assignment=lambda b, b: not b, influence_list=[b])
b = Bus(id_="b", assignment=lambda b, a: not a, influence_list=[a])
```

Use feedback in Flote instead:

```flote
comp Latch {
    in bit set;
    in bit reset;
    out bit q;
    out bit q_bar;

    q = reset nor q_bar;
    q_bar = set nor q;
}
```

### Integer Values Only

Buses hold integer values, not floating-point:

```python
# Works
value = 42

# Doesn't work
value = 3.14  # Will be truncated or cause error
```

### Size Constraints

Values must fit in the specified bit width:

```python
bus = Bus(id_="small", size=4, ...)  # Max value: 15
# Assign 16 -> wraps to 0
# Assign 17 -> wraps to 1
```

Use modulo to enforce:

```python
def safe_logic(buses, input_val):
    bus_size = buses['output'].size
    return input_val % (2 ** bus_size)
```

## Next Steps

- **[Testbenches](testbenches.md)** - Test HLS components
- **[Examples: Full Adder](../examples/full-adder.md)** - See HLS in action
- **[API Reference: HLS](../api/hls-api.md)** - Complete API documentation

---

*HLS bridges Python's expressiveness with Flote's hardware simulation. Use it to build complex components quickly!*
