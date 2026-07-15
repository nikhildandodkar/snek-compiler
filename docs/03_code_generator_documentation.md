# Compiler Pass Documentation: x86-64 Code Generator

## 1. Overview and Responsibility
The **Code Generation Pass** transforms a type-validated AST into runnable x86-64 assembly instructions. 
*   **Target Framework:** System V AMD64 ABI architecture calling conventions.
*   **Encoding Scheme:** Employs a specific tagged-pointer strategy for unified representation of runtime types inside 64-bit registers.

## 2. Runtime Value Encoding (NaN Boxing / Tagged Pointers)
To handle dynamic runtime values without explicit memory overhead, numbers and booleans are packed into 64-bit registers (`rax`) using unique bitwise signatures:

*   **Integers:** Shifted left by 1 bit with the lowest bit set to `1`. Formula: $\text{Runtime Value} = (\text{Integer} \times 2) + 1$.
*   **Booleans:** Assigned unique structural bitmasks containing low-bit indicators:
    *   `TRUE_VAL`  = `0xfffffffffffffffe`
    *   `FALSE_VAL` = `0x7ffffffffffffffe`

## 3. Storage and Stack Allocation Model
The generator maintains local context stack frames on the x86 stack frame utilizing base register offsets `[rbp - offset]`.
*   Variable tracking is dynamic using internal stack index count increments (`self.push_variable()` and `self.pop_variable()`).
*   Every stack shift maps directly to 8-byte boundaries matching architecture alignment requirements.

## 4. Code Generation Rules (Visitor Implementations)

### Structure Prologue & Epilogue
Every compiled binary file generated outputs formal initialization templates:
```assembly
section .text
global code_starts_here:
code_starts_here:
     push rbp 
     mov rbp, rsp
     ; ... generated code body ...
     mov rsp, rbp
     pop rbp
     ret
```

### Node Generation Logic

#### `IntegerNode` / `BoolNode`
Loads structural packed value representations directly into the working register:
*   Integer: `mov rax, (val * 2 + 1)`
*   True: `mov rax, 0xfffffffffffffffe`

#### `AddNode`
1.  Visits `left_expr` $ightarrow$ Result goes into `rax`.
2.  Pushes `rax` onto the stack frame block offset via `push_variable()`.
3.  Visits `right_expr` $ightarrow$ Result overwrites `rax`.
4.  Unmasks the tagged integer component via `and rax, 0xfffffffffffffffe`.
5.  Executes `add rax, [rbp - stack_offset]` to add the left value.
6.  Pops local variable stack bounds via `pop_variable()`.

#### `IncNode` / `DecNode`
*   Visits the operand sub-expression.
*   Since integers are stored multiplied by 2, incrementing or decrementing by an absolute value of `1` corresponds to an operation value shift of `2` (`add rax, 2` or `sub rax, 2`).

#### `LetNode` / `IdentifierNode`
*   `LetNode` evaluates the assigned block expression, stores the computed value inside a newly allocated stack variable slot, and tracks it in `self.variable_map`.
*   `IdentifierNode` fetches the stored value from its known stack address mapping relative to `rbp`.

#### `IfNode` (Branching Logic)
Uses comparison evaluations alongside jumping flags:
1.  Evaluates `cond_expr`.
2.  Emits `cmp rax, 0` and `je else_of_if_N`.
3.  Emits instructions for the `then_expr` body, followed by a `jmp end_of_if_N`.
4.  Appends the unique relational label marker tags `else_of_if_N:` and `end_of_if_N:` dynamically tracking blocks.
