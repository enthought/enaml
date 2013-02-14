#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from types import FunctionType

from atom.api import AtomMeta, Member, ReadOnly, Value, Signal, Event, null

from .dynamic_scope import DynamicAttributeError
from .exceptions import DeclarativeNameError, OperatorLookupError
from .object import Object
from .operator_context import OperatorContext


def scope_lookup(name, scope, description):
    """ A function which retrieves a name from a scope.

    If the lookup fails, a DeclarativeNameError is raised. This can
    be used to lookup names for a description dict from a global scope
    with decent error reporting when the lookup fails.

    Parameters
    ----------
    name : str
        The name to retreive from the scope.

    scope : mapping
        A mapping object.

    description : dict
        The description dictionary associated with the lookup.

    """
    try:
        item = scope[name]
    except KeyError:
        lineno = description['lineno']
        filename = description['filename']
        block = description['block']
        raise DeclarativeNameError(name, filename, lineno, block)
    return item


def setup_bindings(instance, bindings, identifiers, f_globals):
    """ Setup the expression bindings for a declarative instance.

    Parameters
    ----------
    instance : Declarative
        The declarative instance which owns the bindings.

    bindings : list
        A list of binding dicts created by the enaml compiler.

    identifiers : dict
        The identifiers scope to associate with the bindings.

    f_globals : dict
        The globals dict to associate with the bindings.

    """
    operators = instance.operators
    for binding in bindings:
        opname = binding['operator']
        try:
            operator = operators[opname]
        except KeyError:
            filename = binding['filename']
            lineno = binding['lineno']
            block = binding['block']
            raise OperatorLookupError(opname, filename, lineno, block)
        code = binding['code']
        # If the code is a tuple, it represents a delegation
        # expression which is a combination of subscription
        # and update functions.
        if isinstance(code, tuple):
            sub_code, upd_code = code
            func = FunctionType(sub_code, f_globals)
            func._update = FunctionType(upd_code, f_globals)
        else:
            func = FunctionType(code, f_globals)
        operator(instance, binding['name'], func, identifiers)


class DeclarativeProperty(Member):

    __slots__ = ('_member',)

    def __init__(self, member):
        self._member = member
        self.has_default = True
        self.has_validate = True

    def default(self, owner, name):
        value = owner.eval_expression(name)
        member = self._member
        if value is not null:
            if member.has_validate:
                value = member.validate(owner, name, null, value)
        elif member.has_default:
            value = member.default(owner, name)
        return value

    def validate(self, owner, name, old, new):
        member = self._member
        if member.has_validate:
            new = member.validate(owner, name, old, new)
        return new

    def __set__(self, owner, value):
        name = self._name
        old = getattr(owner, name)
        super(DeclarativeProperty, self).__set__(owner, value)
        new = getattr(owner, name)
        if old != new:
            owner.run_listeners(name, old, new)


class DeclarativeMeta(AtomMeta):
    """ The type of declarative classes.

    The Declarative metaclass is responsible for collecting all of the
    declarative properties, events, and signals defined on the class so
    that declarative expressions and listeners may be efficiently bound.

    """
    def __new__(meta, name, bases, dct):
        cls = super(DeclarativeMeta, meta).__new__(meta, name, bases, dct)
        properties = set()
        signals = set()
        events = set()
        for base in reversed(cls.__mro__[1:]):
            if isinstance(base, DeclarativeMeta):
                properties.update(base.__declarative_properties__)
                signals.update(base.__declarative_signals__)
                events.update(base.__declarative_events__)
        for key, value in dct.iteritems():
            if isinstance(value, DeclarativeProperty):
                properties.add(key)
            elif isinstance(value, Signal):
                signals.add(key)
            elif isinstance(value, Event):
                events.add(key)
            else:
                print value
        cls.__declarative_properties__ = properties
        cls.__declarative_signals__ = signals
        cls.__declarative_events__ = events
        return cls


