from functools import singledispatchmethod
import logging
from src.ast_nodes import (
    ASTNode, AddNode, IncNode, DecNode, IntegerNode, LetNode, IdentifierNode, IfNode, BoolNode, BinOpNode, SetNode, WhileNode
)

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
            for instructions in self.generated_code:
                asm_file.write(instructions +"\n")
            logging.info(f"assembly file is generated")
    
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
        
        # self.add_instruction(f"push rax")
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

    @visit.register(FuncDefNode)
    def _visit_funcdef(self, node):
        old_var_map = self.variable_map.copy()
        old_stack_count = self._stack_count
        self.generated_code.append(f"{node.function_name}_snek:\n")
        self.generated_code.append(f"\tpush rbp \n")
        self.generated_code.append(f"\tmov rbp, rsp\n")
        self._stack_count=0
        self.variable_map[node.parameter_name]=self._stack_count+1
        self.generated_code.append(f"\tpush rdi\n")
        self.visit(node.body_expr)
        self.generated_code.append(f"\tmov rsp, rbp\n")
        self.generated_code.append(f"\tpop rbp\n")
        self.generated_code.append(f"\tret\n")
        self._stack_count = old_stack_count
        self.variable_map = old_var_map

    @visit.register(CallNode)
    def _visit_call(self, node):
        self.visit(node.para_expr)
        self.add_instruction(f"mov rdi, rax\n")
        # align stack 16 byte
        pad_stack = self._stack_count%2 != 0
        if pad_stack:
            self.add_instruction(f"sub rsp, 8")
        self.add_instruction(f"call {node.function_name}_snek \n")
        if pad_stack:
            self.add_instruction(f"add rsp, 8")

    @visit.register(ProgramNode)
    def _visit_program(self, node):
        self.generated_code.append(f"section .text\n")
        self.generated_code.append(f"global code_starts_here:\n")
        for func in node.function_defs:
            self.visit(func)

        self.generated_code.append(f"code_starts_here:\n")
        self.generated_code.append(f"\t push rbp \n")
        self.generated_code.append(f"\t mov rbp, rsp\n")
        self.visit(node.expr)
        self.generated_code.append(f"\t mov rsp, rbp\n")
        self.generated_code.append(f"\t pop rbp\n")
        self.generated_code.append(f"\t ret\n")
