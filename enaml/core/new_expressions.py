#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import namedtuple

from traits.api import HasTraits, Disallow, TraitListObject, TraitDictObject

from enaml.signaling import Signal

from .abstract_expressions import AbstractExpression, AbstractListener
from .code_tracing import CodeTracer, CodeInverter
from .dynamic_scope import DynamicScope, AbstractScopeListener, Nonlocals
from .funchelper import call_func


#------------------------------------------------------------------------------
# Traits Code Tracer
#------------------------------------------------------------------------------
class TraitsTracer(CodeTracer):
    """ A CodeTracer for tracing expressions using Traits.

    """
    def __init__(self, notifier):
        """ Initialize a TraitsTracer.

        Parameters
        ----------
        notifier : AbstractNotifier
            The notifier to use as a handler for traits dependencies.

        """
        self._notifier = notifier
        self._bound = set()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _bind_trait(self, obj, name):
        """ Bind the a handler for the named trait on the object.

        Parameters
        ----------
        obj : HasTraits
            The traits object owning the attribute.

        name : str
            The trait name to for which to bind a handler.

        """
        trait = obj.trait(name)
        if trait is not None and trait is not Disallow:
            key = (obj, name)
            bound = self._bound
            if key not in bound:
                obj.on_trait_change(self._notifier.notify, name)
                bound.add(key)

    #--------------------------------------------------------------------------
    # AbstractScopeListener Interface
    #--------------------------------------------------------------------------
    def dynamic_load(self, obj, attr, value):
        """ Called when an object attribute is dynamically loaded.

        This will attach a listener to the object if it is a HasTraits
        instance. See also: `AbstractScopeListener.dynamic_load`.

        """
        if isinstance(obj, HasTraits):
            self._bind_trait(obj, attr)

    #--------------------------------------------------------------------------
    # CodeTracer Interface
    #--------------------------------------------------------------------------
    def load_attr(self, obj, attr):
        """ Called before the LOAD_ATTR opcode is executed.

        This will attach a listener to the object if it is a HasTraits
        instance. See also: `CodeTracer.dynamic_load`.

        """
        if isinstance(obj, HasTraits):
            self._bind_trait(obj, attr)

    def call_function(self, func, argtuple, argspec):
        """ Called before the CALL_FUNCTION opcode is executed.

        This will attach a listener if the func is the builtin `getattr`
        and the object is a HasTraits instance.
        See also: `CodeTracer.call_function`

        """
        nargs = argspec & 0xFF
        nkwargs = (argspec >> 8) & 0xFF
        if (func is getattr and (nargs == 2 or nargs == 3) and nkwargs == 0):
            obj, attr = argtuple[0], argtuple[1]
            if isinstance(obj, HasTraits) and isinstance(attr, basestring):
                self._bind_trait(obj, attr)

    def binary_subscr(self, obj, idx):
        """ Called before the BINARY_SUBSCR opcode is executed.

        This will attach a trait if the object is a `TraitListObject`
        or a `TraitDictObject`. See also: `CodeTracer.get_iter`.

        """
        if isinstance(obj, (TraitListObject, TraitDictObject)):
            o = obj.object()
            if o is not None:
                if obj.name_items:
                    self._bind_trait(o, obj.name_items)

    def get_iter(self, obj):
        """ Called before the GET_ITER opcode is executed.

        This will attach a trait if the object is a `TraitListObject`.
        See also: `CodeTracer.get_iter`.

        """
        if isinstance(obj, TraitListObject):
            o = obj.object()
            if o is not None:
                if obj.name_items:
                    self._bind_trait(o, obj.name_items)


AbstractScopeListener.register(TraitsTracer)


#------------------------------------------------------------------------------
# Standard Code Inverter
#------------------------------------------------------------------------------
class StandardInverter(CodeInverter):
    """ The standard code inverter for Enaml expressions.

    """
    def __init__(self, nonlocals):
        """ Initialize a StandardInverter.

        Parameters
        ----------
        nonlocals : Nonlocals
            The nonlocal scope for the executing expression.

        """
        self._nonlocals = nonlocals

    #--------------------------------------------------------------------------
    # CodeInverter Interface
    #--------------------------------------------------------------------------
    def load_name(self, name, value):
        """ Called before the LOAD_NAME opcode is executed.

        This method performs STORE_NAME by storing to the nonlocals.
        See also: `CodeInverter.load_name`.

        """
        self._nonlocals[name] = value

    def load_attr(self, obj, attr, value):
        """ Called before the LOAD_ATTR opcode is executed.

        This method performs STORE_ATTR via the builting `setattr`.
        See also: `CodeInverter.load_attr`.

        """
        setattr(obj, attr, value)

    def call_function(self, func, argtuple, argspec, value):
        """ Called before the CALL_FUNCTION opcode is executed.

        This method inverts a call to the builtin `getattr` into a call
        to the builtin `setattr`, and allows the builtin `setattr` to
        execute unmodified. All other calls will raise.
        See also: `CodeInverter.call_function`.

        """
        nargs = argspec & 0xFF
        nkwargs = (argspec >> 8) & 0xFF
        if (func is getattr and (nargs == 2 or nargs == 3) and nkwargs == 0):
            obj, attr = argtuple[0], argtuple[1]
            setattr(obj, attr, value)
        elif (func is setattr and nargs == 3 and nkwargs == 0):
            obj, attr = argtuple[0], argtuple[1]
            setattr(obj, attr, value)
        else:
            self.fail()

    def binary_subscr(self, obj, idx, value):
        """ Called before the BINARY_SUBSCR opcode is executed.

        This method performs a STORE_SUBSCR operation through standard
        setitem semantics. See also: `CodeInverter.binary_subscr`.

        """
        obj[idx] = value


