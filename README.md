# Snek Compiler - x86-64 Compiler for S-expression Language

A compiler for a Lisp/Scheme-like language (S-expressions) that generates x86-64 assembly. Inspired by UCSD CSE 131 Compiler Construction course.

**Status**: In Progress

## Features

### Currently Implemented
- [x] Arithmetic: `+`, `inc`, `dec`
- [x] S-expression parser
- [x] Stack-based code generation to x86-64
- [x] Basic runtime setup
- [x] Let bindings (variables)
- [x] Conditionals (`if`)

### Planned / In Progress
- [ ] Functions and calling convention
- [ ] Tuples / Data structures
- [ ] Garbage Collection
- [ ] Register allocation
- [ ] Optimizations

## Tech Stack
- **Language**: Python 3
- **Target**: x86-64 Assembly (NASM)
- **Tools**: Python, Make, GCC

## Quick Start

```bash
# Clone the repo
git clone https://github.com/nikhildandodkar/snek-compiler.git
cd snek-compiler

# Install dependencies
pip install -r requirements.txt

# Build and run a program
make run FILE=examples/simple.snek
```
## Unit Test

```bash
# Go to project directory
cd snek-compiler

# command to run all test
python -m unittest discover -s tests

# command to run test for single module
python -m unittest tests/test_parser.py
```
