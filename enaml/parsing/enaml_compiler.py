from itertools import chain

#-------------------------------------------------------------------------------
# Instructions
#-------------------------------------------------------------------------------
START_COMPONENT = 1

END_COMPONENT = 2

DEFAULT_EXPRESSION = 3

BIND_EXPRESSION = 4

DELEGATE_EXPRESSION = 5

NOTIFY_EXPRESSION = 6

CALL_FACTORY = 7


class EnamlCompiler(object):

    @classmethod
    def instance(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance

    @classmethod
    def compile(cls, defn_ast):
        visitor = cls.instance()
        instructions = []
        visitor.visit(defn_ast, instructions)
        return instructions

    def visit(self, node, instructions):
        name = 'visit_%s' % node.__class__.__name__
        method = getattr(self, name, self.default_visit)
        method(node, instructions)

    def default_visit(self, node, instructions):
        raise ValueError('Unhandled Node %s.' % node)

    def visit_EnamlDefine(self, node, instructions):
        self.visit(node.component, instructions)
    
    def visit_EnamlCall(self, node, instructions):
        instruction = (CALL_FACTORY, (node.name, node.arguments))
        instructions.append(instruction)

    def visit_EnamlComponent(self, node, instructions):
        instruction = (START_COMPONENT, (node.name, node.identifier))
        instructions.append(instruction)
        self.visit(node.body, instructions)
        instruction = (END_COMPONENT, ())
        instructions.append(instruction)

    def visit_EnamlComponentBody(self, node, instructions):
        for item in chain(node.expressions, node.children):
            self.visit(item, instructions)

    def visit_EnamlExpression(self, node, instructions):
        ctxt = (node.lhs, node.rhs.py_ast)
        op = node.op
        if op == node.DEFAULT:
            instruction = (DEFAULT_EXPRESSION, ctxt)
        elif op == node.BIND:
            instruction = (BIND_EXPRESSION, ctxt)
        elif op == node.DELEGATE:
            instruction = (DELEGATE_EXPRESSION, ctxt)
        elif op == node.NOTIFY:
            instruction = (NOTIFY_EXPRESSION, ctxt)
        else:
            raise ValueError('Invalid expression op.')
        instructions.append(instruction)

