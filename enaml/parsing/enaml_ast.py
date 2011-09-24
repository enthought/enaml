#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
class EnamlASTNode(object):

    def __repr__(self):
        return self.__class__.__name__

    def __str__(self):
        return repr(self)
    
    def pprint(self):
        indentor = '    '
        stack = [(0, self)]
        while stack:
            indent, item = stack.pop()
            print ((indentor * indent) + '%s' % item)
            for child in reversed(item.node_children):
                stack.append((indent + 1, child))
    
    @property
    def node_children(self):
        return []
            

class EnamlModule(EnamlASTNode):
    
    def __init__(self, imports, components):
        self.imports = imports
        self.components = components

    @property
    def node_children(self):
        return self.imports + self.components


class EnamlPyImport(EnamlASTNode):

    def __init__(self, py_ast):
        self.py_ast = py_ast


class EnamlComponent(EnamlASTNode):

    def __init__(self, name, identifier, body):
        self.name = name
        self.identifier = identifier
        self.body = body
    
    @property
    def node_children(self):
        return [self.body]


class EnamlComponentBody(EnamlASTNode):

    def __init__(self, expressions, children):
        self.expressions = expressions
        self.children = children
    
    @property
    def node_children(self):
        return self.expressions + self.children


class EnamlExpression(EnamlASTNode):

    DEFAULT = 0

    BIND = 1

    DELEGATE = 2

    NOTIFY = 3

    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs

    @property
    def node_children(self):
        return [self.lhs, self.rhs]

    
class EnamlName(EnamlASTNode):

    def __init__(self, root, leaf):
        self.root = root
        self.leaf = leaf


class EnamlPyExpression(EnamlASTNode):

    def __init__(self, py_ast):
        self.py_ast = py_ast


class EnamlPyStatement(EnamlASTNode):

    def __init__(self, py_ast):
        self.py_ast = py_ast


class EnamlTemplate(EnamlASTNode):

    def __init__(self, names, components):
        self.names = names
        self.components = components

    @property
    def node_children(self):
        return self.names + self.components

