import ast


class AttributeVisitor(ast.NodeVisitor):

    def __init__(self):
        self.deps = set()
        self.current = []

    def visit_Attribute(self, node):
        self.current.append(node.attr)
        self.visit(node.value)

    def visit_Name(self, node):
        self.deps.add((node.id, tuple(reversed(self.current))))
        self.current = []
        
    def generic_visit(self, node):
        self.current = []
        super(AttributeVisitor, self).generic_visit(node)

    def results(self):
        return tuple(self.deps)

