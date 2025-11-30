# Python API Reference

This page documents Flote's Python API for circuit elaboration, simulation, and testbench creation.

## Module: flote

The main module for working with Flote circuits.

```python
import flote as ft
```

## Core Functions

### elaborate_file()

Load and elaborate a Flote circuit file.

```python
circuit = ft.elaborate_file(
    filepath: str,
    hls_components: list = []
) -> Circuit
```

**Parameters:**

- `filepath` (str): Path to the `.ft` Flote file
- `hls_components` (list, optional): List of HLS Component objects to include

**Returns:**

- `Circuit`: Elaborated circuit object ready for simulation

**Example:**

```python
# Basic elaboration
circuit = ft.elaborate_file('HalfAdder.ft')

# With HLS components
from my_hls import Counter
circuit = ft.elaborate_file('top.ft', hls_components=[Counter])
```

**Raises:**

- `FileNotFoundError`: If filepath doesn't exist
- `SyntaxError`: If Flote file has syntax errors
- `ValueError`: If circuit structure is invalid

---

## Circuit Class

Represents an elaborated circuit ready for simulation.

### update()

Apply new values to input signals.

```python
circuit.update(inputs: dict[str, str]) -> None
```

**Parameters:**

- `inputs` (dict): Mapping of signal names to binary string values

**Example:**

```python
# Update single-bit inputs
circuit.update({'a': '1', 'b': '0'})

# Update multi-bit inputs
circuit.update({'data': '10110011', 'enable': '1'})
```

**Notes:**

- Values must be binary strings ('0' and '1')
- Updates propagate through circuit immediately
- Only input signals can be updated

---

### wait()

Advance simulation time without changing inputs.

```python
circuit.wait(time_units: int) -> None
```

**Parameters:**

- `time_units` (int): Time to advance (arbitrary units)

**Example:**

```python
circuit.wait(10)  # Wait 10 time units
circuit.wait(100) # Wait 100 time units
```

**Notes:**

- Used to create gaps in VCD waveform
- Does not change signal values
- Essential for viewing signal transitions

---

### read()

Read current value of a signal.

```python
value = circuit.read(signal_name: str) -> str
```

**Parameters:**

- `signal_name` (str): Name of the signal to read

**Returns:**

- `str`: Binary string representation of signal value

**Example:**

```python
# Read single-bit output
sum_value = circuit.read('sum')  # Returns '0' or '1'

# Read multi-bit output
data = circuit.read('output')    # Returns '10110011'
```

**Raises:**

- `KeyError`: If signal name doesn't exist

---

### save_vcd()

Save simulation waveform to VCD file.

```python
circuit.save_vcd(
    filename: str,
    signals: list[str] = None
) -> None
```

**Parameters:**

- `filename` (str): Output VCD file path
- `signals` (list, optional): List of signals to include (default: all)

**Example:**

```python
# Save all signals
circuit.save_vcd('output.vcd')

# Save specific signals
circuit.save_vcd('debug.vcd', signals=['clock', 'data', 'result'])
```

**Notes:**

- VCD files can be viewed with GTKWave
- Only records changes made via `update()` and `wait()`
- Hierarchical signal names use dot notation: `component.signal`

---

### get_all_signals()

Get list of all signal names in the circuit.

```python
signals = circuit.get_all_signals() -> list[str]
```

**Returns:**

- `list[str]`: List of all signal names

**Example:**

```python
all_signals = circuit.get_all_signals()
print("Available signals:", all_signals)

# Read all outputs
for sig in all_signals:
    if not sig.startswith('input'):  # Skip inputs
        print(f"{sig} = {circuit.read(sig)}")
```

---

### reset()

Reset circuit to initial state.

```python
circuit.reset() -> None
```

**Example:**

```python
# Run some simulation
circuit.update({'clock': '1'})
circuit.wait(10)

# Reset to beginning
circuit.reset()

# Circuit is now in initial state
```

**Notes:**

- Clears all signal values
- Resets simulation time to 0
- Does not clear VCD history (call `save_vcd()` before reset if needed)

---

## Complete Example

```python
import flote as ft

# Elaborate circuit
adder = ft.elaborate_file('FullAdder.ft')

# Get available signals
signals = adder.get_all_signals()
print(f"Circuit has {len(signals)} signals")

# Test all input combinations
for a in ['0', '1']:
    for b in ['0', '1']:
        for cin in ['0', '1']:
            # Apply inputs
            adder.update({'a': a, 'b': b, 'carry_in': cin})
            adder.wait(10)

            # Read outputs
            sum_out = adder.read('sum')
            cout = adder.read('carry_out')

            # Display
            a_int = int(a)
            b_int = int(b)
            cin_int = int(cin)
            result = a_int + b_int + cin_int

            print(f"{a} + {b} + {cin} = {sum_out} (carry={cout})")

            # Verify
            expected_sum = str(result % 2)
            expected_carry = str(result // 2)
            assert sum_out == expected_sum
            assert cout == expected_carry

# Save waveform
adder.save_vcd('full_adder_test.vcd')
print("\nAll tests passed! ✓")
```

