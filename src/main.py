# This is a sample Python script.
from dataclasses import dataclass
from functools import singledispatchmethod
from enum import Enum, auto
import logging
import argparse


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# BACKUS NAUR FORM
# expr := <number>
#       | true
#       | false
#       | <identifier>
#       | (<op> <expr>)
#       | (let (name <expr>) <expr>)
#       | (+ <expr> <expr>)
#       | (if <expr> <expr> <expr>)
# op:= inc
#   | dec

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

def Tokenize(sexp):
    spaced = sexp.replace('(',' ( ').replace(')',' ) ')
    return spaced.split()

class Parser:
    def __init__(self,token_list:list):
        self._token_list= token_list
        self._pos=0
        self.keywords =['let']
        self.identifier=[]
        self.binary_operator=['<','>','==']

    def get_next_token(self)->str|None:
        logging.debug(f"[get_next_token] positon is {self._pos}")
        if self._pos > len(self._token_list):
            return None
        else:
            return self._token_list[self._pos]
    def consume_token(self):
        self._pos+=1
        logging.debug(f"[consume_token] position is {self._pos}")

    def is_binary_operator(self,token):
        return token in self.binary_operator

    def parse(self):
        current_token = self.get_next_token()
        logging.debug(f"[parse] current_token is {current_token}")
        if current_token.isdecimal():
            self.consume_token()
            return IntegerNode(val=int(current_token))
        elif current_token == 'true':
            self.consume_token()
            return BoolNode(flag=True)
        elif current_token == 'false':
            self.consume_token()
            return BoolNode(flag=False)
        elif current_token in self.identifier:
            self.consume_token()
            return IdentifierNode(name=current_token)
        elif current_token == '(':
            self.consume_token()
            current_token = self.get_next_token()
            if current_token == 'inc' or current_token == 'dec':
                op_token = current_token
                self.consume_token()
                arg_expr=self.parse()
                current_token=self.get_next_token()
                if current_token == ')':
                    self.consume_token()
                    if op_token == 'inc':
                        return IncNode(arg_expr=arg_expr)
                    else:
                        return DecNode(arg_expr=arg_expr)
                else:
                    raise ValueError(f"Incorrect expression.unexpected charater found {current_token}")
            elif current_token == '+':
                self.consume_token()
                left_expr=self.parse()
                right_expr=self.parse()
                current_token = self.get_next_token()
                if current_token == ')':
                    self.consume_token()
                    return AddNode(left_expr=left_expr,right_expr=right_expr)
                else:
                    raise ValueError(f"Incorrect expression.unexpected charater found {current_token}")
            elif current_token == 'let':
                self.consume_token()
                current_token = self.get_next_token()
                if current_token == '(':
                    self.consume_token()
                    current_token = self.get_next_token()
                    if current_token not in self.keywords:
                        var_name=current_token
                        self.consume_token()
                        var_expr=self.parse()
                        current_token =self.get_next_token()
                        self.identifier.append(var_name)
                        if current_token == ')':
                            self.consume_token()
                            let_expr= self.parse()
                            current_token = self.get_next_token()
                            if current_token == ')':
                                self.consume_token()
                                return LetNode(name=var_name,name_expr=var_expr,let_expr=let_expr)
                            else:
                                raise ValueError(f"unexpected charater found {current_token}")
                        else:
                            raise ValueError(f"unexpected charater found {current_token}")
                    else:
                        raise ValueError(f"not a valid variable name {current_token}")
                else:
                    raise ValueError(f"unexpected charater found {current_token}")

            elif current_token == 'if':
                self.consume_token()
                cond_expr = self.parse()
                then_expr = self.parse()
                else_expr = self.parse()
                return IfNode(cond_expr=cond_expr,then_expr=then_expr,else_expr=else_expr)
            elif self.is_binary_operator(current_token):
                self.consume_token()
                operator=current_token
                left_expr=self.parse()
                right_expr=self.parse()
                current_token = self.get_next_token()
                if current_token == ')':
                    self.consume_token()
                    return BinOpNode(operator=operator,left_expr=left_expr,right_expr=right_expr)
                else:
                    raise ValueError(f"Incorrect expression.unexpected charater found {current_token}")
            elif current_token == 'set':
                self.consume_token()
                var_name = self.get_next_token()
                # Ensure it's a known identifier and not a keyword
                if var_name in self.keywords:
                    raise ValueError(f"Cannot assign to a keyword: {var_name}")
                
                self.consume_token()
                val_expr = self.parse()
                
                current_token = self.get_next_token()
                if current_token == ')':
                    self.consume_token()
                    return SetNode(name=var_name, val_expr=val_expr)
                else:
                    raise ValueError(f"Expected ')' after set expression, found {current_token}")

            elif current_token == 'while':
                self.consume_token()
                cond_expr = self.parse()
                body_expr = self.parse()
                
                current_token = self.get_next_token()
                if current_token == ')':
                    self.consume_token()
                    return WhileNode(cond_expr=cond_expr, body_expr=body_expr)
                else:
                    raise ValueError(f"Expected ')' after while expression, found {current_token}")
            else:
                raise ValueError(f"Incorrect expression.unexpected charater found {current_token}")
            

