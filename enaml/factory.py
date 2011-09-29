#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from itertools import chain, izip

from traits.api import HasStrictTraits, Instance

from .constructors import DelegateBinder, NotifierBinder, DefnCallCtorProxy
from .toolkit import Toolkit, default_toolkit
from .parsing import enaml_ast, enaml_compiler
from .view import View, NamespaceProxy


class ExecutionContext(HasStrictTraits):

    toolkit = Instance(Toolkit)

    module_scope = Instance(dict)

    base_scope = Instance(dict)

    id_scope = Instance(dict)


class _NullItem(object):

    def __init__(self):
        self.root = None
    
    def add_child(self, child):
        if self.root:
            raise RuntimeError('Adding multiple children to null item.')
        self.root = child


def _build_component(instructions, ctxt):
    stack = [_NullItem()]
    stack_push = stack.append
    stack_pop = stack.pop

    toolkit = ctxt.toolkit
    mod_scope = ctxt.module_scope
    base_scope = ctxt.base_scope
    id_scope = ctxt.id_scope

    START_COMPONENT = enaml_compiler.START_COMPONENT
    END_COMPONENT = enaml_compiler.END_COMPONENT
    DEFAULT_EXPRESSION = enaml_compiler.DEFAULT_EXPRESSION
    BIND_EXPRESSION = enaml_compiler.BIND_EXPRESSION
    DELEGATE_EXPRESSION = enaml_compiler.DELEGATE_EXPRESSION
    NOTIFY_EXPRESSION = enaml_compiler.NOTIFY_EXPRESSION
    CALL_FACTORY = enaml_compiler.CALL_FACTORY

    for op, var_ctxt in instructions:

        if op == START_COMPONENT:
            name, identifier = var_ctxt
            ctor = toolkit.create_constructor(name, identifier)
            stack_push(ctor)
        
        elif op == END_COMPONENT:
            ctor = stack_pop()
            stack[-1].add_child(ctor)
        
        elif op == DEFAULT_EXPRESSION:
            name, py_ast = var_ctxt
            expr = toolkit.default(py_ast)
            binder = DelegateBinder(expr, name, id_scope, base_scope, mod_scope)
            stack[-1].add_expression_binder(binder)

        elif op == BIND_EXPRESSION:
            name, py_ast = var_ctxt
            expr = toolkit.bind(py_ast)
            binder = DelegateBinder(expr, name, id_scope, base_scope, mod_scope)
            stack[-1].add_expression_binder(binder)

        elif op == DELEGATE_EXPRESSION:
            name, py_ast = var_ctxt
            expr = toolkit.delegate(py_ast)
            binder = DelegateBinder(expr, name, id_scope, base_scope, mod_scope)
            stack[-1].add_expression_binder(binder)
        
        elif op == NOTIFY_EXPRESSION:
            name, py_ast = var_ctxt
            expr = toolkit.notify(py_ast)
            binder = NotifierBinder(expr, name, id_scope, base_scope, mod_scope)
            stack[-1].add_expression_binder(binder)
        
        elif op == CALL_FACTORY:
            factory_name, arguments = var_ctxt

            if factory_name not in mod_scope:
                raise NameError('Name `%s` is not defined' % name)
            
            args = []
            for arg in arguments.args:
                name = arg.name
                if name in base_scope:
                    args.append(base_scope[name])
                elif name in mod_scope:
                    args.append(mod_scope[name])
                else:
                    raise NameError('Name `%s` is not defined' % name)
            
            kwargs = {}
            for kwarg in arguments.kwargs:
                name = kwarg.name
                code = compile(kwarg.py_ast, 'Enaml', mode='eval')
                value = eval(code, mod_scope, base_scope)
                kwargs[name] = value
            
            factory = mod_scope[factory_name]
            component, cmpnt_scope = factory._build_component(args, kwargs)
            ctor = DefnCallCtorProxy(component, cmpnt_scope)
            stack[-1].add_child(ctor)

        else:
            raise RuntimeError('Invalid instruction.')

    ctor = stack[-1].root
    return ctor(id_scope), id_scope


