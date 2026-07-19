from functools import singledispatchmethod
from enum import Enum, auto
import logging
from src.ast_nodes import (
    ASTNode, BoolNode, IntegerNode, AddNode, BinOpNode, IfNode, LetNode, IdentifierNode, SetNode, WhileNode
)

class TypeKind(Enum):
    INT=auto()
    BOOL=auto()

class TypeChecker:
    def __init__(self, root_node: "ASTNode"):
        # Correct PEP 8 attribute naming
        self.ast_node = root_node
        self.variable_map = {}

    def add_to_map(self, var_name, type_kind):
        self.variable_map[var_name]=type_kind
    
    def typecheck(self):
        self.visit(self.ast_node)
        
    @singledispatchmethod
    def visit(self, node):
        """This is the generic fallback method."""
        raise TypeError(f"No visitor registered for {type(node)} or a invalid node")

    @visit.register(ASTNode)
    def _visit_ast(self, node):
        # Python 3 equivalent of map(self.visit, node.children)
        for child in node.children:
            self.visit(child)

    @visit.register(BoolNode)
    def _visit_bool(self, node):
        return TypeKind.BOOL

    @visit.register(IntegerNode)
    def _visit_constant(self, node):
        return TypeKind.INT

    @visit.register(AddNode)
    def _visit_binary(self, node):
        left_expr=self.visit(node.left_expr)
        right_expr=self.visit(node.right_expr)
        if left_expr == TypeKind.INT and right_expr == TypeKind.INT:
            return TypeKind.INT
        else:
            raise TypeError(f"cannot add {left_expr} and {right_expr}")

    @visit.register(BinOpNode)
    def _visit_bin_op(self, node):
        left_expr = self.visit(node.left_expr)
        right_expr = self.visit(node.right_expr)
        if left_expr == TypeKind.INT and right_expr == TypeKind.INT:
            return TypeKind.BOOL
        else:
            raise TypeError(f"cannot {node.operator} on {left_expr} and {right_exp}")
    
    @visit.register(IfNode)
    def _visit_if(self,node):
        cond_expr = self.visit(node.cond_expr)
        if cond_expr == TypeKind.BOOL:
            then_expr = self.visit(node.then_expr)
            else_expr = self.visit(node.else_expr)
            if then_expr == else_expr :
                return then_expr
            else:
                raise TypeError(f"branches have different type")
        else:
            raise TypeError(f"condition expression in not bool type")

    @visit.register(LetNode)
    def _visit_let(self, node):
        name_expr = self.visit(node.name_expr)
        self.variable_map[node.name]=name_expr
        logging.debug(f" name_expr type is {name_expr} and name_expr is {node.name_expr}")
        let_expr = self.visit(node.let_expr)
        return let_expr

    @visit.register(IdentifierNode)
    def _visit_id(self, node):
        logging.debug(f" node.name is {node.name} and node.name type is {self.variable_map[node.name]}")
        return self.variable_map[node.name]
    
    @visit.register(SetNode)
    def _visit_set(self, node):
        if node.name not in self.variable_map:
            raise TypeError(f"Undefined variable mutation: {node.name}")
        
        val_type = self.visit(node.val_expr)
        expected_type = self.variable_map[node.name]
        
        if val_type != expected_type:
            raise TypeError(f"Cannot assign type {val_type} to variable '{node.name}' of type {expected_type}")
            
        return val_type

    @visit.register(WhileNode)
    def _visit_while(self, node):
        cond_type = self.visit(node.cond_expr)
        if cond_type != TypeKind.BOOL:
            raise TypeError(f"Loop condition must be a BOOL, got {cond_type}")
        self.visit(node.body_expr)
        return TypeKind.BOOL