class CodeGenerator:
    TRUE_VAL  = 0xfffffffffffffffe
    FALSE_VAL = 0x7ffffffffffffffe
    def __init__(self, root_node: "ASTNode"):
        # Correct PEP 8 attribute naming
        self.ast_node = root_node
        self._stack_count=0;
        self.generated_code = []
        self.variable_map = {}
        self._label_num=-1

    def add_instruction(self,str):
        self.generated_code.append("\t"+str)
    
    def add_label(self,str):
        self._label_num+=1
        self.generated_code.append(f"{str}_{self._label_num}:")
    
    def push_variable(self):
        self._stack_count+=1
        return 8*self._stack_count
    
    def pop_variable(self):
        self._stack_count-=1

    def top_variable(self):
        return 8*self._stack_count

    def generate(self) -> str:
        # Example processing method
        self.visit(self.ast_node)
        print(self.generated_code)
        with open(file="generated_code.asm",mode="w") as asm_file:
            asm_file.write(f"section .text\n")
            asm_file.write(f"global code_starts_here:\n")
            asm_file.write(f"code_starts_here:\n")
            asm_file.write(f"\t push rbp \n")
            asm_file.write(f"\t mov rbp, rsp\n")
            for instructions in self.generated_code:
                asm_file.write(instructions +"\n")
            logging.info(f"assembly file is generated")
            asm_file.write(f"\t mov rsp, rbp\n")
            asm_file.write(f"\t pop rbp\n")
            asm_file.write(f"\t ret\n")
    
    @singledispatchmethod
    def visit(self, node):
        """This is the generic fallback method."""
        raise TypeError(f"No visitor registered for {type(node)}")

    @visit.register(ASTNode)
    def _visit_ast(self, node):
        # Python 3 equivalent of map(self.visit, node.children)
        for child in node.children:
            self.visit(child)

    @visit.register(AddNode)
    def _visit_binary(self, node):
        self.visit(node.left_expr)
        self.add_instruction(f"mov [rbp - {self.push_variable()}], rax")
        logging.debug(f"push rax")
        self.visit(node.right_expr)
        self.add_instruction(f"and rax,{self.TRUE_VAL}")
        self.add_instruction(f"add rax,[rbp - {self.top_variable()}]")
        logging.debug(f"add rax,[rbp - {self.top_variable()}]")
        self.pop_variable()

    @visit.register(IncNode)
    def _visit_constant(self, node):
        self.visit(node.arg_expr)
        self.add_instruction(f"add rax, 2")
        logging.debug(f"add rax, 1")

    @visit.register(DecNode)
    def _visit_constant(self, node):
        self.visit(node.arg_expr)
        self.add_instruction(f"sub rax, 2")
        logging.debug(f"sub rax, 1")

    @visit.register(IntegerNode)
    def _visit_constant(self, node):
        integer_node_code=f"mov rax, {node.val*2+1}"
        self.add_instruction(integer_node_code)
        logging.debug(f"mov rax, {node.val}")

    @visit.register(LetNode)
    def _visit_let(self, node):
        self.visit(node.name_expr)
        self.variable_map[node.name]=self._stack_count+1
        self.add_instruction(f"mov [rbp - {self.push_variable()}], rax")
        self.visit(node.let_expr)


    @visit.register(IdentifierNode)
    def _visit_id(self, node):
        self.add_instruction(f"mov rax,[rbp -{8*self.variable_map[node.name]}]")

    @visit.register(IfNode)
    def _visit_if(self, node):
        self.visit(node.cond_expr)
        self.add_instruction(f"cmp rax,0")
        self.add_instruction(f"je else_of_if_{self._label_num+1}")
        self.visit(node.then_expr)
        self.add_instruction(f"jmp end_of_if_{self._label_num+2}")
        self.add_label(f"else_of_if")
        self.visit(node.else_expr)
        self.add_label(f"end_of_if")

    @visit.register(BoolNode)
    def _visit_bool(self, node):
        if node.flag: 
            self.add_instruction(f"mov rax,{self.TRUE_VAL}")
        else:
            self.add_instruction(f"mov rax,{self.FALSE_VAL}")

    @visit.register(BinOpNode)
    def _visit_bin_op(self, node):
        self.visit(node.left_expr)
        self.add_instruction(f"mov [rbp - {self.push_variable()}], rax")
        self.visit(node.right_expr)
        if node.operator == '<':
            self.add_instruction(f"sub [rbp -{self.top_variable()}],rax")
            self.add_instruction(f"mov rax,[rbp -{self.top_variable()}]")
        elif node.operator == '>':
            self.add_instruction(f"sub rax,[rbp - {self.top_variable()}]")
        elif node.operator == '==':
            self.add_instruction(f"sub rax,[rbp - {self.top_variable()}]")
        self.pop_variable()
        self.add_instruction(f"shr rax,63")
    
    @visit.register(SetNode)
    def _visit_set(self, node):
        self.visit(node.val_expr)
        stack_offset = 8 * self.variable_map[node.name]
        self.add_instruction(f"mov [rbp - {stack_offset}], rax")

    @visit.register(WhileNode)
    def _visit_while(self, node):
        self._label_num += 1
        loop_start = f"while_start_{self._label_num}"
        loop_end = f"while_end_{self._label_num}"
        self.generated_code.append(f"{loop_start}:")
        self.visit(node.cond_expr)
        self.add_instruction(f"cmp rax, 0") 
        self.add_instruction(f"je {loop_end}") # If condition evaluation fails, escape loop block
        self.visit(node.body_expr)
        self.add_instruction(f"jmp {loop_start}")
        self.generated_code.append(f"{loop_end}:")
        self.add_instruction(f"mov rax,{self.FALSE_VAL}")

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

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description="This is snek compiler which compiles s-expression")
    arg_parser.add_argument("file_path", help="file to compile")
    
    arg_parser.add_argument(
        "--verbose", 
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="WARNING",  # Default if user doesn't pass --verbose
        type=lambda s: s.upper(), 
        help="verbose level for logging"
    )
    
    args = arg_parser.parse_args()
    
    log_level = getattr(logging, args.verbose, logging.WARNING)
    
    logging.basicConfig(
        filename='compiler.log', 
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    with open(file=args.file_path, mode="r") as file:
        source_code = file.read()
        
    if not source_code.strip():
        raise ValueError(f"File is empty at {args.file_path}")
        
    tokens = Tokenize(source_code)
    logging.debug(f'tokens are {tokens}')
    
    parser = Parser(tokens)
    ast_root_node = parser.parse()
    
    type_checker = TypeChecker(ast_root_node)
    type_checker.typecheck()
    
    code_gen = CodeGenerator(ast_root_node)
    code_gen.generate()

