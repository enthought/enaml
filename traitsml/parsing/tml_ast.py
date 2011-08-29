

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

    def __init__(self, py_ast):
        self.py_ast = py_ast

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
        return [self.body]


class TMLElementBody(Node):

    def __init__(self, exprs, metas, tml_children):
        self.exprs = exprs
        self.metas = metas
        self.tml_children = tml_children
    
    def __repr__(self):
        return 'TMLElementBody'
    
    @property
    def children(self):
        return self.metas + self.exprs + self.tml_children


class TMLMeta(Node):

    def __init__(self, name, identifier, exprs):
        self.name = name
        self.identifier = identifier
        self.exprs = exprs
    
    def __repr__(self):
        return 'TMLMeta %s' % self.name
    
    @property
    def children(self):
        return self.exprs


class TMLDefault(Node):

    def __init__(self, name, py_ast):
        self.name = name
        self.py_ast = py_ast

    def __repr__(self):
        return 'Assign %s' % self.name


class TMLExprBind(Node):

    def __init__(self, name, py_ast):
        self.name = name
        self.py_ast = py_ast

    def __repr__(self):
        return 'Bind %s' % self.name


class TMLNotify(Node):

    def __init__(self, name, py_ast):
        self.name = name
        self.py_ast = py_ast

    def __repr__(self):
        return 'Changed %s' % self.name


class TMLDelegate(Node):
    
    def __init__(self, name, obj_name, attr_name):
        self.name = name
        self.obj_name = obj_name
        self.attr_name = attr_name

    def __repr__(self):
        return 'Delegate %s' % self.name

