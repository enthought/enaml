#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
class ASTNode(object):

    __slots__ = ()

    def __repr__(self):
        return self.__class__.__name__

    def __str__(self):
        return repr(self)
            

class Module(ASTNode):
    
    __slots__ = ('doc', 'body',)

    def __init__(self, doc, body):
        self.doc = doc
        self.body = body


class _PyAST(ASTNode):

    __slots__ = ('py_ast',)

    def __init__(self, py_ast):
        self.py_ast = py_ast


class Import(_PyAST):
    __slots__ = ()


class RawPython(_PyAST):
    __slots__ = ()


class Declaration(ASTNode):

    __slots__ = ('name', 'base', 'identifier', 'doc', 'body')

    def __init__(self, name, base, identifier, doc, body):
        self.name = name
        self.base = base
        self.identifier = identifier
        self.doc = doc
        self.body = body


class Instantiation(ASTNode):

    __slots__ = ('name', 'identifier', 'body')

    def __init__(self, name, identifier, body):
        self.name = name
        self.identifier = identifier
        self.body = body


class AttributeBinding(ASTNode):

    __slots__ = ('name', 'binding')

    def __init__(self, name, binding):
        self.name = name
        self.binding = binding


class BoundExpression(ASTNode):

    __slots__ = ('op', 'expr')

    def __init__(self, op, expr):
        self.op = op
        self.expr = expr


class BoundCodeBlock(_PyAST):
    __slots__ = ()


class Defn(ASTNode):

    __slots__ = ('name', 'parameters', 'doc', 'body')

    def __init__(self, name, parameters, doc, body):
        self.name = name
        self.parameters = parameters
        self.doc = doc
        self.body = body


class Parameters(ASTNode):

    __slots__ = ('names', 'defaults')
    
    def __init__(self, names, defaults):
        self.names = names
        self.defaults = defaults
        

class Call(ASTNode):
    
    __slots__ = ('name', 'arguments')

    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class Argument(_PyAST):    
    __slots__ = ()


class KeywordArgument(ASTNode):

    __slots__ = ('name', 'py_ast')

    def __init__(self, name, py_ast):
        self.name = name
        self.py_ast = py_ast


class VarDeclare(ASTNode):

    __slots__ = ('type', 'vars')

    def __init__(self, type, vars):
        self.type = type
        self.vars = vars


class Var(ASTNode):

    __slots__ = ('name', 'default')

    def __init__(self, name, default):
        self.name = name
        self.default = default

