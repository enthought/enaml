from traits.api import HasStrictTraits, Instance

from ..constructors.i_toolkit_constructor import IToolkitConstructor
from ..constructors.toolkit import default_toolkit
from ..parsing import tml_ast, tml_parser


class _ConstructorVisitor(object):

    def __init__(self, toolkit, default=None, bind=None, delegate=None, 
                 notify=None):
        self.toolkit = toolkit
        self.default = default
        self.bind = bind
        self.delegate = delegate
        self.notify = notify
        self.root = None
        self.imports = {}
        self.stack = []

    def visit(self, node):
        name = 'visit_%s' % node.__class__.__name__
        method = getattr(self, name, self.default_visit)
        method(node)

    def results(self):
        return self.root, self.imports

    def default_visit(self, node):
        for child in node.children():
            self.visit(child)

    def visit_TML(self, node):
        for item in node.body:
            self.visit(item)

    def visit_TMLImport(self, node):
        code = compile(node.py_ast, 'TML', mode='exec')
        exec code in {}, self.imports

    def visit_TMLElement(self, node):
        try:
            ctor_cls = self.toolkit[node.name]
        except KeyError:
            msg = 'Toolkit does not support the %s item.' % node.name
            raise ValueError(msg)
        
        ctor = ctor_cls()

        identifier = node.identifier
        if identifier is not None:
            ctor.identifier = identifier
        
        stack = self.stack
        stack.append(ctor)
        self.visit(node.body)
        stack.pop()
        if stack:
            stack[-1].children.append(ctor)
        else:
            self.root = ctor

    def visit_TMLElementBody(self, node):
        for metas in node.metas:
            self.visit(metas)
        for expr in node.exprs:
            self.visit(expr)
        for child in node.tml_children:
            self.visit(child)

    def visit_TMLMeta(self, node):
        try:
            ctor_cls = self.toolkit[node.name]
        except KeyError:
            msg = 'Toolkit does not support the %s item.' % node.name
            raise ValueError(msg)
        
        ctor = ctor_cls()

        identifier = node.identifier
        if identifier is not None:
            ctor.identifier = identifier
        
        stack = self.stack
        stack.append(ctor)
        self.visit(node.body)
        stack.pop()
        stack[-1].metas.append(ctor)

    def visit_TMLDefault(self, node):
        default = self.default
        if default is None:
            msg = 'No interceptor factory supplied for `default`.'
            raise ValueError(msg)
        else:
            item = (node.name, default(node.py_ast))
            self.stack[-1].exprs.append(item)
            
    def visit_TMLExprBind(self, node):
        bind = self.bind
        if bind is None:
            msg = 'No interceptor factory supplied for `bind`.'
            raise ValueError(msg)
        else:
            item = (node.name, bind(node.py_ast))
            self.stack[-1].exprs.append(item)
    
    def visit_TMLNotify(self, node):
        notify = self.notify
        if notify is None:
            msg = 'No interceptor factory supplied for `notify`.'
            raise ValueError(msg)
        else:
            item = (node.name, notify(node.py_ast))
            self.stack[-1].exprs.append(item)

    def visit_TMLDelegate(self, node):
        delegate = self.delegate
        if delegate is None:
            msg = 'No interceptor factory supplied for `delegate`.'
            raise ValueError(msg)
        else:
            item = (node.name, delegate(node.obj_name, node.attr_name))
            self.stack[-1].exprs.append(item)


class TMLViewFactory(HasStrictTraits):

    _ast = Instance(tml_ast.TML)

    _toolkit = Instance(dict)

    _ctor_tree = Instance(IToolkitConstructor)

    _imports = Instance(dict)

    @classmethod
    def parse_tml(cls, filehandle):
        if isinstance(filehandle, basestring):
            with open(filehandle) as f:
                tml_source = f.read()
        else:
            tml_source = filehandle.read()
        return tml_parser.parse(tml_source)
    
    def __init__(self, filehandle, toolkit=None):
        super(TMLViewFactory, self).__init__()
        self._ast = self.parse_tml(filehandle)
        self._toolkit = toolkit or default_toolkit()
        self._ctor_tree = None
        self._imports = None

    def _build_ctor_tree(self):
        # If we want to build for a different binding semantic (like pixies)
        # import and use different interceptor factories here.
        from ..interceptors import tml
        visitor = _ConstructorVisitor(self._toolkit, default=tml.Default,
                                      bind=tml.Bind, delegate=tml.Delegate,
                                      notify=tml.Notify)
        visitor.visit(self._ast)
        tree, imports = visitor.results()
        self._ctor_tree = tree
        self._imports = imports

    def __call__(self, **ctxt_objs):
        if self._ctor_tree is None:
            self._build_ctor_tree
        ns = {}
        ns.update(self._imports)
        ns.update(ctxt_objs)
        return self._ctor_tree(**ns)

