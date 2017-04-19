import ast
from .compiler import Compiler

def compile(file):
    compiler = Compiler()
    return compiler.compile(ast.parse("\n".join(open(file).readlines())))