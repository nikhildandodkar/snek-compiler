# This is a sample Python script.
import argparse
import logging
from parser import Tokenize, Parser
from typecheck import TypeChecker
from codegen import CodeGenerator

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
    
    log_level = getattr(logging, args.verbose, logging.DEBUG)
    
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

