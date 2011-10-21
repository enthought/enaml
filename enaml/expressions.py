#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import ast
import abc
from collections import namedtuple
import types

from traits.api import (Any, HasStrictTraits, HasTraits, Instance, Str,
                        WeakRef, Interface, implements, Callable)

from .parsing.analyzer import AttributeVisitor


#------------------------------------------------------------------------------
# Custom mapping type for namespace type checking
#------------------------------------------------------------------------------
class MappingType(object):
    """ An abstract class used for type checking on instances to ensure
    that they provide a __getitem__ and __setitem__ method.

    """
    __metaclass__ = abc.ABCMeta

    @classmethod
    def __subclasshook__(cls, C):
        """ Returns True if the class has a __getitem__ and __setitem__
        method. Otherwise, returns NotImplemented.

        """
        if cls is MappingType:
            if hasattr(C, '__getitem__') and hasattr(C, '__setitem__'):
                return True
        return NotImplemented


#------------------------------------------------------------------------------
# Express Locals
#------------------------------------------------------------------------------
class ExpressionLocals(object):
    """ A mapping object that will first look in the provided overrides,
    then in the given locals mapping, and finally in the attribute space
    of the given object.

    Notes
    -----
    Setting items on this object will delegate the operation to the
    provided locals mapping.

    Strong references are kept to all objects passed to the constructor,
    so care should be taken in managing the lifetime of these scope
    objects since their use is likely to create reference cycles.
    (It's probably best to create these objects on-the-fly when needed)

    """
    __slots__ = ('local_ns', 'obj', 'overrides')

    def __init__(self, local_ns, obj, overrides):
        """ Initialize an expression locals instance.

        Parameters
        ----------
        local_ns : dict
            The locals dict to check before checking the attribute space
            of the given object.

        obj : object
            The python object on which to attempt the getattr.

        overrides : dict
            Objects that should take complete precedent in the scope
            lookup. Note this is a dict instead of **overrides, so that
            'self' can be added to the namespace. If we didn't do this,
            'self' would clash with this method definition.

        """
        self.local_ns = local_ns
        self.obj = obj
        self.overrides = overrides

    def __getitem__(self, name):
        """ Lookup an item from the namespace.

        Returns the named item from the namespace by first looking in
        the overrides, then the provided locals namespace, and finally
        the attribute space of the object. If the value is not found,
        a KeyError is raised.

        Parameters
        ----------
        name : string
            The name that should be looked up in the namespace.

        Returns
        -------
        result : object
            The value associated with the name, if found.

        """
        try:
            res = self.overrides[name]
        except KeyError:
            try:
                res = self.local_ns[name]
            except KeyError:
                try:
                    res = getattr(self.obj, name)
                except AttributeError:
                    raise KeyError(name)
        return res

    def __setitem__(self, name, val):
        """ Set the value in the local namespace.

        This operation delegates the setting to the local namespace that
        was provided during instantiation.

        Parameters
        ---------
        name : string
            The name to set in the namespace.

        val : object
            The value to set in the namespace.

        """
        self.local_ns[name] = val


#------------------------------------------------------------------------------
# Expression Binder Interface
#------------------------------------------------------------------------------
class IExpressionBinder(Interface):
    """ The expression binder interface definition.

    Classes should implemented this interface if they wish instances to
    be useable by enaml as expression binder objects.

    Methods
    -------
    __init__(py_ast, code, global_ns, local_ns)
        Initialize a binder object.

    bind(obj, name)
        Bind the expression to the `name` attribute on `object`.

    eval_expression()
        Evaluate the expression and return the result. This will be
        called only after `bind` has been called.

    """
    def __init__(self, py_ast, code, global_ns, local_ns):
        """ Initialize an expression binder.

        Parameters
        ----------
        py_ast : Instance(ast.Expression)
            The Python expression ast node for this expression.

        code : Instance(types.CodeType)
            The compiled code object of the Python expression ast.

        global_ns : Callable
            A callable which returns the global namespace dictionary
            for the expression.

        local_ns : Callable
            A callable which returns a mapping object for the local
            namespace of the expression.

        """
        raise NotImplementedError

    def bind(self, obj, name):
        """ Binds the expression to the attribute of the object.

        Parameters
        ----------
        obj : object
            The enaml Component object to which we are binding the
            expression.

        name : string
            The name of the attribute on the object to which we are
            binding the expression.

        """
        raise NotImplementedError

    def eval_expression(self):
        """ Evaluates and returns the results of the expression. This
        will be called only after `bind` has been called.

        """
        raise NotImplementedError


