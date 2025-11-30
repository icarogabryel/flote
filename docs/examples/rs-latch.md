# RS Latch

An **RS Latch** (Set-Reset Latch) is a fundamental sequential circuit that stores one bit of information.

## What is a Latch?

A latch is a **memory element** that:

- Stores a binary value (0 or 1)
- Retains its state until explicitly changed
- Has two stable states (bistable)

Unlike combinational circuits (gates), latches have **feedback** - their outputs feed back to their inputs.

## RS Latch Behavior

The RS Latch has two inputs:

- **S (Set):** Forces output Q to 1
- **R (Reset):** Forces output Q to 0

And two outputs:

- **Q:** The stored bit
- **Q̄ (Q-bar):** The complement of Q

### Truth Table

| S | R | Q (next) | Q̄ (next) | Action |
|---|---|----------|----------|--------|
| 0 | 0 | Q (hold) | Q̄ (hold) | Hold current state |
| 0 | 1 | 0        | 1        | Reset |
| 1 | 0 | 1        | 0        | Set |
| 1 | 1 | Invalid  | Invalid  | **Forbidden state** |

!!! warning "Forbidden State"
    Setting both S=1 and R=1 simultaneously creates an invalid state. When both return to 0, the output is unpredictable.

## Circuit Diagram

```
     ┌───────┐
  S──┤       │
     │  NOR  ├──Q
  ┌──┤       │
  │  └───────┘
  │
  │  ┌───────┐
  └──┤       │
     │  NOR  ├──Q̄
  R──┤       │
  ┌──┤       │
  │  └───────┘
  │
  └──────────┘
```

The latch consists of two NOR gates with **cross-coupled feedback**.

## Flote Implementation

```flote
// RsLatch.ft
main comp RsLatch {
    in bit s;      // Set input
    in bit r;      // Reset input
    out bit q;     // Output
    out bit q_bar; // Complementary output

    // Cross-coupled NOR gates
    q = r nor q_bar;
    q_bar = s nor q;
}
```

This is a **feedback circuit** - each output depends on the other output.

## How It Works

### Set Operation (S=1, R=0)

1. `q_bar = s nor q = 1 nor q = 0` (NOR with 1 is always 0)
2. `q = r nor q_bar = 0 nor 0 = 1`

Result: **Q=1, Q̄=0** (latch is SET)

### Reset Operation (S=0, R=1)

1. `q = r nor q_bar = 1 nor q_bar = 0`
2. `q_bar = s nor q = 0 nor 0 = 1`

Result: **Q=0, Q̄=1** (latch is RESET)

### Hold Operation (S=0, R=0)

The latch maintains its previous state through feedback:

- If Q was 1: `q = 0 nor 0 = 1` ✓ (stays 1)
- If Q was 0: `q_bar = 0 nor 1 = 0` → `q = 0 nor 0 = 1` ✗

Actually: feedback propagates to stabilize at previous state.

## Testbench

```python
# test_rs_latch.py
import flote as ft

# Elaborate the latch
latch = ft.elaborate_file('RsLatch.ft')

print("RS Latch Test")
print("=" * 60)
print("Operation      | S | R | Q | Q̄ | State")
print("-" * 60)

# Initial state (both inputs 0)
latch.update({'s': '0', 'r': '0'})
latch.wait(10)
q = latch.read('q')
q_bar = latch.read('q_bar')
print(f"Initial        | 0 | 0 | {q} | {q_bar} | Unknown")

# Set the latch
latch.update({'s': '1', 'r': '0'})
latch.wait(10)
q = latch.read('q')
q_bar = latch.read('q_bar')
print(f"Set            | 1 | 0 | {q} | {q_bar} | Q=1")

# Hold (release set)
latch.update({'s': '0', 'r': '0'})
latch.wait(10)
q = latch.read('q')
q_bar = latch.read('q_bar')
print(f"Hold           | 0 | 0 | {q} | {q_bar} | Q=1 (held)")

# Reset the latch
latch.update({'s': '0', 'r': '1'})
latch.wait(10)
q = latch.read('q')
q_bar = latch.read('q_bar')
print(f"Reset          | 0 | 1 | {q} | {q_bar} | Q=0")

# Hold (release reset)
latch.update({'s': '0', 'r': '0'})
latch.wait(10)
q = latch.read('q')
q_bar = latch.read('q_bar')
print(f"Hold           | 0 | 0 | {q} | {q_bar} | Q=0 (held)")

# Set again
latch.update({'s': '1', 'r': '0'})
latch.wait(10)
q = latch.read('q')
q_bar = latch.read('q_bar')
print(f"Set again      | 1 | 0 | {q} | {q_bar} | Q=1")

# Forbidden state warning
latch.update({'s': '1', 'r': '1'})
latch.wait(10)
q = latch.read('q')
q_bar = latch.read('q_bar')
print(f"Forbidden      | 1 | 1 | {q} | {q_bar} | Invalid!")

print("-" * 60)

# Save waveform
latch.save_vcd('rs_latch.vcd')
print("\nWaveform saved to rs_latch.vcd")
```

