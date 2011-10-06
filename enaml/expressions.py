#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import ast
import abc
from collections import namedtuple
import types

from traits.api import (Any, CTrait, HasStrictTraits, HasTraits, Instance, 
                        Property, Str, WeakRef, Interface, implements, Callable)

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
        if cls is MappingType:
            if hasattr(C, '__getitem__') and hasattr(C, '__setitem__'):
                return True
        return NotImplemented


#-----------------------------------------------------------------------------
# Express Locals
#-----------------------------------------------------------------------------
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
    (It's probably best to create these on-the-fly when needed)

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
        
        **overrides
            Objects that should take complete precedent.

        """
        self.local_ns = local_ns
        self.obj = obj
        self.overrides = overrides
    
    def __getitem__(self, name):
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
        self.local_ns[name] = val


#------------------------------------------------------------------------------
# Expression Interface definitions
#------------------------------------------------------------------------------
class IExpressionDelegate(Interface):
    pass


class IExpressionNotifier(Interface):
    pass


#------------------------------------------------------------------------------
# Default Expression Classes
#------------------------------------------------------------------------------
class BaseExpression(HasStrictTraits):
    """ A base class with common traits needed to implement various
    expression delegates and notifiers.

    Attributes
    ----------
    code : Instance(types.CodeType)
        The code object that holds the expression

    global_ns : Callable
        A callable which returns the global namespace dictionary
        for this expression.

    local_ns : Callable
        A callable which returns the local namespace mapping object
        for this expression.

    obj : WeakRef
        The object for which we are providing delegation. We don't
        specify the type (which would be Component) in order to avoid
        a circular import.

    name : Str
        The name on the object which we are delegating

    validate_trait : Instance(CTrait)
        The trait to use to validate the expression values.

    value : Property
        A property which gets and sest the value of the expression.

    _value : Any
        The underlying value store.

    """
    global_ns = Callable

    local_ns = Callable

    py_ast = Instance(ast.Expression)

    code = Instance(types.CodeType)

    obj = WeakRef

    name = Str

    validate_trait = Instance(CTrait)

    value = Property(depends_on='_value')

    _value = Any

    def __init__(self, py_ast, code, global_ns, local_ns):
        super(BaseExpression, self).__init__()
        self.global_ns = global_ns
        self.local_ns = local_ns
        self.py_ast = py_ast
        self.code = code

    def parse_attr_names(self, py_ast, obj):
        names = set()
        name_node = ast.Name
        for node in ast.walk(py_ast):
            if isinstance(node, name_node):
                name = node.id
                if obj.trait(name):
                    names.add(name)
        return names

    def get_globals(self):
        global_ns = self.global_ns()
        if type(global_ns) is not dict:
            raise TypeError('The type of the global namespace must be dict')
        return global_ns
    
    def get_locals(self, overrides):
        local_ns = self.local_ns()
        if not isinstance(local_ns, MappingType):
            raise TypeError('The local namespace must be a mapping type')
        return ExpressionLocals(local_ns, self.obj, overrides)

    def bind(self, obj, name, validate_trait):
        self.obj = obj
        self.name = name
        self.validate_trait = validate_trait


class DefaultExpression(BaseExpression):
    """ An expression delegate which provides a default value for an
    attribute on an enaml widget. The default value is set once during
    startup but is free to be changed by user code at a later time.

    See Also
    --------
    IExpressionDelegate

    """
    implements(IExpressionDelegate)

    def _get_value(self):
        """ The getter for the 'value' property. Returns the value in
        the '_value' attribute.

        """
        return self._value

    def _set_value(self, val):
        """ The setter for the 'value' property. Validates the value
        against the validate trait before assigning it to '_value'.

        """
        val = self.validate_trait.validate(self.obj, self.name, val)
        self._value = val

    def __value_default(self):
        """ Computes the default value of the expression by evaluating
        the code object in the namespaces and validating the results
        with the validate_trait.

        """
        f_globals = self.get_globals()
        f_locals = self.get_locals({'self': self.obj})
        val = eval(self.code, f_globals, f_locals)
        val = self.validate_trait.validate(self.obj, self.name, val)
        return val


class BindingExpression(DefaultExpression):
    """ An expression delegate which binds the results of an expression
    to the attribute of an enaml widget. Whenever the dependencies in
    the expression change, the expression is re-evaluated and the
    value of the attribute is updated.

    Attributes
    ----------
    dependencies : List(Tuple(Str, Str))
        A list of dependencies information provided by the factory
        that created this instance. It has the form [(root, attr), ...]
        where root and attr are string that make up an attribute
        expression such as 'a.b' or 'a.b()' or 'a.b.c()'. Only
        one level of attribute access is tracked.

    """
    def bind(self, obj, name, validate_trait):
        """ Binds the expression update method to listeners on the
        dependencies in the expression.

        """
        super(BindingExpression, self).bind(obj, name, validate_trait)

        global_ns = self.get_globals()
        local_ns = self.get_locals({'self': self.obj})
        py_ast = self.py_ast

        visitor = AttributeVisitor()
        visitor.visit(py_ast)
        
        refresh_value = self.refresh_value
        for dep_name, attr in visitor.results():
            try:
                dep = local_ns[dep_name]
            except KeyError:
                try:
                    dep = global_ns[dep_name]
                except KeyError:
                    raise NameError('name `%s` is not defined' % dep_name)
            if isinstance(dep, HasTraits):
                dep.on_trait_change(refresh_value, attr)
        
        for name in self.parse_attr_names(py_ast, obj):
            obj.on_trait_change(refresh_value, name)

    def refresh_value(self):
        """ The refresh function that is called by the dependency
        listeners. It re-evaluates the expression and sets it as
        the value.

        """
        f_globals = self.get_globals()
        f_locals = self.get_locals({'self': self.obj})
        val = eval(self.code, f_globals, f_locals)
        self.value = val


class DelegateExpression(DefaultExpression):
    """ An expression delegate which provides a two-way binding between
    an attribute on an enaml widget, and an attribute on a model. The
    values of the two attributes remain synced together.

    Attributes
    ----------
    dependencies : List(Tuple(Str, Str))
        A tuple of dependencies information provided by the factory
        that created this instance. It has the form [(root, attr)]
        where root and attr are string that make up an attribute
        expression such as 'a.b'.

    delegate : Any
        The object to which we are delegating

    delegate_attr_name : Str
        The attribute name on the delegate to which we are delegating.

    See Also
    --------
    IExpressionDelegate

    """
    delegate_obj = Any

    delegate_attr_name = Str

    def bind(self, obj, name, validate_trait):
        """ Binds the expression update method to a listener on the
        delegate attribute.

        """
        super(DelegateExpression, self).bind(obj, name, validate_trait)
        
        global_ns = self.get_globals()
        local_ns = self.get_locals({'self': self.obj})
        
        visitor = AttributeVisitor()
        visitor.visit(self.py_ast)
        deps = visitor.results()

        if len(deps) > 1:
            raise TypeError('Invalid expression for delegation.')

        obj_name, attr_name = deps[0]

        try:
            obj = local_ns[obj_name]
        except KeyError:
            try:
                obj = global_ns[obj_name]
            except KeyError:
                raise NameError('name `%s` is not defined' % obj_name)

        self.delegate_obj = obj
        self.delegate_attr_name = attr_name

        if isinstance(obj, HasTraits):
            obj.on_trait_change(self.refresh_value, attr_name)

    def _get_value(self):
        """ Overridden from the parent class property getter to pull
        the value from the delegate object rather than the '_value'
        attribute on this instance.

        """
        val = getattr(self.delegate_obj, self.delegate_attr_name)
        val = self.validate_trait.validate(self.obj, self.name, val)
        return val

    def _set_value(self, val):
        """ Overridden from the parent class property setter to set
        the value on the delegate object rather than the '_value'
        attribute on this instance.

        """
        val = self.validate_trait.validate(self.obj, self.name, val)
        setattr(self.delegate_obj, self.delegate_attr_name, val)

    def refresh_value(self):
        """ Refreshes the value of the delegate by invalidating
        the '_value' attribute which will cause the 'value' property
        to pull a new value.

        """
        self._value = not self._value


class NotifierExpression(BaseExpression):
    """ An expression notifier which will evaluate an expression
    whenever an attribute on an Enaml widget changes. A message
    object will be added to the local namespace of the expression
    at the 'msg' name. This allows the expression to accept
    arguments from the attribute change.

    """
    implements(IExpressionNotifier)

    arguments = namedtuple('Arguments', ('obj', 'name', 'old', 'new'))

    def bind(self, obj, name, validate_trait=None):
        """ Overridden from the parent class since we don't recieve
        (or care about) the validate_trait since a notification is
        only right associative

        """
        super(NotifierExpression, self).bind(obj, name, validate_trait)
        obj.on_trait_change(self.notify, name)

    def notify(self, obj, name, old, new):
        """ The notify method is called by the listeners on the widget
        attribute. It simply evaluates the expression in the proper
        namespaces while adding a message object in the local ns.

        """
        args = self.arguments(obj, name, old, new)
        f_globals = self.get_globals()
        f_locals = self.get_locals({'self': self.obj, 'args': args})
        eval(self.code, f_globals, f_locals)

