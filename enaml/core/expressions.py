#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from collections import namedtuple
from weakref import ref

from traits.api import HasTraits, Disallow, TraitListObject, TraitDictObject

from enaml.signaling import Signal

from .abstract_expressions import (
    AbstractExpression, AbstractListener, AbstractListenableExpression
)
from .code_tracing import CodeTracer, CodeInverter
from .dynamic_scope import DynamicScope, AbstractScopeListener, Nonlocals
from .funchelper import call_func


#------------------------------------------------------------------------------
# Traits Code Tracer
#------------------------------------------------------------------------------
class TraitsTracer(CodeTracer):
    """ A CodeTracer for tracing expressions which use Traits.

    This tracer maintains a running set of `traced_items` which are the
    (obj, name) pairs of traits items discovered during tracing.

    """
    def __init__(self):
        """ Initialize a TraitsTracer.

        """
        self.traced_items = set()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _trace_trait(self, obj, name):
        """ Add the trait object and name pair to the traced items.

        Parameters
        ----------
        obj : HasTraits
            The traits object owning the attribute.

        name : str
            The trait name to for which to bind a handler.

        """
        # Traits will happily force create a trait for things which aren't
        # actually traits. This tries to avoid most of that when possible.
        trait = obj.trait(name)
        if trait is not None and trait.trait_type is not Disallow:
            self.traced_items.add((obj, name))

    #--------------------------------------------------------------------------
    # AbstractScopeListener Interface
    #--------------------------------------------------------------------------
    def dynamic_load(self, obj, attr, value):
        """ Called when an object attribute is dynamically loaded.

        This will attach a listener to the object if it is a HasTraits
        instance. See also: `AbstractScopeListener.dynamic_load`.

        """
        if isinstance(obj, HasTraits):
            self._trace_trait(obj, attr)

    #--------------------------------------------------------------------------
    # CodeTracer Interface
    #--------------------------------------------------------------------------
    def load_attr(self, obj, attr):
        """ Called before the LOAD_ATTR opcode is executed.

        This will attach a listener to the object if it is a HasTraits
        instance. See also: `CodeTracer.dynamic_load`.

        """
        if isinstance(obj, HasTraits):
            self._trace_trait(obj, attr)

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
                self._trace_trait(obj, attr)

    def binary_subscr(self, obj, idx):
        """ Called before the BINARY_SUBSCR opcode is executed.

        This will attach a traits items listener if the object is a
        `TraitListObject` or a `TraitDictObject`.
        See also: `CodeTracer.get_iter`.

        """
        if isinstance(obj, (TraitListObject, TraitDictObject)):
            traits_obj = obj.object()
            if traits_obj is not None:
                if obj.name_items:
                    self._trace_trait(traits_obj, obj.name_items)

    def get_iter(self, obj):
        """ Called before the GET_ITER opcode is executed.

        This will attach a traits items listener if the object is a
        `TraitListObject`. See also: `CodeTracer.get_iter`.

        """
        if isinstance(obj, TraitListObject):
            traits_obj = obj.object()
            if traits_obj is not None:
                if obj.name_items:
                    self._trace_trait(traits_obj, obj.name_items)


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

        This method performs STORE_ATTR via the builtin `setattr`.
        See also: `CodeInverter.load_attr`.

        """
        setattr(obj, attr, value)

    def call_function(self, func, argtuple, argspec, value):
        """ Called before the CALL_FUNCTION opcode is executed.

        This method inverts a call to the builtin `getattr` into a call
        to the builtin `setattr`. All other calls will raise.
        See also: `CodeInverter.call_function`.

        """
        nargs = argspec & 0xFF
        nkwargs = (argspec >> 8) & 0xFF
        if (func is getattr and (nargs == 2 or nargs == 3) and nkwargs == 0):
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
            A function created by the Enaml compiler with bytecode that
            has been patched to support the semantics required of the
            expression.

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
class SubscriptionNotifier(object):
    """ A simple object used for attaching notification handlers.

    """
    __slots__ = ('expr', 'name', 'keyval', '__weakref__')

    def __init__(self, expr, name, keyval):
        """ Initialize a Notifier.

        Parameters
        ----------
        expr : AbstractListenableExpression
            The expression whose `invalidated` signal should be emitted
            when the notifier is triggered. It must be weakref-able.

        name : str
            The name to which the expression is bound.

        keyval : object
            An object to use for testing equivalency of notifiers.

        """
        self.expr = ref(expr)
        self.name = name
        self.keyval = keyval

    def notify(self):
        """ Notify that the expression is invalid.

        """
        expr = self.expr()
        if expr is not None:
            expr.invalidated.emit(self.name)


class SubscriptionExpression(BaseExpression):
    """ An implementation of AbstractListenableExpression for the `<<`
    operator.

    """
    # Note: __slots__ are not declared because Enaml Signals require a
    # __dict__ to exist on the instance.

    #: Private storage for the SubscriptionNotifier.
    _notifier = None

    #--------------------------------------------------------------------------
    # AbstractListenableExpression Interface
    #--------------------------------------------------------------------------
    invalidated = Signal()

    def eval(self, obj, name):
        """ Evaluate and return the expression value.

        """
        tracer = TraitsTracer()
        overrides = {'nonlocals': Nonlocals(obj, tracer)}
        scope = DynamicScope(obj, self._identifiers, overrides, tracer)
        with obj.operators:
            result = call_func(self._func, (tracer,), {}, scope)

        # In most cases, the object comprising the dependencies of an
        # expression will not change during subsequent evaluations of
        # the expression. Rather than creating a new notifier on each
        # pass and repeating the work of creating the change handlers,
        # a key for the dependencies is computed and a new notifier is
        # created only when the key changes. The key uses the id of an
        # object instead of the object itself so strong references to
        # the object are not maintained by the expression.
        id_ = id
        traced = tracer.traced_items
        keyval = frozenset((id_(obj), attr) for obj, attr in traced)
        notifier = self._notifier
        if notifier is None or keyval != notifier.keyval:
            notifier = SubscriptionNotifier(self, name, keyval)
            self._notifier = notifier
            handler = notifier.notify
            for obj, attr in traced:
                obj.on_trait_change(handler, attr)

        return result


AbstractListenableExpression.register(SubscriptionExpression)


#------------------------------------------------------------------------------
# Delegation Expression
#------------------------------------------------------------------------------
class DelegationExpression(SubscriptionExpression):
    """ An object which implements the `:=` operator by implementing the
    AbstractListenableExpression and AbstractListener interfaces.

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

