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
from .expressions import (
    SimpleExpression, NotificationExpression, SubscriptionExpression,
    UpdateExpression, DelegationExpression
)


def op_simple(obj, name, func, identifiers):
    """ The default Enaml operator for `=` expressions.

    This operator binds an instance of SimpleExpression to the attribute
    on the object. The function takes no arguments and returns the value
    of the expression. It is patched for dynamic scoping and it should be
    invoked with `funchelper.call_func(...)`.

    """
    expr = SimpleExpression(func, identifiers)
    obj.bind_expression(name, expr)


def op_notify(obj, name, func, identifiers):
    """ The default Enaml operator for `::` expressions.

    This operator binds an instance of NotificationExpression to the
    attribute on the object. The function takes no arguments and will
    return None. It is patched for dynamic scoping and it should be
    invoked with `funchelper.call_func(...)`.

    """
    expr = NotificationExpression(func, identifiers)
    obj.bind_listener(name, expr)


def op_update(obj, name, func, identifiers):
    """ The default Enaml operator for `>>` expressions.

    This operator binds an instance of UpdateExpression to the attribute
    on the object. The function takes two arguments: a code inverter and
    the new value of the attribute, and returns None. It is patched for
    dynamic scoping and code inversion and it should be invoked with
    `funchelper.call_func(...)`.

    """
    expr = UpdateExpression(func, identifiers)
    obj.bind_listener(name, expr)


def op_subscribe(obj, name, func, identifiers):
    """ The default Enaml operator for `<<` expressions.

    This operator binds an instance of SubscriptionExpression to the
    attribute on the object. The function takes one argument: a code
    tracer, and returns the value of the expression. It is patched for
    dynamic scoping and code tracing and it should be invoked with
    `funchelper.call_func(...)`.

    """
    expr = SubscriptionExpression(func, identifiers)
    obj.bind_expression(name, expr)


def op_delegate(obj, name, func, identifiers):
    """ The default Enaml operator for `:=` expressions.

    This operator binds an instance of DelegationExpression to the
    attribute on the object. The semantics of the function are the same
    as that of `op_subscribe`. The function also has an attribute named
    `_update` which is a function implementing `op_update` semantics.
    Both functions should be invoked with `funchelper.call_func(...)`.
    In this fashion, `op_delegate` is the combination of `op_subscribe`
    and `op_update`.

    """
    expr = DelegationExpression(func, identifiers)
    obj.bind_expression(name, expr)
    obj.bind_listener(name, expr)


OPERATORS = {
    '__operator_Equal__': op_simple,
    '__operator_LessLess__': op_subscribe,
    '__operator_ColonEqual__': op_delegate,
    '__operator_ColonColon__': op_notify,
    '__operator_GreaterGreater__': op_update,
}

