import unittest
from src.parser import Tokenize, Parser
from src.ast_nodes import IntegerNode, BoolNode, AddNode, LetNode, IdentifierNode

class TestSnekParser(unittest.TestCase):
    def test_parse_integer(self):
        tokens = Tokenize("42")
        parser = Parser(tokens)
        ast = parser.parse()
        self.assertIsInstance(ast, IntegerNode)
        self.assertEqual(ast.val, 42)

    def test_parse_boolean_true(self):
        tokens = Tokenize("true")
        parser = Parser(tokens)
        ast = parser.parse()
        self.assertIsInstance(ast, BoolNode)
        self.assertTrue(ast.flag)

    def test_parse_addition(self):
        tokens = Tokenize("(+ 5 10)")
        parser = Parser(tokens)
        ast = parser.parse()
        self.assertIsInstance(ast, AddNode)
        self.assertEqual(ast.left_expr.val, 5)
        self.assertEqual(ast.right_expr.val, 10)

    def test_parse_let_binding(self):
        tokens = Tokenize("(let (x 1) x)")
        parser = Parser(tokens)
        ast = parser.parse()
        self.assertIsInstance(ast, LetNode)
        self.assertEqual(ast.name, "x")
        self.assertIsInstance(ast.name_expr, IntegerNode)
        self.assertIsInstance(ast.let_expr, IdentifierNode)

    def test_parse_invalid_syntax_throws_error(self):
        tokens = Tokenize("(+ 1")
        parser = Parser(tokens)
        with self.assertRaises(IndexError):
            parser.parse()

if __name__ == '__main__':
    unittest.main()