#------------------------------------------------------------------------------
# Declarative
#------------------------------------------------------------------------------
class Declarative(Object):
    """ The most base class of the Enaml declarative objects.

    This class provides the core functionality required of declarative
    Enaml types. It can be used directly in a declarative Enaml object
    tree to store and react to state changes. It has no concept of a
    visual representation; that functionality is added by subclasses.

    """
    __metaclass__ = DeclarativeMeta

    #: A readonly property which returns the current instance of the
    #: component. This allows declarative Enaml expressions to access
    #: 'self' according to Enaml's dynamic scoping rules.
    self = property(lambda self: self)

    #: The operator context used to build out this instance. This is
    #: assigned during object instantiation. It should not be edited
    #: by user code.
    operators = ReadOnly()

    #: Private storage values. These should *never* be manipulated by
    #: user code. For performance reasons, these are not type checked.
    _expressions = Value(factory=list)
    _listeners = Value(factory=list)

    def __init__(self, parent=None, **kwargs):
        """ Initialize a declarative component.

        Parameters
        ----------
        parent : Object or None, optional
            The Object instance which is the parent of this object, or
            None if the object has no parent. Defaults to None.

        **kwargs
            Additional keyword arguments needed for initialization.

        """
        self.operators = OperatorContext.active_context()
        super(Declarative, self).__init__(parent, **kwargs)

    #--------------------------------------------------------------------------
    # Declarative API
    #--------------------------------------------------------------------------
    def populate(self, description, identifiers, f_globals):
        """ Populate this declarative instance from a description.

        This method is called when the object was created from within
        a declarative context. In particular, there are two times when
        it may be called:

            - The first is when a type created from the `enamldef`
              keyword is instatiated; in this case, the method is
              invoked by the EnamlDef metaclass.

            - The second occurs when the object is instantiated by
              its parent from within its parent's `populate` method.

        In the first case, the description dict will contain the key
        `enamldef: True`, indicating that the object is being created
        from a "top-level" `enamldef` block.

        In the second case, the dict will have the key `enamldef: False`
        indicating that the object is being populated as a declarative
        child of some other parent.

        Subclasses may reimplement this method to gain custom control
        over how the children for its instances are created.

        *** This method may be called multiple times ***

        Consider the following sample:

        enamldef Foo(PushButton):
            text = 'bar'

        enamldef Bar(Foo):
            fgcolor = 'red'

        enamldef Main(Window):
            Container:
                Bar:
                    bgcolor = 'blue'

        The instance of `Bar` which is created as the `Container` child
        will have its `populate` method called three times: the first
        to populate the data from the `Foo` block, the second to populate
        the data from the `Bar` block, and the third to populate the
        data from the `Main` block.

        Parameters
        ----------
        description : dict
            The description dictionary for the instance.

        identifiers : dict
            The dictionary of identifiers to use for the bindings.

        f_globals : dict
            The dictionary of globals for the scope in which the object
            was declared.

        Notes
        -----
        The caller of this method should enter the child event context
        of the instance before invoking the method. This reduces the
        number of child events which are generated during startup.

        """
        ident = description['identifier']
        if ident:
            identifiers[ident] = self
        bindings = description['bindings']
        if len(bindings) > 0:
            setup_bindings(self, bindings, identifiers, f_globals)
        children = description['children']
        if len(children) > 0:
            for child in children:
                cls = scope_lookup(child['type'], f_globals, child)
                instance = cls(self)
                instance.populate(child, identifiers, f_globals)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def bind_expression(self, expression):
        """ Bind an expression to a declarative property.

        Parameters
        ----------
        expression : AbstractExpression
            A concrete implementation of AbstractExpression. This value
            is not type checked for performance reasons. It is assumed
            that the caller provides a correct value.

        """
        if expression.name not in self.__declarative_properties__:
            msg = "Cannot bind expression. '%s' is not a declarative property "
            msg += "on the %s object."
            raise TypeError(msg % (expression.name, self))
        # All expressions are added, even if they override an old one.
        # When looking up an expression, it is done in reverse order so
        # that the most recently bound expression is used.
        self._expressions.append(expression)

    def bind_listener(self, listener):
        """ Bind a listener to a declarative property.

        Parameters
        ----------
        listener : AbstractListener
            A concrete implementation of AbstractListener. This value
            is not type checked for performance reasons. It is assumed
            that the caller provides a correct value.

        """
        print self.__declarative_signals__
        name = listener.name
        if name in self.__declarative_properties__:
            self._listeners.append(listener)
        elif name in self.__declarative_signals__:
            signal = getattr(self, name)
            signal.connect(lambda self: self.run_listeners(name, null, null))
            self._listeners.append(listener)
        else:
            msg = "Cannot bind listener. '%s' is not a declarative property "
            msg += "on the %s object."
            raise AttributeError(msg % (listener.name, self))

    def eval_expression(self, name):
        """ Evaluate a bound expression with the given name.

        Parameters
        ----------
        name : str
            The name of the attribute with the bound expression.

        Returns
        -------
        result : object or NotImplemented
            The result of evaluating the expression, or NotImplemented
            if there is no expression bound to the given name.

        """
        for expression in reversed(self._expressions):
            if expression.name == name:
                return expression.eval(self, name)
        return null

    def refresh_expression(self, name):
        """ Refresh the value of a bound expression.

        Parameters
        ----------
        name : str
            The attribute name to which the invalid expression is bound.

        """
        value = self.eval_expression(name)
        if value is not null:
            setattr(self, name, value)

    def run_listeners(self, name, old, new):
        """ Run the listeners bound to the given attribute name.

        Parameters
        ----------
        name : str
            The name of the attribute with the bound listeners.

        old : object
            The old value to pass to the listeners.

        new : object
            The new value to pass to the listeners.

        """
        for listener in self._listeners:
            if listener.name == name:
                listener.value_changed(self, name, old, new)

