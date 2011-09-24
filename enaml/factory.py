#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import itertools

from traits.api import HasStrictTraits, Instance

from .constructors import IToolkitConstructor
from .toolkit import default_toolkit, Toolkit
from .parsing import enaml_ast, parser
from .util.trait_types import SubClass
from .expressions import (
    IExpressionDelegateFactory, IExpressionNotifierFactory,
    DefaultExpressionFactory, BindingExpressionFactory, 
    DelegateExpressionFactory, NotifierExpressionFactory,
)


class EnamlCtorBuilder(HasStrictTraits):
    """ An Enaml AST visitor which builds a constructor tree.

    A visitor which walks an Enaml AST and converts it into a tree
    of toolkit constructor instances which we can be called to create
    a view.

    Attributes
    ----------
    toolkit : Instance(dict)
        A toolkit dictionary which maps string widget names to the toolkit 
        constructor classes for that widget.

    ast : Instance(tml_ast.TML)
        A root tml_ast node from which we'll build the tree.

    default : Instance(IExpressionDelegateFactory)
        An expression delegate factory class for handling default 
        expressions.
    
    bind : Instance(IExpressionDelegateFactory)
        An expression delegate factory class for handling binding 
        expressions.

    delegate : Instance(IExpressionDelegateFactory)
        An expression delegate factory class for handling delegate 
        expressions.
    
    notify : Instance(INotifierFactory)
        An expression notifier factory class for handling notifier 
        expressions.
    
    Methods
    -------
    build()
        After creating the builder, call this method with an enaml ast
        instance to build the constructor tree.
    
    results()
        After calling visit(...), call this method to retrieve the
        results.

    """
    toolkit = Instance(Toolkit)

    ast = Instance(enaml_ast.EnamlModule)

    default = SubClass(IExpressionDelegateFactory)

    bind = SubClass(IExpressionDelegateFactory)
    
    delegate = SubClass(IExpressionDelegateFactory)

    notify = SubClass(IExpressionNotifierFactory)

    _root = Instance(IToolkitConstructor)

    _imports = Instance(dict, ())

    _stack = Instance(list, ())

    def __init__(self, toolkit, ast, default, bind, delegate, notify):
        super(EnamlCtorBuilder, self).__init__(
            toolkit=toolkit, ast=ast, default=default, bind=bind,
            delegate=delegate, notify=notify,
        )

    def build(self):
        """ Call this method after instantiating a builder to run the
        build process.
        
        Arguments
        ---------
        None

        Returns
        -------
        result : None

        """
        self.visit(self.ast)

    def results(self):
        """ Call this method after running the build process to retrieve
        the results.

        Arguments
        ---------
        None

        Returns
        -------
        tree, imports : IToolkitConstructor, dict
            The root node of the constructor tree and the dictionary
            of imports that were executed by the Enaml source.

        """
        return self._root, self._imports
    
    #--------------------------------------------------------------------------
    # The following methods are for internal use only
    #--------------------------------------------------------------------------
    def visit(self, node):
        name = 'visit_%s' % node.__class__.__name__
        method = getattr(self, name, self.default_visit)
        method(node)

    def default_visit(self, node):
        for child in node.children():
            self.visit(child)

    def visit_EnamlModule(self, node):
        for item in itertools.chain(node.imports, node.components):
            self.visit(item)

    def visit_EnamlPyImport(self, node):
        code = compile(node.py_ast, 'Enaml', mode='exec')
        exec code in {}, self._imports

    def visit_EnamlComponent(self, node):
        ctor = self.toolkit.create_ctor(node.name)
        identifier = node.identifier
        if identifier is not None:
            ctor.identifier = identifier
        stack = self._stack
        stack.append(ctor)
        self.visit(node.body)
        stack.pop()
        if stack:
            stack[-1].children.append(ctor)
        else:
            self._root = ctor

    def visit_EnamlComponentBody(self, node):
        for item in itertools.chain(node.expressions, node.children):
            self.visit(item)

    def visit_EnamlExpression(self, node):
        name_node = node.lhs
        name = (name_node.root, name_node.leaf)
        op = node.op
        if op == node.DEFAULT:
            item = (name, self.default(node.rhs.py_ast))
            self._stack[-1].delegates.append(item)
        elif op == node.BIND:
            item = (name, self.bind(node.rhs.py_ast))
            self._stack[-1].delegates.append(item)
        elif op == node.DELEGATE:
            item = (name, self.delegate(node.rhs.py_ast))
            self._stack[-1].delegates.append(item)
        elif op == node.NOTIFY:
            item = (name, self.notify(node.rhs.py_ast))
            self._stack[-1].notifiers.append(item)
        else:
            raise ValueError('Invalid expression op.')


class EnamlFactory(HasStrictTraits):
    """ The class which will create a factory for generating View 
    objects from Enaml source code.
    
    Instances of this class are callable with **kwargs and return
    enaml.view.View objects for the provide Enaml source.

    """
    _ast = Instance(enaml_ast.EnamlModule)

    _toolkit = Instance(Toolkit)

    _ctor_tree = Instance(IToolkitConstructor)

    _imports = Instance(dict)

    @classmethod
    def parse_enaml(cls, filehandle):
        """ Parses Enaml source code into an Enaml ast. The source
        can be provided as a file like object or a string path to 
        a file.

        """
        if isinstance(filehandle, basestring):
            with open(filehandle) as f:
                enaml_source = f.read()
        else:
            enaml_source = filehandle.read()
        return parser.parse(enaml_source)
    
    def __init__(self, filehandle, toolkit=None):
        """ Initialize an Enaml factory.

        Parameters
        ----------
        filehandle : file-like object or string
            A file-like object containing Enaml source code or the 
            string path to an Enaml source file.

        toolkit : Toolkit, optional
            The toolkit to use to create the views. It defaults to 
            None in which case the default toolkit is determined
            based on the user's environment variables.

        """
        super(EnamlFactory, self).__init__()
        self._ast = self.parse_enaml(filehandle)
        self._toolkit = toolkit or default_toolkit()

    def expression_factories(self):
        return (DefaultExpressionFactory, BindingExpressionFactory, 
                DelegateExpressionFactory, NotifierExpressionFactory)

    def _build_ctor_tree(self):
        builder = EnamlCtorBuilder(
            self._toolkit, self._ast , *self.expression_factories()
        )
        builder.build()
        tree, imports = builder.results()
        self._ctor_tree = tree
        self._imports = imports

    def __call__(self, **ctxt_objs):
        if self._ctor_tree is None:
            self._build_ctor_tree()
        ns = {}
        ns.update(self._imports)
        ns.update(ctxt_objs)
        ns.update(__builtins__)
        self._toolkit.prime_event_loop()
        view = self._ctor_tree(**ns)
        view.toolkit = self._toolkit
        return view

