import unittest
from src.typecheck import TypeChecker, TypeKind
from src.ast_nodes import IntegerNode, BoolNode, AddNode, IfNode

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

if __name__ == '__main__':
    unittest.main()
