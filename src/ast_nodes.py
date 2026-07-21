from dataclasses import dataclass

@dataclass 
class ASTNode:
    pass

@dataclass 
class AddNode(ASTNode):
    left_expr:ASTNode
    right_expr:ASTNode

@dataclass 
class IncNode(ASTNode):
    arg_expr:ASTNode

@dataclass 
class DecNode(ASTNode):
    arg_expr:ASTNode

@dataclass 
class IntegerNode(ASTNode):
    val:int

@dataclass 
class LetNode(ASTNode):
    name:str
    name_expr:ASTNode
    let_expr:ASTNode
 
@dataclass 
class IdentifierNode(ASTNode):
    name:str

@dataclass 
class IfNode(ASTNode):
    cond_expr:ASTNode
    then_expr:ASTNode
    else_expr:ASTNode

@dataclass 
class BinOpNode(ASTNode):
    operator:str
    left_expr:ASTNode
    right_expr:ASTNode

@dataclass 
class BoolNode(ASTNode):
    flag:bool

@dataclass 
class SetNode(ASTNode):
    name: str
    val_expr: ASTNode

@dataclass 
class WhileNode(ASTNode):
    cond_expr: ASTNode
    body_expr: ASTNode

@dataclass 
class TypeNode(ASTNode):
    type_name:str

@dataclass 
class FuncDefNode(ASTNode):
    function_name:str
    parameter_name:str
    parameter_type:TypeNode
    return_type:TypeNode
    body_expr:ASTNode

@dataclass 
class CallNode(ASTNode):
    function_name:str 
    para_expr: ASTNode

@dataclass 
class ProgramNode(ASTNode):
    function_defs:[FuncDefNode]
    expr: ASTNode

