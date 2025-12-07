# Quick Start: Building Your First Circuit

This tutorial will walk you through creating a complete digital circuit in Flote, from writing the HDL code to simulating and visualizing the results.

## What We'll Build

We'll create a **Half Adder** - a fundamental digital circuit that adds two 1-bit numbers, producing a sum and carry bit.

**Truth Table:**

| A | B | Sum | Carry |
|---|---|-----|-------|
| 0 | 0 |  0  |   0   |
| 0 | 1 |  1  |   0   |
| 1 | 0 |  1  |   0   |
| 1 | 1 |  0  |   1   |

## Step 1: Create the Circuit

Create a new file called `HalfAdder.ft`:

```flote
comp HalfAdder {
    in bit a;
    in bit b;

    out bit sum = a xor b;
    out bit carry = a and b;
}
```

Let's break this down:

- `comp HalfAdder {` - Define a component named HalfAdder
- `in bit a;` - Declare input signal 'a' (1 bit)
- `in bit b;` - Declare input signal 'b' (1 bit)
- `out bit sum = a xor b;` - Output 'sum' is XOR of inputs
- `out bit carry = a and b;` - Output 'carry' is AND of inputs
- `}` - End component definition

!!! tip "Concise Syntax"
    Notice how we can declare outputs with their logic in a single line! No separate `architecture` block like VHDL.

## Step 2: Create a Testbench

Create a file called `test_half_adder.py`:

```python
import flote as ft

# Elaborate (compile) the circuit
half_adder = ft.elaborate_file('HalfAdder.ft')

# Test case 1: 0 + 0 = 0
print("Testing 0 + 0")
half_adder.update({'a': '0', 'b': '0'})
half_adder.wait(10)
print(f"  Sum: {half_adder.component.busses['sum'].value}")
print(f"  Carry: {half_adder.component.busses['carry'].value}")

# Test case 2: 0 + 1 = 1
print("\nTesting 0 + 1")
half_adder.update({'a': '0', 'b': '1'})
half_adder.wait(10)
print(f"  Sum: {half_adder.component.busses['sum'].value}")
print(f"  Carry: {half_adder.component.busses['carry'].value}")

# Test case 3: 1 + 0 = 1
print("\nTesting 1 + 0")
half_adder.update({'a': '1', 'b': '0'})
half_adder.wait(10)
print(f"  Sum: {half_adder.component.busses['sum'].value}")
print(f"  Carry: {half_adder.component.busses['carry'].value}")

# Test case 4: 1 + 1 = 10 (binary)
print("\nTesting 1 + 1")
half_adder.update({'a': '1', 'b': '1'})
half_adder.wait(10)
print(f"  Sum: {half_adder.component.busses['sum'].value}")
print(f"  Carry: {half_adder.component.busses['carry'].value}")

# Save waveform for visualization
half_adder.save_vcd('HalfAdder.vcd')
print("\nWaveform saved to HalfAdder.vcd")
```

## Step 3: Run the Simulation

Execute the testbench:

```bash
python test_half_adder.py
```

Expected output:

```
Testing 0 + 0
  Sum: 0
  Carry: 0

Testing 0 + 1
  Sum: 1
  Carry: 0

Testing 1 + 0
  Sum: 1
  Carry: 0

Testing 1 + 1
  Sum: 0
  Carry: 1

Waveform saved to HalfAdder.vcd
```

## Step 4: Visualize Waveforms

The simulation generated a `HalfAdder.vcd` file containing the signal waveforms.

### Option 1: VS Code (Recommended)

1. Install the **WaveTrace** extension in VS Code
2. Open `HalfAdder.vcd` in VS Code
3. View the beautiful waveform visualization!

### Option 2: GTKWave (Cross-platform)

1. Install [GTKWave](http://gtkwave.sourceforge.net/)
2. Open the VCD file:

   ```bash
   gtkwave HalfAdder.vcd
   ```

## Understanding the Code

### The Flote Circuit

```flote
comp HalfAdder {           // Component definition
    in bit a;              // 1-bit input
    in bit b;              // 1-bit input

    out bit sum = a xor b;    // Combinational logic
    out bit carry = a and b;  // Directly in output
}
```

Key concepts:

- **Components** are the building blocks (like `entity` in VHDL)
- **Signals** can be `in`, `out`, or internal
- **Logic** is expressed directly using gates: `and`, `or`, `xor`, `not`, etc.
- **Assignment** can happen inline with declaration

### The Python Testbench

```python
# 1. Load and compile the circuit
half_adder = ft.elaborate_file('HalfAdder.ft')

# 2. Apply input stimulus
half_adder.update({'a': '0', 'b': '1'})

# 3. Advance simulation time
half_adder.wait(10)  # Wait 10 time units

# 4. Read outputs
value = half_adder.component.busses['sum'].value

# 5. Generate waveform file
half_adder.save_vcd('HalfAdder.vcd')
```

## What's Happening Behind the Scenes?

When you run `ft.elaborate_file()`:

1. **Lexical Analysis**: Breaks code into tokens
2. **Syntax Parsing**: Validates grammar, builds Abstract Syntax Tree
3. **Semantic Analysis**: Checks types, connections, builds symbol table
4. **IR Generation**: Creates JSON intermediate representation
5. **Rendering**: Instantiates simulation objects with influence graph
6. **Ready**: Circuit is ready to simulate!

When you call `update()` and `wait()`:

1. **Update Inputs**: New values applied to input signals
2. **Propagation**: Event-driven simulation with delta cycles
3. **Stabilization**: Values propagate through logic gates
4. **Time Advance**: Simulation clock moves forward
5. **Sample**: Values recorded for VCD output

## Common Patterns

### Testing All Combinations

```python
import flote as ft

half_adder = ft.elaborate_file('HalfAdder.ft')

# Test all 4 combinations
for a in ['0', '1']:
    for b in ['0', '1']:
        half_adder.update({'a': a, 'b': b})
        half_adder.wait(10)
        print(f"{a} + {b} = {half_adder.component.busses['carry'].value}"
              f"{half_adder.component.busses['sum'].value}")

half_adder.save_vcd('HalfAdder.vcd')
```

### Using Assertions

```python
import flote as ft

half_adder = ft.elaborate_file('HalfAdder.ft')

# Test case with assertion
half_adder.update({'a': '1', 'b': '1'})
half_adder.wait(10)

assert half_adder.component.busses['sum'].value == False, "Sum should be 0"
assert half_adder.component.busses['carry'].value == True, "Carry should be 1"

print("✓ All tests passed!")
```

## Next Steps

Congratulations! You've created, simulated, and visualized your first Flote circuit.

### Learn More

- **[Basic Concepts](../guide/basic-concepts.md)** - Understand Flote fundamentals
- **[Syntax Reference](../guide/syntax-reference.md)** - Complete language reference

### Try These Challenges

1. **Full Adder**: Build a 1-bit full adder (3 inputs: a, b, cin)
2. **4-bit Adder**: Chain multiple adders together
3. **Multiplexer**: Create a 2:1 mux with a select signal
4. **Counter**: Build a simple up-counter with clock

### Join the Community

- **GitHub**: [github.com/icarogabryel/flote](https://github.com/icarogabryel/flote)
- **Report Issues**: Found a bug? Let us know!
- **Contribute**: Help improve Flote

---

*You just built a complete digital circuit in minutes. With VHDL, this would take much longer!*
