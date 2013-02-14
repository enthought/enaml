#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .declarative import DeclarativeExpression, DeclarativeListener
from .dynamic_scope import DynamicScope, Nonlocals
from .funchelper import call_func
from .traits_tracer import TraitsTracer
from .standard_inverter import StandardInverter


class BaseExpression(object):
    """ The base class of the standard Enaml expression classes.

    """
    __slots__ = ('_func', '_f_locals')

    def __init__(self, func, f_locals):
        """ Initialize a BaseExpression.

        Parameters
        ----------
        func : types.FunctionType
            A function created by the Enaml compiler with bytecode that
            has been patched to support the semantics required of the
            expression.

        f_locals : dict
            The dictionary of local identifiers for the function.

        """
        self._func = func
        self._f_locals = f_locals


class SimpleExpression(BaseExpression):
    """ An implementation of AbstractExpression for the `=` operator.

    """
    __slots__ = ()

    def evaluate(self, owner):
        """ Evaluate and return the expression value.

        """
        overrides = {'nonlocals': Nonlocals(owner, None)}
        scope = DynamicScope(owner, self._f_locals, overrides, None)
        with owner.operators:
            return call_func(self._func, (), {}, scope)


class NotificationExpression(BaseExpression):
    """ An implementation of AbstractListener for the `::` operator.

    """
    __slots__ = ()

    def property_changed(self, change):
        """ Called when the attribute on the owner has changed.

        """
        owner = change.object
        nonlocals = Nonlocals(owner, None)
        overrides = {'change': change, 'event': change, 'nonlocals': nonlocals}
        scope = DynamicScope(owner, self._f_locals, overrides, None)
        with owner.operators:
            call_func(self._func, (), {}, scope)


class UpdateExpression(BaseExpression):
    """ An implementation of AbstractListener for the `>>` operator.

    """
    __slots__ = ()

    def property_changed(self, change):
        """ Called when the attribute on the owner has changed.

        """
        owner = change.object
        nonlocals = Nonlocals(owner, None)
        overrides = {'nonlocals': nonlocals}
        inverter = StandardInverter(nonlocals)
        scope = DynamicScope(owner, self._f_locals, overrides, None)
        with owner.operators:
            call_func(self._func, (inverter, change.new), {}, scope)


class SubscriptionNotifier(object):
    """ A simple object used for attaching notification handlers.

    """
    __slots__ = ('notifier', 'name', 'keyval', '__weakref__')

    def __init__(self, notifier, name, keyval):
        """ Initialize a SubscriptionNotifier.

        Parameters
        ----------
        notifier : callable
            ...

        name : str
            The name to which the expression is bound.

        keyval : object
            An object to use for testing equivalency of notifiers.

        """
        self.notifier = notifier
        self.name = name
        self.keyval = keyval

    def notify(self):
        """ Notify that the expression is invalid.

        """
        self.notifier(self.name)


class SubscriptionExpression(BaseExpression):
    """ An implementation of AbstractExpression for the `<<` operator.

    """
    __slots__ = ('_notifier')

    def __init__(self, func, f_locals):
        """ Initialize a SubscriptionExpression.

        """
        super(SubscriptionExpression, self).__init__(func, f_locals)
        self._notifier = None

    def evaluate(self, owner):
        """ Evaluate and return the expression value.

        """
        tracer = TraitsTracer()
        overrides = {'nonlocals': Nonlocals(owner, tracer)}
        scope = DynamicScope(owner, self._f_locals, overrides, tracer)
        with owner.operators:
            result = call_func(self._func, (tracer,), {}, scope)

        # In most cases, the objects comprising the dependencies of an
        # expression will not change during subsequent evaluations of
        # the expression. Rather than creating a new notifier on each
        # pass and repeating the work of creating the change handlers,
        # a key for the dependencies is computed and a new notifier is
        # created only when the key changes. The key uses the id of an
        # object instead of the object itself so strong references to
        # the object are not maintained by the expression. A sorted
        # tuple is used instead of a frozenset to reduced the memory
        # footprint. It is slightly slower to compute but ~5x smaller.
        traced = tracer.traced_items
        keyval = tuple(sorted((id(obj), attr) for obj, attr in traced))
        notifier = self._notifier
        if notifier is None or keyval != notifier.keyval:
            name = self._func.__name__
            notifier = SubscriptionNotifier(owner.notifier, name, keyval)
            self._notifier = notifier
            handler = notifier.notify
            for obj, attr in traced:
                obj.on_trait_change(handler, attr)

        return result


class DelegationExpression(SubscriptionExpression):
    """ An expression and listener implementation for the `:=` operator.

    """
    __slots__ = ()

    def property_changed(self, change):
        """ Called when the attribute on the owner has changed.

        """
        owner = change.object
        nonlocals = Nonlocals(owner, None)
        inverter = StandardInverter(nonlocals)
        overrides = {'nonlocals': nonlocals}
        scope = DynamicScope(owner, self._f_locals, overrides, None)
        with owner.operators:
            call_func(self._func._update, (inverter, change.new), {}, scope)


DeclarativeExpression.register(SimpleExpression)
DeclarativeExpression.register(SubscriptionExpression)
DeclarativeListener.register(NotificationExpression)
DeclarativeListener.register(UpdateExpression)
DeclarativeListener.register(DelegationExpression)

