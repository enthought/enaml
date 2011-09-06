import ast
from collections import namedtuple
import types

from traits.api import (Any, CTrait, HasStrictTraits, Tuple, HasTraits, 
                        Instance, Property, Str, implements, cached_property,
                        Interface, WeakRef, List)

from .parsing.analyzer import AttributeVisitor


#-------------------------------------------------------------------------------
# Interfaces
#-------------------------------------------------------------------------------
class IExpressionDelegate(Interface):
    """ Defines the IExpressionDelegate interface for Enaml.

    An expression delegate can be added to an Enaml ui widget to change
    the behavior of attributes on the widget. This makes it possible to
    bind expressions and other dynamic behavior to the widget.

    Attributes
    ----------
    value : Property
        Should get and set the value of the expression.
    
    validate_trait : Instance(CTrait)
        The trait to use to validate the expression values.

    global_ns : Instance(dict)
        The global namespace in which the expression should execute.

    local_ns : Intance(dict)
        The local namespace in which the expression should execute.
    
    Methods
    -------
    bind(obj, name)
        Called automatically when the delegate should hook up listeners.

    """
    value = Property

    validate_trait = Instance(CTrait)

    global_ns = Instance(dict)

    local_ns = Instance(dict)

    def bind(self, obj, name, validate_trait):
        """ Called automatically when the delegate should bind listeners.

        Arguments
        ---------
        obj : Component
            The enaml component widget.
        
        name : string
            The name of the attribute on the component to which we
            are delegating.

        validate_trait : Instance(CTrait)
            The trait that should be used to validate expression values.

        Returns
        -------
        result : None

        """
        raise NotImplementedError


class IExpressionDelegateFactory(Interface):
    """ Defines the IExpressionDelegateFactory interface for Enaml.

    The IExpressionDelegateFactory defines the interface for creating 
    factories that create IExpressionDelegate objects which bind code 
    and/or expressions to the Enaml object tree.

    Methods
    -------
    __call__(global_ns, local_ns)
        Creates an IExpressionDelegate instance that is ready to be
        added to an Enaml ui object.

    """
    def __call__(self, global_ns, local_ns):
        """ Creates an IExpressionDelegate instance.

        Creates an IExpressionDelegate instance that is ready to be
        added to an Enaml ui object.

        Arguments
        ---------
        global_ns : dict
            The global namespace for the delegate.
        
        local_ns : dict
            The local namespace for the delegate.

        Returns
        -------
        result : IExpressionDelegate
            The delegate that will handle this code.

        """
        raise NotImplementedError


class IExpressionNotifier(Interface):
    """ The interface to create expression notifiers.

    Attributes
    ----------
    global_ns : Instance(dict)
        The global namespace in which the expression should execute.

    local_ns : Intance(dict)
        The local namespace in which the expression should execute.

    Methods
    -------
    bind(obj, name)
        Called automatically when the notifier should hook up listeners.

    """
    global_ns = Instance(dict)

    local_ns = Instance(dict)

    def bind(self, obj, name):
        """ Called automatically when the notifier should bind listeners.

        This is called automatically by the enaml widget when the notifier
        should hook up listeners.

        Arguments
        ---------
        obj : Component
            The enaml component widget.
        
        name : string
            The name of the attribute on the component to which we are 
            delegating.

        Returns
        -------
        result : None

        """
        raise NotImplementedError


class IExpressionNotifierFactory(Interface):
    """ Defines the IExpressionNotifierFactory interface for Enaml.

    An IExpressionNotifierFactory should create and return an
    IExpressionNotifier that will execute an expression in response
    to a change on an attribute of an Enaml widget.

    Methods
    -------
    __call__()
        Creates and returns an IExpressionNotifier.

    """
    def __call__(self, global_ns, local_ns):
        """ Creates and returns an IExpressionNotifier.

        Arguments
        ---------
        global_ns : dict
            The global namespace for the delegate.
        
        local_ns : dict
            The local namespace for the delegate.

        Returns
        -------
        result : IExpressionNotifier
            The expression notifier that will handle the notifications.

        """
        raise NotImplementedError


