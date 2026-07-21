import logging
from src.ast_nodes import (
    ASTNode, IntegerNode, BoolNode, IdentifierNode, IncNode, DecNode,
    AddNode, LetNode, IfNode, BinOpNode, SetNode, WhileNode, FuncDefNode, TypeNode, CallNode, ProgramNode
)

def Tokenize(sexp):
    spaced = sexp.replace('(',' ( ').replace(')',' ) ')
    return spaced.split()

class Parser:
    def __init__(self,token_list:list):
        self._token_list= token_list
        self._pos=0
        self.keywords =['let','set','while']
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
    
    def is_integer(self,s:str) -> bool:
    	return s[1:].isdigit() if s.startswith("-") else s.isdigit()

    def is_end_tokens(self):
        return self._pos > len(self._token_list)

    def parse_expression(self):
        current_token = self.get_next_token()
        logging.debug(f"[parse_expression] current_token is {current_token}")
        if self.is_integer(current_token):
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
                arg_expr=self.parse_expression()
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
                left_expr=self.parse_expression()
                right_expr=self.parse_expression()
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
                        var_expr=self.parse_expression()
                        current_token =self.get_next_token()
                        self.identifier.append(var_name)
                        if current_token == ')':
                            self.consume_token()
                            let_expr= self.parse_expression()
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
                cond_expr = self.parse_expression()
                then_expr = self.parse_expression()
                else_expr = self.parse_expression()
                return IfNode(cond_expr=cond_expr,then_expr=then_expr,else_expr=else_expr)
            elif self.is_binary_operator(current_token):
                self.consume_token()
                operator=current_token
                left_expr=self.parse_expression()
                right_expr=self.parse_expression()
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
                val_expr = self.parse_expression()
                
                current_token = self.get_next_token()
                if current_token == ')':
                    self.consume_token()
                    return SetNode(name=var_name, val_expr=val_expr)
                else:
                    raise ValueError(f"Expected ')' after set expression, found {current_token}")

            elif current_token == 'while':
                self.consume_token()
                cond_expr = self.parse_expression()
                body_expr = self.parse_expression()
                
                current_token = self.get_next_token()
                if current_token == ')':
                    self.consume_token()
                    return WhileNode(cond_expr=cond_expr, body_expr=body_expr)
                else:
                    raise ValueError(f"Expected ')' after while expression, found {current_token}")
            elif current_token == 'def':
                self.consume_token()
                function_name = self.get_next_token()
                self.consume_token()
                current_token = self.get_next_token()
                if current_token == '(':
                    self.consume_token()
                    para_name = self.get_next_token()
                    self.identifier.append(para_name)
                    self.consume_token()
                    current_token = self.get_next_token()
                    if current_token == ':':
                        self.consume_token()
                        current_token = self.get_next_token()
                        para_type=TypeNode(type_name=current_token)
                        self.consume_token()
                        current_token = self.get_next_token()
                        if current_token == ')':
                            self.consume_token()
                            current_token = self.get_next_token()
                            if current_token == ':':
                                self.consume_token()
                                current_token = self.get_next_token()
                                return_type=TypeNode(type_name=current_token)
                                self.consume_token()
                                body_expr = self.parse_expression()
                                current_token = self.get_next_token()
                                if current_token == ')':
                                    self.consume_token()
                                    return FuncDefNode(function_name = function_name, parameter_name = para_name,parameter_type = para_type,return_type = return_type ,body_expr = body_expr )
                                else:
                                    raise ValueError(f"Expected ')' after while expression, found {current_token}")
                            else:
                                raise ValueError(f"Incorrect expression.unexpected charater found {current_token}")
                        else:
                            raise ValueError(f"Incorrect expression.unexpected charater found {current_token}")
                    else:
                        raise ValueError(f"Incorrect expression.unexpected charater found {current_token}")
                else:
                     raise ValueError(f"Incorrect expression.unexpected charater found {current_token}")

            else:
              function_name=current_token
              self.consume_token()
              para_expr=self.parse_expression()
              return CallNode(function_name = function_name, para_expr = para_expr)


 
    def parse(self):
        function_list=[]
        while not self.is_end_tokens():
            expr = self.parse_expression()
            if isinstance(expr,FuncDefNode):
                function_list.append(expr)
            else:
                return ProgramNode(function_defs=function_list,expr=expr)
        raise ValueError(f"no body expression to execute")
