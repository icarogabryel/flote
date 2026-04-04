# Flote Roadmap

Overview of Flote's development, organized by phases and versions.

## Version 1.0

The beta phase focuses on core functionality, distribution and documentation, including:

- [X] Make the component class for simulation
- [X] Make EBNF for the language
- [X] Make Scanner
- [X] Make Parser
- [X] Make Builder
- [X] Add expressions
- [X] Make testbench class
- [X] Create signal class for waveform dump
- [X] Improve the algorithm of simulation (n² -> n+e)
- [X] Publish initial beta package in PyPI
- [X] Improve declaration to accept assignment
- [X] Make declaration order not necessary
- [X] Make multi-declaration support
- [X] Add Arrays signals support
  - [X] Declaration
  - [X] Assignment
  - [X] Operation
  - [X] Error handling for declaration and assignment
  - [X] .vcd dump support for multi-dimensional bit signals
  - [X] Indexing
  - [X] Slicing
  - [X] Error handling for indexing and slicing
  - [X] Concatenation
  - [X] Reverse arrays support
- [X] Add sub-components support
  - [X] Instantiation
  - [X] Connection
  - [X] Error handling for instantiation and connection
  - [X] .vcd dump scope support for sub-components
- [X] complete Python API
- [ ] Make automated tests
- [X] Create GitHub Actions for CI/CD
- [ ] Create complete documentation
- [ ] Make oficial Site with GitHub pages

## Version 2.0

Expansion of functionality, FPGA support, rust backend for FPGA simulation, and VS Code extension.

- [ ] Create import feature
- [ ] Add multi-dimensional array support
- [ ] Implement abstract Python components
- [ ] Make FPGA support (Altera and Xilinx)
- [ ] Implement Rust backend for faster FPGA simulation
- [ ] Create VS Code extension for language server support

## Version 3.0

Package manager, std libs, and advanced language features.

- [ ] Create std libs
- [ ] Package manager
- [ ] Add generate statement support
- [ ] Add multi-assignment support
- [ ] Add in-out signals support
- [ ] Add x-bit (0, 1, x, z) support

## Version 4.0

FPGA superset language with comportamental commands.

- [ ] FPGA superset language

---

## 📊 Estimated Timeline

Since Flote is an open-source project, timelines are flexible and depend on contributions and priorities.

## 📞 Feedback & Contributions

This roadmap is dynamic and can be adjusted based on:

- Community feedback
- Priorities and timing
- Technical discoveries

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

*Last updated: April 2026*
