#

<div align="center">
  <img src="https://i.postimg.cc/nz5SPMR6/logo.png" width="60%" alt="Flote logo"/>
</div>

<br>

<div align="center">
  <img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/icarogabryel/flote?style=flat&logo=github">
  <img alt="GitHub Workflow" src="https://img.shields.io/github/actions/workflow/status/icarogabryel/flote/CI.yml">
  <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/flote?color=green">
  <img src="https://img.shields.io/github/license/icarogabryel/flote" alt="license"/>
</div>

## A Modern Hardware Description Language

<div align="center">
  <img src="https://i.postimg.cc/xC7p4qpr/print.png" width="90%" alt="Flote in VS Code"/>
</div>

Flote is a **hardware description language (HDL)** and **Python framework** designed for digital circuit simulation. It's built to be **friendly, simple, lightweight, and productive** — much easier to learn and use than traditional HDLs like VHDL and Verilog.

### Key Features

- **🎯 Simple Syntax**: Clean, intuitive syntax inspired by modern programming languages
- **🚀 Easy to Learn**: Minimal learning curve compared to VHDL/Verilog
- **⚡ Fast Installation**: Install via pip in seconds: `pip install flote`
- **🐍 Python Integration**: Write testbenches in Python with full language expressiveness
- **🔧 Lightweight**: No heavy IDEs required — use any text editor
- **📊 VCD Output**: Standard waveform output for visualization
- **🎨 HLS Support**: Create complex components using pure Python
- **🔄 Event-Driven Simulation**: Efficient simulation with delta-cycle support

### Quick Example

```flote
comp HalfAdder {
    in bit a;
    in bit b;

    out bit sum = a xor b;
    out bit carry = a and b;
}
```

```python
import flote as ft

# Elaborate the circuit
half_adder = ft.elaborate_file('HalfAdder.ft')

# Test all combinations
half_adder.update({'a': '0', 'b': '0'})
half_adder.wait(10)

half_adder.update({'a': '0', 'b': '1'})
half_adder.wait(10)

# Save waveform
half_adder.save_vcd('HalfAdder.vcd')
```

## Why Flote?

Traditional HDLs like VHDL and Verilog were designed decades ago for FPGA/ASIC synthesis. They come with:

- ❌ Verbose, complex syntax
- ❌ Confusing abstractions
- ❌ Heavy, buggy toolchains
- ❌ Steep learning curve
- ❌ Poor documentation

Flote addresses these issues with:

- ✅ Concise, modern syntax (58% less code than VHDL)
- ✅ Clear logic gate abstractions
- ✅ Lightweight Python-based tools
- ✅ Easy to learn and use
- ✅ Comprehensive documentation

## Who is Flote For?

- **Students** learning digital design and computer architecture
- **Engineers** prototyping and validating digital circuits
- **Researchers** experimenting with hardware algorithms
- **Educators** teaching digital systems without VHDL complexity

## Get Started

Ready to simplify your hardware development?

<div class="grid cards" markdown>

-   🚀 __Quick Start__

    ---

    Get up and running with Flote in minutes

    [Getting Started](getting-started/introduction.md)

-   📖 __User Guide__

    ---

    Learn Flote syntax and concepts

    [User Guide](guide/basic-concepts.md)

<!-- -   📝 __Examples__

    ---

    Explore practical circuit examples

    [Examples](examples/half-adder.md) -->

</div>

## Community & Support

- **GitHub**: [icarogabryel/flote](https://github.com/icarogabryel/flote)
- **Issues**: Report bugs or request features on GitHub
- **PyPI**: [flote](https://pypi.org/project/flote/)

## License

Flote is open-source software distributed under the MIT License.

---

*Flote is an open-source project developed as part of academic research at CESLa (of Federal University of Piauí) and my humble bedroom, Brazil.*

<div align="center">
  <img src="imgs/brazil-mentioned.png" width="50%" alt="Brazil Mentioned"/>
</div>