class ComponentFactory(HasStrictTraits):
    """ A factory which will builds and return an enaml View object.

    ComponentFactorys are created and added to py module objects 
    by the enaml import hooks. Calling these instances with context
    objects will created the underlying enaml widget tree which and
    return a view which wraps the tree.

    """
    toolkit = Instance(Toolkit)
    
    _defn_ast = Instance(enaml_ast.EnamlDefine)

    _instructions = Instance(list)

    _module_dict = Instance(dict)

    _kwarg_defaults = Instance(dict)

    def __init__(self, ast, module_dict):
        """ Initialize a component factory.

        Parameters
        ----------
        ast : EnamlComponent ast node.
            The component ast node for the view we want to build.

        module_dict : dict
            The __dict__ for the module in which we are being created.
        
        """
        super(ComponentFactory, self).__init__()
        self._defn_ast = ast
        self._module_dict = module_dict
        self._kwarg_defaults = self._compute_kwarg_defaults(ast, module_dict)
        self._instructions = enaml_compiler.EnamlCompiler.compile(ast)

    def __call__(self, *args, **kwargs):
        """ Create an enaml View for the given component.

        Parameters
        ----------
        *args

        **kwargs
            The objects to add the local namespaces of the expressions
            in the view.
        
        """
        
        component, id_scope = self._build_component(args, kwargs)
        
        ns = NamespaceProxy(id_scope)
        view = View(component=component, toolkit=self.toolkit, ns=ns)
        view.apply_style_sheet()
        
        return view
    
    def _build_component(self, args, kwargs):
        ctxt = ExecutionContext(
            toolkit=self.toolkit,
            id_scope={},
            module_scope=self._module_dict,
            base_scope = self._create_base_scope(self._defn_ast, args, kwargs),
        )
        return _build_component(self._instructions, ctxt)
         
    def _compute_kwarg_defaults(self, defn_ast, module_dict):
        res = {}
        kwargs = defn_ast.arguments.kwargs
        for kw in kwargs:
            name = kw.name
            code = compile(kw.py_ast, 'Enaml', mode='eval')
            res[name] = eval(code, {}, module_dict)
        return res

    def _create_base_scope(self, defn_ast, args, kwargs):
        """ Given a define ast and the args and kwargs with which it
        was called, this creates an initial scope dictionary for the
        component, or raises an error if there was an argument 
        mismatch.

        """
        node = defn_ast
        arguments = node.arguments
        defn_args = arguments.args
        defn_kwargs = arguments.kwargs

        if defn_kwargs:
            min_required = len(defn_args)
            max_allowed = min_required + len(defn_kwargs)
            n_supplied = len(args) + len(kwargs)
            if n_supplied < min_required:
                msg = '%s() requires at least %s arguments (%s given)'
                raise TypeError(msg % (node.name, min_required, n_supplied))
            elif n_supplied > max_allowed:
                msg = '%s() takes at most %s arguments (%s given)'
                raise TypeError(msg % (node.name, max_allowed, n_supplied))
        else:
            n_required = len(defn_args)
            n_supplied = len(args) + len(kwargs)
            if n_supplied != n_required:
                msg = '%s() takes exactly %s arguments (%s given)'
                raise TypeError(msg % (node.name, n_required, n_supplied))
        
        scope = {}
        scope.update(self._kwarg_defaults)
        
        valid_arg_names = set(arg.name for arg in chain(defn_args, defn_kwargs))
        for name, value in kwargs.iteritems():
            if name not in valid_arg_names:
                msg = '%s() got an unexpected keyword argument `%s`'
                raise TypeError(msg % (node.name, name))
            scope[name] = value

        for value, arg in izip(args, chain(defn_args, defn_kwargs)):
            name = arg.name
            if name in scope:
                msg = '%s() got multiple values for keyword argument `%s`'
                raise TypeError(msg % (node.name, name))
            scope[name] = value
        
        return scope
    
    #---------------------------------------------------------------------------
    # Traits Handlers
    #---------------------------------------------------------------------------
    def _toolkit_default(self):
        return default_toolkit()

