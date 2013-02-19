#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" The default Enaml operators.

The operator functions are called by the Enaml runtime to implement the
expression binding semantics of the Enaml operators. The functions are
passed a number of arguments in order to perform their work:

Parameters
----------
obj : Declarative
    The Declarative object which owns the expression which is being
    bound.

name : string
    The name of the attribute on the object which is being bound.

func : types.FunctionType
    A function with bytecode that has been patched by the Enaml compiler
    for semantics specific to the operator. The docs for each operator
    given a more complete description of this function, since it varies
    for each operator.

identifiers : dict
    The dictionary of identifiers available to the expression. This dict
    is shared amongst all expressions within a given lexical scope. It
    should therefore not be modified or copied since identifiers may
    continue to be added to this dict as runtime execution continues.

"""
from atom.api import Atom, Member, Event

from .declarative import DeclarativeProperty, DeclarativeExpression
from .dynamic_scope import DynamicScope, Nonlocals
from .funchelper import call_func
from .standard_inverter import StandardInverter
from .standard_tracer import StandardTracer


class OperatorBase(object):
    """ The base class of the standard Enaml operator implementations.

    """
    __slots__ = ('func', 'f_locals')

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
        self.func = func
        self.f_locals = f_locals

    @property
    def name(self):
        """ Get the name to which the operator is bound.

        """
        return self.func.__name__


class OpSimple(OperatorBase):
    """ A class which implements the `=` operator.

    This class implements the `DeclarativeExpression` interface.

    """
    __slots__ = ()

    def evaluate(self, owner):
        """ Evaluate and return the expression value.

        """
        overrides = {'nonlocals': Nonlocals(owner, None), 'self': owner}
        scope = DynamicScope(owner, self.f_locals, overrides, None)
        with owner.operators:
            return call_func(self.func, (), {}, scope)


DeclarativeExpression.register(OpSimple)


class OpNotify(OperatorBase):
    """ A class which implements the `::` operator.

    Instances of this class can be used as Atom observers.

    """
    __slots__ = ()

    def __call__(self, change):
        """ Called when the attribute on the owner has changed.

        """
        owner = change.object
        nonlocals = Nonlocals(owner, None)
        overrides = {
            'change': change, 'event': change,
            'nonlocals': nonlocals, 'self': owner
        }
        scope = DynamicScope(owner, self.f_locals, overrides, None)
        with owner.operators:
            call_func(self.func, (), {}, scope)


class OpUpdate(OperatorBase):
    """ A class which implements the `>>` operator.

    Instances of this class can be used as Atom observers.

    """
    __slots__ = ()

    def __call__(self, change):
        """ Called when the attribute on the owner has changed.

        """
        owner = change.object
        nonlocals = Nonlocals(owner, None)
        overrides = {'nonlocals': nonlocals, 'self': owner}
        inverter = StandardInverter(nonlocals)
        scope = DynamicScope(owner, self.f_locals, overrides, None)
        with owner.operators:
            call_func(self.func, (inverter, change.new), {}, scope)


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

    def notify(self, change):
        """ Notify that the expression is invalid.

        """
        self.notifier(self.name)


class OpSubscribe(OperatorBase):
    """ A class which implements the `<<` operator.

    This class implements the `DeclarativeExpression` interface.

    """
    __slots__ = 'notifier'

    def __init__(self, func, f_locals):
        """ Initialize a SubscriptionExpression.

        """
        super(OpSubscribe, self).__init__(func, f_locals)
        self.notifier = None

    def evaluate(self, owner):
        """ Evaluate and return the expression value.

        """
        tracer = StandardTracer()
        overrides = {'nonlocals': Nonlocals(owner, tracer), 'self': owner}
        scope = DynamicScope(owner, self.f_locals, overrides, tracer)
        with owner.operators:
            result = call_func(self.func, (tracer,), {}, scope)

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
        notifier = self.notifier
        if notifier is None or keyval != notifier.keyval:
            name = self.func.__name__
            onotifier = owner._expression_notifier
            notifier = SubscriptionNotifier(onotifier, name, keyval)
            self.notifier = notifier
            handler = notifier.notify
            for obj, attr in traced:
                if isinstance(obj, Atom):
                    obj.observe(attr, handler)
                else:
                    obj.on_trait_change(handler, attr)

        return result


DeclarativeExpression.register(OpSubscribe)


class OpDelegate(OpSubscribe):
    """ An expression and listener implementation for the `:=` operator.

    Instances of this class can by used at Atom notifiers.

    """
    __slots__ = ()

    def __call__(self, change):
        """ Called when the attribute on the owner has changed.

        """
        owner = change.object
        nonlocals = Nonlocals(owner, None)
        inverter = StandardInverter(nonlocals)
        overrides = {'nonlocals': nonlocals, 'self': owner}
        scope = DynamicScope(owner, self.f_locals, overrides, None)
        with owner.operators:
            call_func(self.func._update, (inverter, change.new), {}, scope)


# XXX generate a pseudo line number traceback for binding failures

def op_simple(obj, name, func, identifiers):
    """ The default Enaml operator function for `=` bindings.

    """
    member = obj.lookup_member(name)
    if not isinstance(member, DeclarativeProperty):
        msg = "Cannot bind expression. '%s' is not a declarative property "
        msg += "on a '%s' object."
        raise TypeError(msg % (name, type(obj).__name__))
    obj._expressions.append(OpSimple(func, identifiers))


def op_notify(obj, name, func, identifiers):
    """ The default Enaml operator function for `::` bindings.

    """
    member = obj.lookup_member(name)
    # XXX we need to think more about this.
    if not isinstance(member, (Event, DeclarativeProperty)):
        msg = "Cannot bind expression. '%s' is not an event or a declarative "
        msg += "property on a '%s' object."
        raise TypeError(msg % (name, type(obj).__name__))
    obj.observe(name, OpNotify(func, identifiers))


def op_update(obj, name, func, identifiers):
    """ The default Enaml operator function for `>>` bindings.

    """
    member = obj.lookup_member(name)
    if not isinstance(member, DeclarativeProperty):
        msg = "Cannot bind expression. '%s' is not a declarative property "
        msg += "on a '%s' object."
        raise TypeError(msg % (name, type(obj).__name__))
    obj.observe(name, OpUpdate(func, identifiers))


def op_subscribe(obj, name, func, identifiers):
    """ The default Enaml operator function for `<<` bindings.

    """
    member = obj.lookup_member(name)
    if not isinstance(member, DeclarativeProperty):
        msg = "Cannot bind expression. '%s' is not a declarative property "
        msg += "on a '%s' object."
        raise TypeError(msg % (name, type(obj).__name__))
    obj._expressions.append(OpSubscribe(func, identifiers))


def op_delegate(obj, name, func, identifiers):
    """ The default Enaml operator function for `:=` bindings.

    """
    member = obj.lookup_member(name)
    if not isinstance(member, DeclarativeProperty):
        msg = "Cannot bind expression. '%s' is not a declarative property "
        msg += "on a '%s' object."
        raise TypeError(msg % (name, type(obj).__name__))
    expr = OpDelegate(func, identifiers)
    obj._expressions.append(expr)
    obj.observe(name, expr)


OPERATORS = {
    '__operator_Equal__': op_simple,
    '__operator_LessLess__': op_subscribe,
    '__operator_ColonEqual__': op_delegate,
    '__operator_ColonColon__': op_notify,
    '__operator_GreaterGreater__': op_update,
}

