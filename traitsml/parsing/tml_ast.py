

class Node(object):

    def __repr__(self):
        return 'Node'

    def __str__(self):
        return repr(self)
    
    def pprint(self):
        indentor = '    '
        stack = [(0, self)]
        while stack:
            indent, item = stack.pop()
            print ((indentor * indent) + '%s' % item)
            for child in reversed(item.children):
                if isinstance(child, Node):
                    stack.append((indent + 1, child))
    
    @property
    def children(self):
        """ Return the list of child nodes to facilitate tree walking
        and pretty printing.

        """
        return []
            

class TML(Node):
    
    def __init__(self, body):
        self.body = body

    def __repr__(self):
        return 'TML'

    @property
    def children(self):
        return self.body


class TMLImport(Node):

    def __init__(self, ast_mod):
        self.ast_mod = ast_mod

    def __repr__(self):
        return 'Import'


class TMLElement(Node):

    def __init__(self, name, identifier, body):
        self.name = name
        self.identifier = identifier
        self.body = body

    def __repr__(self):
        return self.name
    
    @property
    def children(self):
        return self.body


class TMLExpr(Node):

    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    
    @property
    def children(self):
        return [self.expr]


class TMLAssign(TMLExpr):

    def __repr__(self):
        return 'Assign %s' % self.name


class TMLBind(TMLExpr):

    def __repr__(self):
        return 'Bind %s' % self.name


class TMLNotify(TMLExpr):

    def __repr__(self):
        return 'Changed %s' % self.name


class TMLDelegate(Node):
    
    def __init__(self, name, obj_name, attr_name):
        self.name = name
        self.obj_name = obj_name
        self.attr_name = attr_name

    def __repr__(self):
        return 'Delegate %s' % self.name


