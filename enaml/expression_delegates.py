import ast
from collections import namedtuple
import types

from traits.api import (Any, CTrait, HasStrictTraits, Tuple, HasTraits, 
                        Instance, Property, Str, implements, cached_property,
                        Interface, WeakRef)

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

    def bind(self, obj, name):
        """ Called automatically when the delegate should bind listeners.

        This is called automatically by the enaml widget when the delegate
        should hook up listeners.

        Arguments
        ---------
        obj : Component
            The enaml component widget.
        
        name : string
            The name of the attribute on the component to which we
            are delegating.

        """
        raise NotImplementedError

class IExpressionDelegateFactory(Interface):
    """ Defines the IExpressionDelegateFactory interface for Enaml.

    The IExpressionDelegateFactory defines the interface for creating 
    factories that create IExpressionDelegate objects which bind code 
    and/or expressions to the Enaml object tree.

    Methods
    -------
    delgate()
        Creates an IExpressionDelegate instance that is ready to be
        added to an Enaml ui object.

    """
    def create(self):
        """ Creates an IExpressionDelegate instance.

        Creates an IExpressionDelegate instance that is ready to be
        added to an Enaml ui object.

        Arguments
        ---------
        None

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

        """
        raise NotImplementedError


class IExpressionNotifierFactory(Interface):
    """ Defines the IExpressionNotifierFactory interface for Enaml.

    An IExpressionNotifierFactory should create and return an
    IExpressionNotifier that will execute and expression in response
    to a change on an attribute of an Enaml widget.

    Methods
    -------
    notifier()
        Creates and returns an IExpressionNotifier.

    """
    def create(self):
        """ Creates and returns an IExpressionNotifier.

        Arguments
        ---------
        None

        Returns
        -------
        result : IExpressionNotifier
            The expression notifier that will handle the notifications.

        """
        raise NotImplementedError


#-------------------------------------------------------------------------------
# Implementations
#-------------------------------------------------------------------------------
class BaseExpression(HasStrictTraits):

    # The code object that holds the expression
    code = Instance(types.CodeType)

    # The global namespace for the code.
    global_ns = Instance(dict)

    # The local namespace for the code.
    local_ns = Instance(dict)

    # The object for which we are providing delegation. We don't 
    # specify the type (which would be Component) to avoid a circular
    # import.
    obj = WeakRef

    # The name on the object which we are delegating
    name = Str

    # The trait to validate against
    validate_trait = Instance(CTrait)

    # The value property
    value = Property

    # The underlying value store
    _value = Any


class DefaultExpression(BaseExpression):
    
    implements(IExpressionDelegate)

    def bind(self, obj, name):
        self.obj = obj
        self.name = name

    def _get_value(self):
        return self._value
    
    def _set_value(self, val):
        val = self.validate_trait.validate(self.obj, self.name, val)
        self._value = val

    def __value_default(self):
        val = eval(self.code, self.global_ns, self.local_ns)
        val = self.validate_trait.validate(self.obj, self.name, val)
        return val


class BindingExpression(DefaultExpression):

    # The possible dependencies for this delegate in the 
    # form ((root, attr), (root, attr), ...)
    dependencies = Tuple

    def bind(self, obj, name):
        super(BindingExpression, self).bind()
        self.obj = obj
        self.name = name
        for dep_name, attr in self.dependencies:
            try:
                dep = local_ns[dep_name]
            except KeyError:
                try:
                    dep = global_ns[dep_name]
                except KeyError:
                    msg = '`%s` is not defined or accessible in the namespace.'
                    raise NameError(msg % dep_name)
            if isinstance(dep, HasTraits):
                dep.on_trait_change(self.refresh_value, dep_name)

    def refresh_value(self):
        val = eval(self.code, self.global_ns, self.local_ns)
        self.value = val


class DelegateExpression(DefaultExpression):

    # The delegate dependency for this expression
    dependencies = Tuple((Str, Str))
    
    # The object to which we are delegating
    delegate_obj = Any

    # The attribute on the delegate to which we are delegating
    delegate_attr_name = Str

    def bind(self, obj, name):
        super(DelegateExpression, self).bind(obj, name)
        obj_name, attr_name = self.dependencies
        try:
            obj = local_ns[obj_name]
        except KeyError:
            try:
                obj = global_ns[obj_name]
            except KeyError:
                msg = '`%s` is not defined or accessible in the namespace.'
                raise NameError(msg % obj_name)
        self.delegate_obj = obj
        self.delegate_attr_name = attr_name
        if isinstance(obj, HasTraits):
            obj.on_trait_change(self.refresh_value, attr_name)

    def _get_value(self):
        # Overridden from the parent class to pull from the delegate.
        val = getattr(self.delegate_obj, self.delegate_attr_name)
        val = self.validate_trait.validate(self.obj, self.name, val)
        return val

    def _set_value(self, val):
        # Overridden from the parent class to set on the delegate
        val = self.validate_trait.validate(self.obj, self.name, val)
        setattr(self.delegate_obj, self.delegate_attr_name, val)
        
    def __value_default(self):
        # Overridden from the parent class to pull from the delegate.
        return self._get_value()

    def refresh_value(self):
        # We just need to invalidate the 'value' property so its
        # listeners will pull new values. The property getter does 
        # the actual delegation.
        self._value = not self._value


class NotifierExpression(BaseExpression):
    
    implements(IExpressionNotifier)

    message = namedtuple('Message', ('obj', 'name', 'old', 'new'))

    def bind(self, obj, name):
        self.obj = obj
        self.name = name
        obj.on_trait_change(self.notify, name)

    def notify(self, obj, name, old, new):
        local_ns = self.local_ns
        local_ns['msg'] = self.message(obj, name, old, new)
        eval(self.code, self.global_ns, local_ns)


#-------------------------------------------------------------------------------
# Factory implementations
#-------------------------------------------------------------------------------
class BaseExpressionFactory(HasStrictTraits):

    ast = Instance(ast.Expression)

    code = Property(Instance(types.CodeType), depends_on='ast')

    dependencies = Property(Tuple, depends_on='ast')

    def __init__(self, ast):
        super(BaseInterceptorFactory, self).__init__()
        self.ast = ast

    @cached_property
    def _get_code(self):
        return compile(self.ast, 'Enaml', 'eval')

    @cached_property
    def _get_dependencies(self):
        visitor = AttributeVisitor()
        visitor.visit(self.ast)
        return visitor.results()
        

class DefaultExpressionFactory(BaseExpressionFactory):

    implements(IExpressionDelegateFactory)

    def create(self):
        return DefaultExpression(code=self.code)


class BindingExpressionFactory(BaseExpressionFactory):
    
    implements(IExpressionDelegateFactory)

    def create(self):
        b = BindingExpression(code=self.code, dependencies=self.dependencies)
        return b


class DelegateExpressionFactory(BaseExpressionFactory):

    implements(IExpressionDelegateFactory)

    def create(self):
        d = DelegateExpression(code=self.code, dependencies=self.dependencies)
        return d


class NotifierExpressionFactory(BaseExpressionFactory):

    implements(IExpressionNotifierFactory)

    def create(self):
        return NotifierExpression(code=self.code)

