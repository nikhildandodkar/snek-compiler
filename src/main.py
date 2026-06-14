# This is a sample Python script.
from dataclasses import dataclass
from functools import singledispatchmethod
from enum import Enum
import logging
import argparse


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# BACKUS NAUR FORM
# expr := <number>
#       | <identifier>
#       | (<op> <expr>)
#       | (let (name <expr>) <expr>)
#       | (+ <expr> <expr>)
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

def Tokenize(sexp):
    spaced = sexp.replace('(',' ( ').replace(')',' ) ')
    return spaced.split()
class Parser:
    def __init__(self,token_list:list):
        self._token_list= token_list
        self._pos=0
        self.keywords =['let']
        self.identifier=[]

    def get_next_token(self)->str|None:
        logging.debug(f"[get_next_token] positon is {self._pos}")
        if self._pos > len(self._token_list):
            return None
        else:
            return self._token_list[self._pos]
    def consume_token(self):
        self._pos+=1
        logging.debug(f"[consume_token] position is {self._pos}")

    def parse(self):
        current_token = self.get_next_token()
        logging.debug(f"[parse] current_token is {current_token}")
        if current_token.isdecimal():
            self.consume_token()
            return IntegerNode(val=int(current_token))
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
            else:
                raise ValueError(f"Incorrect expression.unexpected charater found {current_token}")

class CodeGenerator:
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
        val = 8*self._stack_count
        self._stack_count-=1
        return val

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
        self.add_instruction(f"add rax,[rbp - {self.pop_variable()}]")
        logging.debug(f"add rax,[rbp - ]")

    @visit.register(IncNode)
    def _visit_constant(self, node):
        self.visit(node.arg_expr)
        self.add_instruction(f"add rax, 1")
        logging.debug(f"add rax, 1")

    @visit.register(DecNode)
    def _visit_constant(self, node):
        self.visit(node.arg_expr)
        self.add_instruction(f"sub rax, 1")
        logging.debug(f"sub rax, 1")

    @visit.register(IntegerNode)
    def _visit_constant(self, node):
        integer_node_code=f"mov rax, {node.val}"
        self.add_instruction(integer_node_code)
        logging.debug(f"mov rax, {node.val}")

    @visit.register(LetNode)
    def _visit_let(self, node):
        self.visit(node.name_expr)
        self.variable_map[node.name]=self._stack_count+1
        self.add_instruction(f"mov [rbp - {self.push_variable()}], rax")
        self.visit(node.let_expr)


    @visit.register(IdentifierNode)
    def _visit_let(self, node):
        self.add_instruction(f"mov rax,[rbp -{8*self.variable_map[node.name]}]")

    @visit.register(IfNode)
    def _visit_let(self, node):
        self.visit(node.cond_expr)
        self.add_instruction(f"cmp rax,0")
        self.add_instruction(f"je else_of_if_{self._label_num+1}")
        self.visit(node.then_expr)
        self.add_instruction(f"jmp end_of_if_{self._label_num+2}")
        self.add_label(f"else_of_if")
        self.visit(node.else_expr)
        self.add_label(f"end_of_if")

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description="This is itercompiler which compiles s-expression")
    arg_parser.add_argument("file_path",help="file to compile")
    arg_parser.add_argument("--verbose",help="verbose level for logging")
    arg_parser.parse_args()
    args=arg_parser.parse_args()
    with open(file=args.file_path,mode="r") as file:
        source_code=file.read()
    logging.basicConfig(filename='compiler.log', level=logging.INFO)
    if not source_code:
        source_code= "(+(inc 3) (dec 5))"
    tokens = Tokenize(source_code)
    logging.debug(f'tokens are {tokens}')
    parser = Parser(tokens)
    ast_root_node = parser.parse()
    code_gen = CodeGenerator(ast_root_node)
    code_gen.generate()
    
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
