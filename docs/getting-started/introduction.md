# Introduction to Flote

## What is Flote?

Flote is a modern **Hardware Description Language (HDL)** specifically designed for digital circuit **simulation**. Unlike traditional HDLs like VHDL and Verilog, which were created decades ago primarily for FPGA and ASIC synthesis, Flote focuses on making hardware development **accessible, intuitive, and productive**.

## Why Another HDL?

Traditional HDLs present significant challenges:

### Problems with VHDL/Verilog

**Complexity & Verbosity**

```vhdl
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity half_adder is
    port(
        a     : in  std_logic;
        b     : in  std_logic;
        sum   : out std_logic;
        carry : out std_logic
    );
end half_adder;

architecture behavioral of half_adder is
begin
    sum   <= a xor b;
    carry <= a and b;
end behavioral;
```

**vs Flote's Simplicity**

```flote
comp HalfAdder {
    in bit a;
    in bit b;

    out bit sum = a xor b;
    out bit carry = a and b;
}
```

Less code - same functionality!

### Key Issues Flote Addresses

1. **Steep Learning Curve**: VHDL/Verilog have complex syntax based on outdated programming paradigms (Pascal, Ada from the 1980s)

2. **Heavy Toolchains**: Tools like Quartus Prime and ModelSim are bulky, slow, and difficult to set up

3. **Poor Documentation**: Scattered, incomplete, often outdated documentation makes learning difficult

4. **Difficult Debugging**: Confusing error messages, complex debugging workflows

5. **Low Productivity**: Verbose code + complex tools = slow development

## The Flote Approach

Flote solves these problems through:

### 1. Simple, Modern Syntax

- Inspired by modern languages (Python, C++)
- Clear, readable code
- Logical structure that matches hardware concepts

### 2. Lightweight Python Integration

- Install with a single command: `pip install flote`
- Use any text editor (VS Code, Sublime, even Notepad++)
- Write testbenches in familiar Python
- No heavy IDE required

### 3. Focus on Logic Gates

Abstractions are based directly on digital logic concepts:

- AND, OR, XOR, NAND, NOR, XNOR, NOT gates
- Clear signal flow
- Hierarchical component composition

## Design Philosophy

Flote is built on these principles:

**Simplicity Over Features**
: Include only what's necessary for effective circuit simulation

**Clarity Over Brevity**
: Code should be self-documenting and easy to understand

**Learning Over Legacy**
: Designed for students and newcomers, not just experts

**Python Integration**
: Leverage Python's ecosystem and familiarity

## Who Should Use Flote?

### Perfect For

- **Students**: Learning digital design without VHDL complexity
- **Educators**: Teaching computer architecture with minimal overhead
- **Engineers**: Rapid prototyping and validation of digital circuits
- **Researchers**: Experimenting with hardware algorithms
- **Hobbyists**: Building and simulating digital systems

### Not Ideal For

- **FPGA Synthesis**: Flote is simulation-focused (use VHDL/Verilog for synthesis)
- **ASIC Production**: Professional chip design requires specialized tools

!!! note "Simulation vs Synthesis"
    Flote is optimized for **simulation** and **validation**, not physical implementation. If you need to synthesize to an FPGA or ASIC, you'll need to use traditional tools. However, Flote is excellent for designing, testing, and validating your logic before committing to synthesis.

## Research Validation

Flote has been empirically validated through research at the Federal University of Piauí (UFPI) with 18 Computer Science students who had experience with VHDL.

| Metric | VHDL (Difficulty) | Flote (Ease) | Improvement |
|--------|-------------------|--------------|-------------|
| Learning | 2.22/5 | 4.67/5 | **+110%** |
| Usage | 2.33/5 | 4.61/5 | **+97.9%** |
| Tooling | 1.83/5 | 4.39/5 | **+140%** |

## What's Next?

Ready to get started?

1. **[Installation](installation.md)** - Set up Flote in minutes
2. **[Quick Start](quick-start.md)** - Build your first circuit
3. **[Basic Concepts](../guide/basic-concepts.md)** - Learn core concepts

## Community & Support

- **GitHub**: [github.com/icarogabryel/flote](https://github.com/icarogabryel/flote)
- **Issues**: Report bugs or feature requests
- **PyPI**: [pypi.org/project/flote](https://pypi.org/project/flote/)