#-------------------------------------------------------------------------------
# Expression Implementations
#-------------------------------------------------------------------------------
class BaseExpression(HasStrictTraits):
    """ A base class with common traits needed to implement various
    expression delegates and notifiers.
    
    Attributes
    ----------
    code : Instance(types.CodeType)
        The code object that holds the expression
    
    global_ns : Instance(dict)
        The global namespace in which the expression should execute.

    local_ns : Intance(dict)
        The local namespace in which the expression should execute.
    
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
    code = Instance(types.CodeType)

    global_ns = Instance(dict)

    local_ns = Instance(dict)

    obj = WeakRef

    name = Str

    validate_trait = Instance(CTrait)

    value = Property(depends_on='_value')

    _value = Any


class DefaultExpression(BaseExpression):
    """ An expression delegate which provides a default value for an
    attribute on an enaml widget. The default value is set once during 
    startup but is free to be changed by user code at a later time.
    
    See Also
    --------
    IExpressionDelegate

    """
    implements(IExpressionDelegate)

    def bind(self, obj, name, validate_trait):
        """ The default expression does need to hookup listeners, but
        it does assign the arguments to the appropriate attributes.

        """
        self.obj = obj
        self.name = name
        self.validate_trait = validate_trait

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
        val = eval(self.code, self.global_ns, self.local_ns)
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

    See Also
    --------
    IExpressionDelegate

    """
    dependencies = List(Tuple(Str, Str))

    def bind(self, obj, name, validate_trait):
        """ Binds the expression update method to listeners on the
        dependencies in the expression.

        """
        super(BindingExpression, self).bind(obj, name, validate_trait)
        self.obj = obj
        self.name = name
        for dep_name, attr in self.dependencies:
            try:
                dep = self.local_ns[dep_name]
            except KeyError:
                try:
                    dep = self.global_ns[dep_name]
                except KeyError:
                    msg = '`%s` is not defined or accessible in the namespace.'
                    raise NameError(msg % dep_name)
            if isinstance(dep, HasTraits):
                dep.on_trait_change(self.refresh_value, attr)

    def refresh_value(self):
        """ The refresh function that is called by the dependency
        listeners. It re-evaluates the expression and sets it as 
        the value.

        """
        val = eval(self.code, self.global_ns, self.local_ns)
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
    dependencies = List(Tuple(Str, Str), maxlen=1)
    
    delegate_obj = Any

    delegate_attr_name = Str

    def bind(self, obj, name, validate_trait):
        """ Binds the expression update method to a listener on the
        delegate attribute.

        """
        super(DelegateExpression, self).bind(obj, name, validate_trait)
        obj_name, attr_name = self.dependencies[0]
        try:
            obj = self.local_ns[obj_name]
        except KeyError:
            try:
                obj = self.global_ns[obj_name]
            except KeyError:
                msg = '`%s` is not defined or accessible in the namespace.'
                raise NameError(msg % obj_name)
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
    
    message = namedtuple('Message', ('obj', 'name', 'old', 'new'))

    def bind(self, obj, name):
        """ Binds the expression notify method to a listener on the
        attribute on the Enaml widget.

        """
        self.obj = obj
        self.name = name
        obj.on_trait_change(self.notify, name)

    def notify(self, obj, name, old, new):
        """ The notify method is called by the listeners on the widget
        attribute. It simply evaluates the expression in the proper
        namespaces while adding a message object in the local ns.

        """
        local_ns = self.local_ns
        local_ns['msg'] = self.message(obj, name, old, new)
        eval(self.code, self.global_ns, local_ns)


#-------------------------------------------------------------------------------
# Factory implementations
#-------------------------------------------------------------------------------
class BaseExpressionFactory(HasStrictTraits):
    """ A base class for building expression delegate and notifier
    factories.

    Attributes
    ----------
    ast : Instance(ast.Expression)
        The Python ast.Expression node for this expression.

    code : Property(Instance(types.CodeType))
        The Python code object generated from the Python ast.

    dependencies : Property(List(Tuple(Str, Str)))
        The dependencies created by parsing the Python ast.
    
    """
    ast = Instance(ast.Expression)

    code = Property(Instance(types.CodeType), depends_on='ast')

    dependencies = Property(List(Tuple(Str, Str)), depends_on='ast')

    def __init__(self, ast):
        super(BaseExpressionFactory, self).__init__()
        self.ast = ast

    @cached_property
    def _get_code(self):
        """ Compiles the ast into a code object using 'eval' mode.

        """
        return compile(self.ast, 'Enaml', 'eval')

    @cached_property
    def _get_dependencies(self):
        """ Parses the ast for attribute dependencies.

        """
        visitor = AttributeVisitor()
        visitor.visit(self.ast)
        return visitor.results()
        

class DefaultExpressionFactory(BaseExpressionFactory):
    """ An implementor of IExpressionDelegateFactory that creates
    a DefaultExpression.

    """
    implements(IExpressionDelegateFactory)

    def __call__(self, global_ns, local_ns,):
        return DefaultExpression(code=self.code, 
                                 global_ns=global_ns, 
                                 local_ns=local_ns)


class BindingExpressionFactory(BaseExpressionFactory):
    """ An implementor of IExpressionDelegateFactory that creates
    a BindingExpression.
    
    """
    implements(IExpressionDelegateFactory)

    def __call__(self, global_ns, local_ns):
        return BindingExpression(code=self.code, 
                                 dependencies=self.dependencies,
                                 global_ns=global_ns, 
                                 local_ns=local_ns)


class DelegateExpressionFactory(BaseExpressionFactory):
    """ An implementor of IExpressionDelegateFactory that creates
    a DelegateExpression

    """
    implements(IExpressionDelegateFactory)

    def __call__(self, global_ns, local_ns):
        return DelegateExpression(code=self.code,
                                  dependencies=self.dependencies,
                                  global_ns=global_ns, 
                                  local_ns=local_ns)


class NotifierExpressionFactory(BaseExpressionFactory):
    """ An implementor of INotifierExpressionFactory that creates
    a NotifierExpression

    """
    implements(IExpressionNotifierFactory)

    def __call__(self, global_ns, local_ns):
        return NotifierExpression(code=self.code,
                                  global_ns=global_ns, 
                                  local_ns=local_ns)


