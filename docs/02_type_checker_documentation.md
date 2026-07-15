# Compiler Pass Documentation: Type Checker

## 1. Overview and Responsibility
The **Type Checker Pass** executes semantic validation across the Abstract Syntax Tree (AST) after successfully parsing input code. Its core goals are:
*   Ensure structural expressions are executed with valid type arguments.
*   Perform compile-time safe evaluation of static conditional branches.
*   Establish scope verification and prevent execution type discrepancies.

## 2. Type System Model
The compiler defines two atomic types via an enumeration (`TypeKind`):
1.  `TypeKind.INT`: Represents integer values.
2.  `TypeKind.BOOL`: Represents boolean flags.

## 3. Implementation Details (`TypeChecker` class)
The pass uses Python's `@singledispatchmethod` to elegantly handle multi-dispatch structural AST processing.

### Structural Scoping Tracking
*   `self.variable_map`: Stores the active mapping between strings (bound identifier names) and their corresponding evaluated `TypeKind`.

### Dispatch Rules Matrix

#### Primitive Evaluation
*   `IntegerNode` $
ightarrow$ Automatically returns `TypeKind.INT`.
*   `BoolNode` $
ightarrow$ Automatically returns `TypeKind.BOOL`.

#### Arithmetic Verification (`AddNode`)
*   Evaluates the sub-expressions `left_expr` and `right_expr`.
*   **Constraint:** Both sub-expressions **must** evaluate strictly to `TypeKind.INT`.
*   **Error Condition:** Throws a `TypeError` if any operand evaluates to `TypeKind.BOOL`.

#### Relational Operator Verification (`BinOpNode`)
*   Evaluates the sub-expressions `left_expr` and `right_expr`.
*   **Constraint:** Both operands must be `TypeKind.INT`.
*   **Result:** The expression evaluates to `TypeKind.BOOL`.

#### Conditional Verification (`IfNode`)
*   Step 1: Validates that `cond_expr` evaluates exactly to `TypeKind.BOOL`.
*   Step 2: Evaluates both the `then_expr` branch and the `else_expr` branch.
*   **Constraint:** The static type of both branches **must match exactly**.
*   **Result:** Returns the unified common type of the branches.

#### Local Variable Scoping (`LetNode`)
*   Step 1: Evaluates the binding expression type (`name_expr`).
*   Step 2: Maps the identifier name to this type in `self.variable_map`.
*   Step 3: Evaluates and returns the structural type of the target body expression (`let_expr`).

#### Variable Mutation (`SetNode`)
*   Step 1: Checks if `node.name` exists in `self.variable_map`. If not, throws a `TypeError`.
*   Step 2: Evaluates the new evaluation expression type (`val_expr`).
*   **Constraint:** The new expression's type must match the identifier's existing type signature tracked in `self.variable_map`.
*   **Result:** Returns the type of the assigned value.

#### Loop Verification (`WhileNode`)
*   Step 1: Validates that `cond_expr` evaluates exactly to `TypeKind.BOOL`.
*   Step 2: Evaluates the internal loop loop body expression (`body_expr`).
*   **Result:** Automatically evaluates to `TypeKind.BOOL` since loop boundaries terminate upon hitting a false conditional block state.

#### Variable Reference Verification (`IdentifierNode`)
*   Looks up the variable tracking key inside the active `self.variable_map`.
*   Returns the matched type value directly.

## 4. Error Diagnostics
The phase raises strict `TypeError` messages containing explicit semantic mismatch details to aid debug analysis:
*   `TypeError: cannot add TypeKind.BOOL and TypeKind.INT`
*   `TypeError: branches have different type`
*   `TypeError: condition expression in not bool type`
