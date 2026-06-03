# Makefile for Snek Compiler

SRC_DIR = src
OUTPUT_ASM = generated_code.asm

all: run

run: compile_asm
	./exec

compile_asm:
	python3 $(SRC_DIR)/main.py $(FILE)
	nasm -f elf64 $(OUTPUT_ASM) -o output.o
	clang -c $(SRC_DIR)/runner.c -o runner.o
	clang runner.o output.o -o exec

clean:
	rm -f *.o exec generated_code.asm *.log
	rm -rf __pycache__ output/

.PHONY: all run compile_asm clean
