#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
class EnamlASTNode(object):

    __slots__ = ()

    def __repr__(self):
        return self.__class__.__name__

    def __str__(self):
        return repr(self)
            

class EnamlModule(EnamlASTNode):
    
    __slots__ = ('doc', 'body',)

    def __init__(self, doc, body):
        self.doc = doc
        self.body = body


class EnamlImport(EnamlASTNode):

    __slots__ = ('py_ast',)

    def __init__(self, py_ast):
        self.py_ast = py_ast


class EnamlRawPython(EnamlASTNode):

    __slots__ = ('py_txt',)

    def __init__(self, py_txt):
        self.py_txt = py_txt


class EnamlDefine(EnamlASTNode):

    __slots__ = ('name', 'parameters', 'doc', 'body')

    def __init__(self, name, parameters, doc, body):
        self.name = name
        self.parameters = parameters
        self.doc = doc
        self.body = body


class EnamlCall(EnamlASTNode):

    __slots__ = ('name', 'arguments', 'unpack', 'captures', 'body')

    def __init__(self, name, arguments, unpack, captures, body):
        self.name = name
        self.arguments = arguments
        self.unpack = unpack
        self.captures = captures
        self.body = body


class EnamlParameters(EnamlASTNode):

    __slots__ = ('args', 'defaults')
    
    def __init__(self, args, defaults):
        self.args = args
        self.defaults = defaults
        

class EnamlArgument(EnamlASTNode):    

    __slots__ = ('py_ast',)

    def __init__(self, py_ast):
        self.py_ast = py_ast


class EnamlKeywordArgument(EnamlASTNode):

    __slots__ = ('name', 'py_ast')

    def __init__(self, name, py_ast):
        self.name = name
        self.py_ast = py_ast
    

class EnamlCapture(EnamlASTNode):

    __slots__ = ('ns_name', 'name')

    def __init__(self, ns_name, name):
        self.ns_name = ns_name
        self.name = name


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

