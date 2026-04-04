# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and this project follows Semantic Versioning.

## [1.0.0]

First stable release (non-beta).

### Added

- Flote HDL elaboration pipeline with Scanner, Parser, and Builder.
- Netlist IR generation as a stable boundary between elaboration and simulation.
- Python simulation runtime with signal propagation and stabilization.
- TestBench API with waveform export support (`.vcd`).
- Support for arrays, slicing, concatenation, reverse indexes, and subcomponents.
- Documentation site and project examples.
- CI/CD workflows for package builds and distribution.

### Notes

- Rust backend module exists as a placeholder and is not integrated yet.
