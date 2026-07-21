from functools import singledispatchmethod
from enum import Enum, auto
import logging
from src.ast_nodes import (
    ASTNode, BoolNode, IntegerNode, AddNode, BinOpNode, IfNode, LetNode, IdentifierNode, SetNode, WhileNode, TypeNode, CallNode, FuncDefNode, ProgramNode
)

class TypeKind(Enum):
    INT=auto()
    BOOL=auto()

class TypeChecker:
    def __init__(self, root_node: "ASTNode"):
        # Correct PEP 8 attribute naming
        self.ast_node = root_node
        self.variable_map = {}
        self.function_map = {}

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
        if node.name in self.variable_map:
            logging.debug(f" node.name is {node.name} and node.name type is {self.variable_map[node.name]}")
            return self.variable_map[node.name]
        else:
            raise TypeError(f"variable {node.name} not defined")
    
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

    @visit.register(TypeNode)
    def _visit_typenode(self, node):
        if node.type_name == 'int':
            return TypeKind.INT
        elif node.type_name == 'bool':
            return TypeKind.BOOL
        else:
           raise TypeError(f"Unsuported type {node.type_name} found") 


    @visit.register(ProgramNode)
    def _visit_program(self, node):
        for func in node.function_defs:
            para_type = self.visit(func.parameter_type)
            return_type = self.visit(func.return_type)
            self.function_map[func.function_name]=(para_type,return_type)

        for func in node.function_defs:
            self.visit(func)
        
        self.visit(node.expr)

    @visit.register(FuncDefNode)
    def _visit_funcdef(self, node):
        expected_return_type = self.visit(node.return_type)
        param_type = self.visit(node.parameter_type)

        old_var_map = self.variable_map.copy()
        try:
            self.variable_map[node.parameter_name] = param_type
            actual_return_type = self.visit(node.body_expr)
            
            if actual_return_type != expected_return_type:
                raise TypeError(
                    f"Function '{node.function_name}' body returns {actual_return_type}, "
                    f"but expected {expected_return_type}"
                )
            return expected_return_type
        finally:
            self.variable_map = old_var_map

    @visit.register(CallNode)
    def _visit_call(self, node):
        if node.function_name not in self.function_map:
            raise TypeError(f"Call to undefined function '{node.function_name}'")

        param_type, return_type = self.function_map[node.function_name]
        arg_type = self.visit(node.para_expr)

        if arg_type != param_type:
            raise TypeError(
                f"Function '{node.function_name}' expects argument of type {param_type}, "
                f"got {arg_type}"
            )

        return return_type
