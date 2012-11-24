#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .new_expressions import (
    SimpleExpression, NotificationExpression, SubscriptionExpression,
    UpdateExpression, DelegationExpression
)


def op_simple(obj, name, func, identifiers):
    """ The default Enaml operator for `=` expressions.

    It binds an instance of SimpleExpression to the object.

    """
    expr = SimpleExpression(func, identifiers)
    obj.bind_expression(name, expr)


def op_notify(obj, name, func, identifiers):
    """ The default Enaml operator for `::` expressions.

    It binds an instance of NotificationExpression to the object.

    """
    expr = NotificationExpression(func, identifiers)
    obj.bind_listener(name, expr)


def op_update(obj, name, func, identifiers):
    """ The default Enaml operator for `>>` expressions.

    It binds an instance of UpdateExpression to the object.

    """
    expr = UpdateExpression(func, identifiers)
    obj.bind_listener(name, expr)


def op_subscribe(obj, name, func, identifiers):
    """ The default Enaml operator for `<<` expressions.

    It binds an instance of SubscriptionExpression to the object.

    """
    expr = SubscriptionExpression(func, identifiers)
    obj.bind_expression(name, expr)


def op_delegate(obj, name, func, identifiers):
    """ The default Enaml operator for `:=` expressions.

    It binds an instance of DelegationExpression to the object.

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

