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

if __name__ == '__main__':
    unittest.main()
