#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import ast


class AttributeVisitor(ast.NodeVisitor):

    def __init__(self):
        self.deps = set()
        self.attr = None

    def visit_Attribute(self, node):
        self.attr = node.attr
        self.visit(node.value)

    def visit_Name(self, node):
        attr = self.attr
        if attr is not None:
            self.deps.add((node.id, attr))
        else:
            self.attr = None
        
    def results(self):
        return list(self.deps)


