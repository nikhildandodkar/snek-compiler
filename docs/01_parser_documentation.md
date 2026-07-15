# Compiler Pass Documentation: Tokenizer & Parser

## 1. Overview and Responsibility
The **Parsing Pass** is the entry point of the compiler pipeline. Its responsibilities include:
*   **Lexical Analysis (Tokenization):** Converting the raw string input of an S-expression based language into a structured stream of tokens.
*   **Syntactic Analysis (Parsing):** Validating the token stream against the language's Backus-Naur Form (BNF) grammar and constructing an Abstract Syntax Tree (AST).

## 2. Grammar Rules Supported (BNF)
The language conforms to the following formal grammar definition:
```bnf
expr := <number>
      | true
      | false
      | <identifier>
      | (<op> <expr>)
      | (let (name <expr>) <expr>)
      | (set name <expr>)
      | (while <expr> <expr>)
      | (+ <expr> <expr>)
      | (if <expr> <expr> <expr>)
op   := inc | dec
```

## 3. Abstract Syntax Tree (AST) Nodes
The pass utilizes `dataclasses` to represent AST structural components:
*   `ASTNode`: The base node class.
*   `IntegerNode(val: int)`: Holds integer literal constants.
*   `BoolNode(flag: bool)`: Holds boolean constants (`true` / `false`).
*   `IdentifierNode(name: str)`: Represents bound variable lookups.
*   `IncNode(arg_expr: ASTNode)` / `DecNode(arg_expr: ASTNode)`: Single-argument arithmetic operations.
*   `AddNode(left_expr: ASTNode, right_expr: ASTNode)`: Standard binary addition.
*   `BinOpNode(operator: str, left_expr: ASTNode, right_expr: ASTNode)`: Relational binary comparisons (`<`, `>`, `==`).
*   `LetNode(name: str, name_expr: ASTNode, let_expr: ASTNode)`: Local variable bindings.
*   `IfNode(cond_expr: ASTNode, then_expr: ASTNode, else_expr: ASTNode)`: Conditional branching statements.

## 4. Implementation Details

### Tokenization (`Tokenize` function)
```python
def Tokenize(sexp):
    spaced = sexp.replace('(',' ( ').replace(')',' ) ')
    return spaced.split()
```
*   **Mechanism:** Inserts explicit spaces surrounding parentheses `(` and `)` to ensure simple string splitting via whitespace (`.split()`) works robustly for S-expressions.

### Recursive Descent Parser (`Parser` class)
*   **State Management:** Tracks token arrays via a pointer (`self._pos`).
*   **Lookahead Strategy:** Employs `get_next_token()` for predictive parsing choices without advancing the state immediately.
*   **Symbol Scoping Management:** Populates `self.identifier` dynamically inside the parser loop when a variable binding (`let`) occurs to validate subsequent identifier recognition.

### Critical Parsing Branches
*   **Primitives:** Evaluates `isdecimal()`, `true`, and `false` directly to yield primitive literal nodes.
*   **S-Expression Groups:** Initiated via `(`. Once matched, the parser performs a keyword lookahead to dispatch matching branches:
    *   `inc` / `dec` $
ightarrow$ Unary transformations.
    *   `+` $
ightarrow$ Arithmetic addition node generation.
    *   `let` $
ightarrow$ Binds a local scope block, tracking variable bindings.
    *   `if` $
ightarrow$ Parses three consecutive child expressions (`cond`, `then`, `else`).
    *   Binary operators (`<`, `>`, `==`) $
ightarrow$ Relational structural node generation.

## 5. Error Detection & Validation
The parser throws `ValueError` in any scenario breaking the structured S-expression structure:
1.  **Mismatched Parentheses:** Fails if the closing structural symbol `)` is omitted following block processing.
2.  **Keyword Shadowing:** Explicitly prevents binding reserved syntax keywords (e.g., trying to bind `let` as a variable name).
3.  **Invalid Syntax Configurations:** Throws syntax errors if tokens appear out of grammar alignment.
