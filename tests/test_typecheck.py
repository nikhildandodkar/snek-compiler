import unittest
from src.typecheck import TypeChecker, TypeKind
from src.ast_nodes import ProgramNode, FuncDefNode, CallNode, TypeNode, IntegerNode, BoolNode, AddNode, IfNode, IdentifierNode

class TestSnekTypeChecker(unittest.TestCase):
    def test_typecheck_integer(self):
        node = IntegerNode(val=7)
        checker = TypeChecker(node)
        self.assertEqual(checker.visit(node), TypeKind.INT)

    def test_typecheck_valid_addition(self):
        node = AddNode(left_expr=IntegerNode(val=2), right_expr=IntegerNode(val=3))
        checker = TypeChecker(node)
        self.assertEqual(checker.visit(node), TypeKind.INT)

    def test_typecheck_invalid_addition_throws_error(self):
        node = AddNode(left_expr=IntegerNode(val=2), right_expr=BoolNode(flag=True))
        checker = TypeChecker(node)
        with self.assertRaises(TypeError):
            checker.visit(node)

    def test_typecheck_if_branch_mismatch(self):
        node = IfNode(
            cond_expr=BoolNode(flag=True),
            then_expr=IntegerNode(val=10),
            else_expr=BoolNode(flag=False)
        )
        checker = TypeChecker(node)
        with self.assertRaises(TypeError):
            checker.visit(node)
    # ==========================================
    # 1. TypeNode Validation Tests
    # ==========================================

    def test_typecheck_invalid_primitive_type_name(self):
        """Should raise a TypeError if a function signature uses an unsupported type (e.g., 'string')."""
        node = FuncDefNode(
            function_name="bad_func",
            parameter_name="x",
            parameter_type=TypeNode("string"),  # Unsupported type
            return_type=TypeNode("int"),
            body_expr=IntegerNode(val=5)
        )
        # We test ProgramNode since function registration typically happens at program level
        prog = ProgramNode(function_defs=[node], expr=IntegerNode(val=1))
        checker = TypeChecker(prog)
        with self.assertRaises(TypeError):
            checker.typecheck()


    # ==========================================
    # 2. FuncDefNode Validation Tests
    # ==========================================

    def test_typecheck_valid_func_def(self):
        """Should successfully typecheck when body_expr matches the expected return_type."""
        node = FuncDefNode(
            function_name="is_positive",
            parameter_name="x",
            parameter_type=TypeNode("int"),
            return_type=TypeNode("bool"),
            body_expr=BoolNode(flag=True)  # Returns a bool, matching declaration
        )
        prog = ProgramNode(function_defs=[node], expr=IntegerNode(val=1))
        checker = TypeChecker(prog)
        
        # Checking a valid program shouldn't raise any errors
        try:
            checker.typecheck()
        except TypeError:
            self.fail("typecheck failed on a perfectly valid function definition!")

    def test_typecheck_func_def_return_type_mismatch(self):
        """Should raise a TypeError if the evaluated body type doesn't match the declared return type."""
        node = FuncDefNode(
            function_name="identity_fail",
            parameter_name="x",
            parameter_type=TypeNode("int"),
            return_type=TypeNode("bool"),     # Declared to return bool...
            body_expr=IntegerNode(val=42)    # ...but returns an int instead!
        )
        prog = ProgramNode(function_defs=[node], expr=IntegerNode(val=1))
        checker = TypeChecker(prog)
        with self.assertRaises(TypeError):
            checker.typecheck()

    def test_typecheck_func_body_uses_parameter(self):
        """Should successfully evaluate a function body that relies on its input parameter."""
        # Function: (def add_one (x : int) : int (+ x 1))
        node = FuncDefNode(
            function_name="add_one",
            parameter_name="x",
            parameter_type=TypeNode("int"),
            return_type=TypeNode("int"),
            body_expr=AddNode(left_expr=IdentifierNode(name="x"), right_expr=IntegerNode(val=1))
        )
        prog = ProgramNode(function_defs=[node], expr=IntegerNode(val=1))
        checker = TypeChecker(prog)
        
        try:
            checker.typecheck()
        except TypeError:
            self.fail("Failed to resolve parameter variable 'x' inside the function scope map.")


    # ==========================================
    # 3. CallNode Validation Tests
    # ==========================================

    def test_typecheck_valid_function_call(self):
        """Should return the declared return type when calling a function with the correct argument type."""
        # Main program calling an already registered function: (my_func true)
        node = CallNode(function_name="my_func", para_expr=BoolNode(flag=True))
        checker = TypeChecker(node)
        
        # Seed the global function environment map: "my_func" expects a BOOL, returns an INT
        # Adjust property name based on how you implement your map storage (e.g., function_map, function_env)
        checker.function_map = {"my_func": (TypeKind.BOOL, TypeKind.INT)} 
        
        result_type = checker.visit(node)
        self.assertEqual(result_type, TypeKind.INT)

    def test_typecheck_call_argument_type_mismatch(self):
        """Should raise a TypeError if a function expecting an int receives a bool expression."""
        # Calling (square true) where square expects an int
        node = CallNode(function_name="square", para_expr=BoolNode(flag=True))
        checker = TypeChecker(node)
        
        # square: (INT) -> INT
        checker.function_map = {"square": (TypeKind.INT, TypeKind.INT)}
        
        with self.assertRaises(TypeError):
            checker.visit(node)

    def test_typecheck_call_undefined_function(self):
        """Should raise a TypeError if you try to call a function that hasn't been declared."""
        node = CallNode(function_name="ghost_func", para_expr=IntegerNode(val=10))
        checker = TypeChecker(node)
        checker.function_map = {} # No functions registered
        
        with self.assertRaises(TypeError):
            checker.visit(node)


    # ==========================================
    # 4. ProgramNode Scope Scenarios
    # ==========================================

    def test_typecheck_parameter_leak_isolation(self):
        """Should throw a error if the main block tries to access a parameter out of its function scope."""
        # Function def defines variable 'x'
        func_node = FuncDefNode(
            function_name="f",
            parameter_name="x",
            parameter_type=TypeNode("int"),
            return_type=TypeNode("int"),
            body_expr=IdentifierNode(name="x")
        )
        # Main block expression tries to look up 'x' outside the function boundary
        main_expr = IdentifierNode(name="x") 
        
        prog = ProgramNode(function_defs=[func_node], expr=main_expr)
        checker = TypeChecker(prog)
        
        with self.assertRaises(TypeError):
            checker.typecheck()
    
if __name__ == '__main__':
    unittest.main()
