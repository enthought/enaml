#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Terminal Op Tokens
#------------------------------------------------------------------------------
DEFAULT = 0

BIND = 1

DELEGATE = 2

NOTIFY = 3


#------------------------------------------------------------------------------
# AST nodes
#------------------------------------------------------------------------------
class EnamlASTNode(object):

    __slots__ = ()

    def __repr__(self):
        return self.__class__.__name__

    def __str__(self):
        return repr(self)
            

class EnamlModule(EnamlASTNode):
    
    __slots__ = ('body',)

    def __init__(self, body):
        self.body = body


class EnamlImport(EnamlASTNode):

    __slots__ = ('py_ast')

    def __init__(self, py_ast):
        self.py_ast = py_ast


class EnamlDefine(EnamlASTNode):

    __slots__ = ('name', 'parameters', 'body')

    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body


class EnamlCall(EnamlASTNode):

    __slots__ = ('name', 'arguments', 'unpack', 'body')
    def __init__(self, name, arguments, unpack, body):
        self.name = name
        self.arguments = arguments
        self.unpack = unpack
        self.body = body


class EnamlParameters(EnamlASTNode):

    __slots__ = ('args', 'defaults')
    
    def __init__(self, args, defaults):
        self.args = args
        self.defaults = defaults
        

class EnamlArgument(EnamlASTNode):    

    __slots__ = ('py_ast')

    def __init__(self, py_ast):
        self.py_ast = py_ast


class EnamlKeywordArgument(EnamlASTNode):

    __slots__ = ('name', 'py_ast')

    def __init__(self, name, py_ast):
        self.name = name
        self.py_ast = py_ast
    

class EnamlAssignment(EnamlASTNode):

    __slots__ = ('lhs', 'op', 'rhs')

    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs


class EnamlName(EnamlASTNode):

    __slots__ = ('name',)

    def __init__(self, name):
        self.name = name


class EnamlGetattr(EnamlASTNode):

    __slots__ = ('root', 'attr')

    def __init__(self, root, attr):
        self.root = root
        self.attr = attr


class EnamlIndex(EnamlASTNode):

    __slots__ = ('name', 'idx')

    def __init__(self, name, idx):
        self.name = name
        self.idx = idx


class EnamlExpression(EnamlASTNode):

    __slots__ = ('py_ast',)

    def __init__(self, py_ast):
        self.py_ast = py_ast