#------------------------------------------------------------------------------
# Notifier
#------------------------------------------------------------------------------
class Notifier(object):
    """ A simple object used to attach notification handlers.

    """
    __slots__ = ('_expr', '_name', '__weakref__')

    def __init__(self, expr, name):
        """ Initialize a TraitNotifier.

        Parameters
        ----------
        expr : AbstractExpression
            The expression whose `invalidated` signal should be emitted
            when the notifier is triggered.

        name : str
            The name to which the expression is bound.

        """
        self._expr = expr
        self._name = name

    def notify(self):
        """ Notify that the expression is invalid.

        """
        self._expr.invalidated.emit(self._name)


#------------------------------------------------------------------------------
# Base Expression
#------------------------------------------------------------------------------
class BaseExpression(object):
    """ The base class of the standard Enaml expression classes.

    """
    __slots__ = ('_func', '_identifiers')

    def __init__(self, func, identifiers):
        """ Initialize a BaseExpression.

        Parameters
        ----------
        func : types.FunctionType
            A function whose bytecode has been patch support dynamic
            scoping but not tracing.

        identifiers : dict
            The dictionary of identifiers available to the function.

        """
        self._func = func
        self._identifiers = identifiers


#------------------------------------------------------------------------------
# Simple Expression
#------------------------------------------------------------------------------
class SimpleExpression(BaseExpression):
    """ An implementation of AbstractExpression for the `=` operator.

    """
    __slots__ = ()

    # SimpleExpression does not support invalidation.
    invalidated = None

    #--------------------------------------------------------------------------
    # AbstractExpression Interface
    #--------------------------------------------------------------------------
    def eval(self, obj, name):
        """ Evaluate and return the expression value.

        """
        overrides = {'nonlocals': Nonlocals(obj, None)}
        scope = DynamicScope(obj, self._identifiers, overrides, None)
        with obj.operators:
            return call_func(self._func, (), {}, scope)


AbstractExpression.register(SimpleExpression)


#------------------------------------------------------------------------------
# Notification Expression
#------------------------------------------------------------------------------
class NotificationExpression(BaseExpression):
    """ An implementation of AbstractListener for the `::` operator.

    """
    __slots__ = ()

    #: A namedtuple which is used to pass arguments to the expression.
    event = namedtuple('event', 'obj name old new')

    #--------------------------------------------------------------------------
    # AbstractListener Interface
    #--------------------------------------------------------------------------
    def value_changed(self, obj, name, old, new):
        """ Called when the attribute on the object has changed.

        """
        overrides = {
            'event': self.event(obj, name, old, new),
            'nonlocals': Nonlocals(obj, None),
        }
        scope = DynamicScope(obj, self._identifiers, overrides, None)
        with obj.operators:
            call_func(self._func, (), {}, scope)


AbstractListener.register(NotificationExpression)


#------------------------------------------------------------------------------
# Update Expression
#------------------------------------------------------------------------------
class UpdateExpression(BaseExpression):
    """ An implementation of AbstractListener for the `>>` operator.

    """
    __slots__ = ()

    #--------------------------------------------------------------------------
    # AbstractListener Interface
    #--------------------------------------------------------------------------
    def value_changed(self, obj, name, old, new):
        """ Called when the attribute on the object has changed.

        """
        nonlocals = Nonlocals(obj, None)
        inverter = StandardInverter(nonlocals)
        overrides = {'nonlocals': nonlocals}
        scope = DynamicScope(obj, self._identifiers, overrides, None)
        with obj.operators:
            call_func(self._func, (inverter, new), {}, scope)


AbstractListener.register(UpdateExpression)


#------------------------------------------------------------------------------
# Subcsription Expression
#------------------------------------------------------------------------------
class SubscriptionExpression(BaseExpression):
    """ An implementation of AbstractExpression for the `<<` operator.

    """
    # Slots not declared because Signal requires a __dict__
    invalidated = Signal()

    # Internal storage for the notifier
    _notifier = None

    #--------------------------------------------------------------------------
    # AbstractExpression Interface
    #--------------------------------------------------------------------------
    def eval(self, obj, name):
        """ Evaluate and return the expression value.

        """
        notifier = self._notifier
        if notifier is not None:
            notifier._expr = None # break the ref cycle
        notifier = self._notifier = Notifier(self, name)
        tracer = TraitsTracer(notifier)
        overrides = {'nonlocals': Nonlocals(obj, tracer)}
        scope = DynamicScope(obj, self._identifiers, overrides, tracer)
        with obj.operators:
            return call_func(self._func, (tracer,), {}, scope)


AbstractExpression.register(SubscriptionExpression)


#------------------------------------------------------------------------------
# Delegation Expression
#------------------------------------------------------------------------------
class DelegationExpression(SubscriptionExpression):
    """

    """
    #--------------------------------------------------------------------------
    # AbstractListener Interface
    #--------------------------------------------------------------------------
    def value_changed(self, obj, name, old, new):
        """ Called when the attribute on the object has changed.

        """
        nonlocals = Nonlocals(obj, None)
        inverter = StandardInverter(nonlocals)
        overrides = {'nonlocals': nonlocals}
        scope = DynamicScope(obj, self._identifiers, overrides, None)
        with obj.operators:
            call_func(self._func._setter, (inverter, new), {}, scope)


AbstractListener.register(DelegationExpression)