#------------------------------------------------------------------------------
# Standard Expression Binding Classes
#------------------------------------------------------------------------------
class DefaultExpression(HasStrictTraits):
    """ An IExpressionBinder that provides a default attribute value.

    Attributes
    ----------
    py_ast : Instance(ast.Expression)
        The Python expression ast node for this expression.

    code : Instance(types.CodeType)
        The compiled code object of the Python expression ast.

    global_ns : Callable
        A callable which returns the global namespace dictionary
        for the expression.

    local_ns : Callable
        A callable which returns a mapping object for the local
        namespace of the expression.

    obj : WeakRef
        The object to which we are binding. This is stored as weakref
        to prevent circular references.

    name : Str
        The attribute name on the object which we are binding.

    Methods
    -------
    __init__(py_ast, code, global_ns, local_ns)
        Initialize a binder object.

    bind(obj, name)
        Bind the expression to the `name` attribute on `object`.

    eval_expression()
        Evaluate the expression and return the result. This will be
        called only after `bind` has been called.

    See Also
    --------
    IExpressionBinder

    """
    implements(IExpressionBinder)

    global_ns = Callable

    local_ns = Callable

    py_ast = Instance(ast.Expression)

    code = Instance(types.CodeType)

    obj = WeakRef

    name = Str

    def __init__(self, py_ast, code, global_ns, local_ns):
        """ Initialize a DefaultExpression.

        Parameters
        ----------
        py_ast : Instance(ast.Expression)
            The Python expression ast node for this expression.

        code : Instance(types.CodeType)
            The compiled code object of the Python expression ast.

        global_ns : Callable
            A callable which returns the global namespace dictionary
            for the expression.

        local_ns : Callable
            A callable which returns a mapping object for the local
            namespace of the expression.

        """
        super(DefaultExpression, self).__init__()
        self.global_ns = global_ns
        self.local_ns = local_ns
        self.py_ast = py_ast
        self.code = code

    def bind(self, obj, name):
        """ Binds the expression to the attribute of the object.

        Parameters
        ----------
        obj : object
            The enaml Component object to which we are binding the
            expression.

        name : string
            The name of the attribute on the object to which we are
            binding the expression.

        """
        self.obj = obj
        self.name = name

    def eval_expression(self):
        """ Evaluates and returns the results of the expression. This
        will be called only after `bind` has been called. This adds
        a 'self' attribute to the locals namespace.

        Returns
        -------
        result : object
            The evaluated expression result.

        """
        f_globals = self.get_globals()
        f_locals = self.get_locals({'self': self.obj})
        val = eval(self.code, f_globals, f_locals)
        return val

    def parse_attr_names(self, py_ast, obj):
        """ Parses an expression ast for attributes on the given obj.

        Given an Expression ast node and an objet, returns the set
        of ast Name nodes that are trait attributes on the object. This
        treats the expression as if 'self' were implicit (ala c++)
        and we want to find all the traited attributes referred to
        implicitly in the expression for the purposes of hooking up
        notifiers.

        Paramters
        ---------
        py_ast : Instance(ast.Expresssion)
            The ast Expression node to parse.

        obj : object
            The object we are querrying for attributes.

        Returns
        -------
        result : set
            The set of names referred to in the expression that are trait
            attributes on the object.

        """
        names = set()
        name_node = ast.Name
        for node in ast.walk(py_ast):
            if isinstance(node, name_node):
                name = node.id
                if obj.trait(name):
                    names.add(name)
        return names

    def get_globals(self):
        """ Returns the global namespace dictionary.

        Returns the dict created by the `global_ns` callable attribute,
        or raises a TypeError if the value is not a dict.

        """
        global_ns = self.global_ns()
        if type(global_ns) is not dict:
            raise TypeError('The type of the global namespace must be dict')
        return global_ns

    def get_locals(self, overrides):
        """ Returns the local namespace mapping.

        Returns the mapping object created by the `local_ns` callable
        attribute, or raises a TypeError if the value is not a mapping.

        """
        local_ns = self.local_ns()
        if not isinstance(local_ns, MappingType):
            raise TypeError('The local namespace must be a mapping type')
        return ExpressionLocals(local_ns, self.obj, overrides)


class BindingExpression(DefaultExpression):
    """ A dynamically updating IExpressionBinder.

    The expression is parsed for trait attribute references and when any
    of those traits in the expression change, the expression is evaluated
    and the value of the component attribute is updated.

    Methods
    -------
    update_object()
        The notification handler to update the component object.

    See Also
    --------
    DefaultExpression

    """
    def bind(self, obj, name):
        """ Overridden from the parent class to parse the expression
        for any trait attribute references. A notifier is attached to
        each trait reference that will update the expression value.

        """
        super(BindingExpression, self).bind(obj, name)

        global_ns = self.get_globals()
        local_ns = self.get_locals({'self': obj})
        py_ast = self.py_ast

        # The attribute visitor parses the expression looking for any
        # `foo.bar` style attribute sub-expressions. The results value
        # is a list of ('foo', 'bar') style tuples.
        visitor = AttributeVisitor()
        visitor.visit(py_ast)

        update_object = self.update_object
        for dep_name, attr in visitor.results():
            try:
                dep = local_ns[dep_name]
            except KeyError:
                try:
                    dep = global_ns[dep_name]
                except KeyError:
                    raise NameError('name `%s` is not defined' % dep_name)
            if isinstance(dep, HasTraits):
                dep.on_trait_change(update_object, attr)

        # This portion binds any trait attributes that are being
        # reference via the implicit 'self' feature.
        for name in self.parse_attr_names(py_ast, obj):
            obj.on_trait_change(update_object, name)

    def update_object(self):
        """ The notification handler to update the component object.

        When this method is called, the expression is re-evaluated, and
        the results are assigned to the proper attribute on the component
        object.

        """
        setattr(self.obj, self.name, self.eval_expression())