## Error Handling

### Common Errors

**FileNotFoundError:**

```python
try:
    circuit = ft.elaborate_file('nonexistent.ft')
except FileNotFoundError:
    print("Circuit file not found!")
```

**SyntaxError:**

```python
try:
    circuit = ft.elaborate_file('invalid.ft')
except SyntaxError as e:
    print(f"Syntax error: {e}")
```

**KeyError (invalid signal):**

```python
circuit = ft.elaborate_file('circuit.ft')

try:
    value = circuit.read('nonexistent_signal')
except KeyError:
    print("Signal doesn't exist!")
```

**ValueError (invalid input):**

```python
try:
    circuit.update({'input': '2'})  # Not binary!
except ValueError:
    print("Values must be binary strings")
```

## Best Practices

### Signal Naming

Access hierarchical signals with dot notation:

```python
# Read sub-component output
value = circuit.read('half_adder_1.sum')

# Update sub-component input (if exposed)
circuit.update({'counter.reset': '1'})
```

### Timing

Create clear waveforms with proper spacing:

```python
# Poor: hard to see transitions
circuit.update({'clock': '0'})
circuit.update({'clock': '1'})
circuit.update({'clock': '0'})

# Better: include wait() calls
circuit.update({'clock': '0'})
circuit.wait(10)
circuit.update({'clock': '1'})
circuit.wait(10)
circuit.update({'clock': '0'})
circuit.wait(10)
```

### Testing Patterns

**Exhaustive testing:**

```python
# Test all 2^n input combinations
n = 3  # Number of inputs
for i in range(2**n):
    inputs = {
        'a': str((i >> 0) & 1),
        'b': str((i >> 1) & 1),
        'c': str((i >> 2) & 1)
    }
    circuit.update(inputs)
    circuit.wait(10)
    # Verify outputs...
```

**Stimulus from file:**

```python
# Load test vectors from file
with open('test_vectors.txt') as f:
    for line in f:
        inputs = line.strip().split(',')
        circuit.update({
            'a': inputs[0],
            'b': inputs[1],
            'expected': inputs[2]
        })
        circuit.wait(10)
```

### VCD Organization

**Selective signal saving:**

```python
# Only save important signals
important = ['clock', 'data_in', 'data_out', 'valid']
circuit.save_vcd('output.vcd', signals=important)
```

**Multiple VCD files:**

```python
# Save different test phases separately
circuit.save_vcd('phase1.vcd')
circuit.reset()

# Phase 2
circuit.update({'mode': '1'})
# ... more simulation ...
circuit.save_vcd('phase2.vcd')
```

## Integration with pytest

```python
# test_circuits.py
import pytest
import flote as ft

@pytest.fixture
def half_adder():
    """Fixture providing elaborated half adder."""
    return ft.elaborate_file('HalfAdder.ft')

def test_half_adder_00(half_adder):
    """Test 0 + 0 = 0."""
    half_adder.update({'a': '0', 'b': '0'})
    half_adder.wait(10)

    assert half_adder.read('sum') == '0'
    assert half_adder.read('carry') == '0'

def test_half_adder_01(half_adder):
    """Test 0 + 1 = 1."""
    half_adder.update({'a': '0', 'b': '1'})
    half_adder.wait(10)

    assert half_adder.read('sum') == '1'
    assert half_adder.read('carry') == '0'

def test_half_adder_11(half_adder):
    """Test 1 + 1 = 10 (binary)."""
    half_adder.update({'a': '1', 'b': '1'})
    half_adder.wait(10)

    assert half_adder.read('sum') == '0'
    assert half_adder.read('carry') == '1'

@pytest.fixture(autouse=True)
def save_waveforms(half_adder, request):
    """Automatically save VCD for each test."""
    yield
    test_name = request.node.name
    half_adder.save_vcd(f'{test_name}.vcd')
```

**Run tests:**

```bash
pytest test_circuits.py -v
```

## Type Hints

For better IDE support, use type hints:

```python
from typing import Dict, List
import flote as ft

def run_test(
    circuit_path: str,
    test_vectors: List[Dict[str, str]]
) -> bool:
    """Run test vectors on a circuit."""
    circuit = ft.elaborate_file(circuit_path)

    for inputs in test_vectors:
        circuit.update(inputs)
        circuit.wait(10)
        # Check outputs...

    return True
```

## Next Steps

- **[HLS API Reference](hls-api.md)** - Python API for HLS components
- **[Advanced: Testbenches](../advanced/testbenches.md)** - Advanced testing patterns
- **[Examples](../examples/half-adder.md)** - See API in action

---

*The Python API provides full control over Flote simulations. Use it to build powerful testbenches!*
