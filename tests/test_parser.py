import unittest
from src.parser import Tokenize, Parser
from src.ast_nodes import IntegerNode, BoolNode, AddNode, LetNode, IdentifierNode, FuncDefNode, TypeNode, CallNode, ProgramNode

class TestSnekParser(unittest.TestCase):
    def test_parse_expression_integer(self):
        tokens = Tokenize("42")
        parser = Parser(tokens)
        ast = parser.parse_expression()
        self.assertIsInstance(ast, IntegerNode)
        self.assertEqual(ast.val, 42)

    def test_parse_expression_boolean_true(self):
        tokens = Tokenize("true")
        parser = Parser(tokens)
        ast = parser.parse_expression()
        self.assertIsInstance(ast, BoolNode)
        self.assertTrue(ast.flag)

    def test_parse_expression_addition(self):
        tokens = Tokenize("(+ 5 10)")
        parser = Parser(tokens)
        ast = parser.parse_expression()
        self.assertIsInstance(ast, AddNode)
        self.assertEqual(ast.left_expr.val, 5)
        self.assertEqual(ast.right_expr.val, 10)

    def test_parse_expression_let_binding(self):
        tokens = Tokenize("(let (x 1) x)")
        parser = Parser(tokens)
        ast = parser.parse_expression()
        self.assertIsInstance(ast, LetNode)
        self.assertEqual(ast.name, "x")
        self.assertIsInstance(ast.name_expr, IntegerNode)
        self.assertIsInstance(ast.let_expr, IdentifierNode)

    def test_parse_expression_invalid_syntax_throws_error(self):
        tokens = Tokenize("(+ 1")
        parser = Parser(tokens)
        with self.assertRaises(IndexError):
            parser.parse_expression()

    def test_parse_expression_func_def(self):
        # Hypothetical S-exp: (def f (x : int) : int (+ x 1))
        # You will need to ensure your parser handles the structural details
        tokens = Tokenize("(def f (x : int) : int (+ x 1))")
        parser = Parser(tokens)
        ast = parser.parse_expression()
        
        self.assertIsInstance(ast, FuncDefNode)
        self.assertEqual(ast.function_name, "f")
        self.assertEqual(ast.parameter_name, "x")
        self.assertEqual(ast.parameter_type.type_name, "int")
        self.assertEqual(ast.return_type.type_name, "int")
        self.assertIsInstance(ast.body_expr, AddNode)

    def test_parse_expression_call(self):
        # Hypothetical S-exp: (f 5)
        tokens = Tokenize("(f 5)")
        parser = Parser(tokens)
        ast = parser.parse_expression()
        
        self.assertIsInstance(ast, CallNode)
        self.assertEqual(ast.function_name, "f")
        self.assertIsInstance(ast.para_expr, IntegerNode)

    def test_parse_program(self):
        # A program with a function definition and a main expression
        tokens = Tokenize("(def f (x : int) : int x) (f 10)")
        parser = Parser(tokens)
        ast = parser.parse()
        
        self.assertIsInstance(ast, ProgramNode)
        self.assertEqual(len(ast.function_defs), 1)
        self.assertIsInstance(ast.expr, CallNode)
if __name__ == '__main__':
    unittest.main()