## Running the Example

```bash
python test_rs_latch.py
```

**Expected Output:**

```
RS Latch Test
============================================================
Operation      | S | R | Q | Q̄ | State
------------------------------------------------------------
Initial        | 0 | 0 | 0 | 1 | Unknown
Set            | 1 | 0 | 1 | 0 | Q=1
Hold           | 0 | 0 | 1 | 0 | Q=1 (held)
Reset          | 0 | 1 | 0 | 1 | Q=0
Hold           | 0 | 0 | 0 | 1 | Q=0 (held)
Set again      | 1 | 0 | 1 | 0 | Q=1
Forbidden      | 1 | 1 | 0 | 0 | Invalid!

Waveform saved to rs_latch.vcd
```

## Viewing the Waveform

```bash
gtkwave rs_latch.vcd
```

You'll observe:

- Q and Q̄ are complementary (one high, one low) except in forbidden state
- State persists when both inputs are 0 (hold)
- Transitions occur when S or R is activated

## Delta Cycles and Feedback

Flote's simulator uses **delta cycles** to resolve feedback:

1. Apply input changes
2. Evaluate all logic
3. If outputs changed, repeat evaluation (delta cycle)
4. Continue until stable (no changes)

For the RS latch:

```
Initial: S=0, R=0, Q=0, Q̄=1

Apply S=1, R=0:

Cycle 1:
  q_bar = s nor q = 1 nor 0 = 0
  q = r nor q_bar = 0 nor 1 = 0  (using old q_bar)

Cycle 2:
  q = r nor q_bar = 0 nor 0 = 1  (using new q_bar)

Cycle 3:
  q = r nor q_bar = 0 nor 0 = 1  (no change - stable!)

Final: Q=1, Q̄=0
```

## Building a D Latch

Add a data input and enable:

```flote
// DLatch.ft
comp RsLatch {
    in bit s;
    in bit r;
    out bit q;
    out bit q_bar;

    q = r nor q_bar;
    q_bar = s nor q;
}

main comp DLatch {
    in bit d;       // Data input
    in bit enable;  // Enable input
    out bit q;

    sub RsLatch as rs;

    // When enabled, S=D, R=not D
    bit not_d = not d;
    rs.s = d and enable;
    rs.r = not_d and enable;

    q = rs.q;
}
```

**Test the D Latch:**

```python
# test_d_latch.py
import flote as ft

dlatch = ft.elaborate_file('DLatch.ft')

# Enable=0: should hold value
dlatch.update({'d': '1', 'enable': '0'})
dlatch.wait(10)
print(f"Enable=0, D=1: Q={dlatch.read('q')} (should hold)")

# Enable=1, D=1: latch captures 1
dlatch.update({'enable': '1'})
dlatch.wait(10)
print(f"Enable=1, D=1: Q={dlatch.read('q')}")

# Enable=0: should hold 1
dlatch.update({'enable': '0'})
dlatch.wait(10)
print(f"Enable=0, D=1: Q={dlatch.read('q')} (holding 1)")

# Enable=1, D=0: latch captures 0
dlatch.update({'d': '0', 'enable': '1'})
dlatch.wait(10)
print(f"Enable=1, D=0: Q={dlatch.read('q')}")

dlatch.save_vcd('d_latch.vcd')
```

## Key Concepts

### Sequential vs Combinational

**Combinational circuits:**
- Output depends only on current inputs
- No memory
- Examples: gates, adders, multiplexers

**Sequential circuits:**
- Output depends on current inputs AND previous state
- Has memory (stores state)
- Examples: latches, flip-flops, counters

### Feedback

Feedback creates memory by allowing outputs to influence themselves:

```flote
q = r nor q_bar;    // q influences q_bar
q_bar = s nor q;    // q_bar influences q
```

Without feedback, circuits are purely combinational.

### Metastability

In real hardware, violating timing constraints can cause **metastability** - outputs stuck between 0 and 1. Flote's simulator doesn't model this, but it's a real concern in physical circuits.

## Challenges

### Challenge 1: Toggle Latch

Create a latch with a single "toggle" input that flips state:

```flote
// Hint: use current state in feedback
out bit q;
q = (toggle xor q) or ...
```

### Challenge 2: 4-bit Register

Use 4 D latches to create a 4-bit register:

```flote
in bit data[4];
in bit enable;
out bit stored[4];
```

### Challenge 3: Edge Detection

Modify the D latch to only capture on rising edge of enable (level → edge triggered).

## Next Steps

- **[Half Adder](half-adder.md)** - Combinational circuit review
- **[Multiplexer](multiplexer.md)** - Data routing circuits
- **[Advanced: Feedback Circuits](../guide/feedback-circuits.md)** - Deep dive into sequential logic

---

*The RS latch is the foundation of all digital memory. Master it and sequential circuits become clear!*