class DelegateExpression(DefaultExpression):
    """ An IExpressionBinder that performs two-way binding.

    This expression binder performs two-way binding on expressions
    that are of the form 'foo.bar'

    Attributes
    ----------
    delegate_obj : Any
        The object to which we are delegating, e.g. the 'foo' part
        of a 'foo.bar' style expression.

    delegate_attr_name : Str
        The attribute name on the object to which we are delegating,
        e.g. the 'bar' part of a 'foo.bar' style expression.

    Methods
    -------
    update_object()
        The notification handler to update the component object.

    update_delegate()
        The notification handler to update the delegate object.

    See Also
    --------
    DefaultExpression

    """
    delegate_obj = Any

    delegate_attr_name = Str

    def bind(self, obj, name):
        """ Overridden from the parent class to parse the expression
        for the appropriate delegate information.

        """
        super(DelegateExpression, self).bind(obj, name)

        global_ns = self.get_globals()
        local_ns = self.get_locals({'self': obj})

        # The attribute visitor parses the expression looking for any
        # `foo.bar` style attribute sub-expressions. The results value
        # is a list of ('foo', 'bar') style tuples.
        visitor = AttributeVisitor()
        visitor.visit(self.py_ast)
        deps = visitor.results()

        if len(deps) > 1:
            msg = 'Invalid expression for delegation - lineno (%s)'
            raise TypeError(msg % self.py_ast.lineno)

        dlgt_name, attr_name = deps[0]

        try:
            dlgt = local_ns[dlgt_name]
        except KeyError:
            try:
                dlgt = global_ns[dlgt_name]
            except KeyError:
                raise NameError('name `%s` is not defined' % dlgt_name)

        self.delegate_obj = dlgt
        self.delegate_attr_name = attr_name

        if isinstance(dlgt, HasTraits):
            dlgt.on_trait_change(self.update_object, attr_name)

        obj.on_trait_change(self.update_delegate, name)

    def eval_expression(self):
        """ Overridden from the parent class to get the value from the
        delegate expression.

        """
        return getattr(self.delegate_obj, self.delegate_attr_name)

    def update_object(self):
        """ The notification handler to update the component object.

        When this method is called, the delegate expression is evaluated
        and the results are assigned to the appropriate attribute on
        the component.

        """
        setattr(self.obj, self.name, self.eval_expression())

    def update_delegate(self, val):
        """ The notification handler to update the delegate object.

        When this method is called, the delegate expression is updated
        with the appropriate value from the component.

        """
        setattr(self.delegate_obj, self.delegate_attr_name, val)


class NotifierExpression(DefaultExpression):
    """ An IExpressionBinder that will eval an expression when the
    attribute on the component changes.

    An arguments object will be added to the local namespace of the
    expression at the 'args' name. This allows the expression to accept
    argument information from the attribute change notification, instead
    of needing to do additional attribute lookups.

    Methods
    -------
    notify(obj, name, old, new)
        The notification handler to re-evaluate the expression.

    See Also
    --------
    DefaultExpression

    """
    arguments = namedtuple('Arguments', ('obj', 'name', 'old', 'new'))

    def bind(self, obj, name):
        """ Overridden from the parent class to hookup a notifier on
        the component attribute.

        """
        super(NotifierExpression, self).bind(obj, name)
        obj.on_trait_change(self.notify, name)

    def eval_expression(self):
        """ Overridden from the parent class to add an arguments object
        to the local namespace.

        """
        obj = self.obj
        name = self.name
        val = getattr(obj, name)
        args = self.arguments(obj, name, None, val)
        f_globals = self.get_globals()
        f_locals = self.get_locals({'self': self.obj, 'args': args})
        return eval(self.code, f_globals, f_locals)

    def notify(self, obj, name, old, new):
        """ The notification handler that evals the expression in
        appropriate contexts.

        """
        args = self.arguments(obj, name, old, new)
        f_globals = self.get_globals()
        f_locals = self.get_locals({'self': self.obj, 'args': args})
        eval(self.code, f_globals, f_locals)

