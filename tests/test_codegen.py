import unittest
from src.codegen import CodeGenerator
from src.ast_nodes import IntegerNode, BoolNode, LetNode, IdentifierNode

class TestSnekCodeGenerator(unittest.TestCase):
    def test_codegen_integer(self):
        node = IntegerNode(val=5)
        codegen = CodeGenerator(node)
        codegen.visit(node)
        expected_instr = "\tmov rax, 11" # 5 * 2 + 1 = 11
        self.assertIn(expected_instr, codegen.generated_code)

    def test_codegen_boolean_constants(self):
        true_node = BoolNode(flag=True)
        codegen = CodeGenerator(true_node)
        codegen.visit(true_node)
        self.assertIn(f"\tmov rax,{CodeGenerator.TRUE_VAL}", codegen.generated_code)

    def test_codegen_stack_allocation(self):
        node = LetNode(name="a", name_expr=IntegerNode(val=10), let_expr=IdentifierNode(name="a"))
        codegen = CodeGenerator(node)
        codegen.visit(node)
        self.assertTrue(any("rbp -" in instr for instr in codegen.generated_code))
def test_func_def_codegen(self):
        """Verify that a function definition generates entry labels, stack setup, parameter storing, and ret."""
        # Function: (def inc_val (x : int) : int (+ x 1))
        func_node = FuncDefNode(
            function_name="inc_val",
            parameter_name="x",
            parameter_type=TypeNode("int"),
            return_type=TypeNode("int"),
            body_expr=AddNode(
                left_expr=IdentifierNode(name="x"),
                right_expr=IntegerNode(val=1)
            )
        )
        
        generator = CodeGenerator(func_node)
        generator.visit(func_node)
        
        code_str = "\n".join(generator.generated_code)

        # 1. Label check
        self.assertIn("snek_func_inc_val:", code_str)
        # 2. Frame setup & Parameter receiving from rdi
        self.assertIn("push rbp", code_str)
        self.assertIn("mov rbp, rsp", code_str)
        self.assertIn("mov [rbp - 8], rdi", code_str)
        # 3. Cleanup & Return
        self.assertIn("mov rsp, rbp", code_str)
        self.assertIn("pop rbp", code_str)
        self.assertIn("ret", code_str)

    def test_call_codegen(self):
        """Verify that a function call loads arguments into rdi and executes the call instruction."""
        # Call: (inc_val 5)
        call_node = CallNode(
            function_name="inc_val",
            para_expr=IntegerNode(val=5)
        )

        generator = CodeGenerator(call_node)
        generator.visit(call_node)

        code_str = "\n".join(generator.generated_code)

        # 1. Integer literal 5 tagged value (5 * 2 + 1 = 11)
        self.assertIn("mov rax, 11", code_str)
        # 2. Pass argument to rdi
        self.assertIn("mov rdi, rax", code_str)
        # 3. Function invocation
        self.assertIn("call snek_func_inc_val", code_str)

    def test_program_codegen_structure(self):
        """Verify full ProgramNode output layout with top-level function defs and main entry point."""
        # Function: (def identity (x : int) : int x)
        func_node = FuncDefNode(
            function_name="identity",
            parameter_name="x",
            parameter_type=TypeNode("int"),
            return_type=TypeNode("int"),
            body_expr=IdentifierNode(name="x")
        )
        # Main body: (identity 10)
        main_expr = CallNode(
            function_name="identity",
            para_expr=IntegerNode(val=10)
        )

        program_node = ProgramNode(
            function_defs=[func_node],
            expr=main_expr
        )

        generator = CodeGenerator(program_node)
        generator.visit(program_node)

        code_str = "\n".join(generator.generated_code)

        # 1. Function definition appears first
        func_idx = code_str.find("snek_func_identity:")
        main_idx = code_str.find("code_starts_here:")
        
        self.assertNotEqual(func_idx, -1, "Function label missing")
        self.assertNotEqual(main_idx, -1, "Main entry point label missing")
        self.assertLess(func_idx, main_idx, "Function definition should be placed before main entry code")

        # 2. Main body invocation check
        self.assertIn("call snek_func_identity", code_str)

    def test_call_stack_alignment(self):
        """Verify stack padding behavior when stack count is odd to ensure 16-byte alignment."""
        # Call node evaluated while _stack_count is 1 (odd)
        call_node = CallNode(
            function_name="foo",
            para_expr=IntegerNode(val=1)
        )

        generator = CodeGenerator(call_node)
        generator._stack_count = 1  # Force odd stack depth
        generator.visit(call_node)

        code_str = "\n".join(generator.generated_code)

        # Should subtract and restore 8 bytes around call to align stack
        self.assertIn("sub rsp, 8", code_str)
        self.assertIn("call snek_func_foo", code_str)
        self.assertIn("add rsp, 8", code_str)

if __name__ == '__main__':
    unittest.main()
