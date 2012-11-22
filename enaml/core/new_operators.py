#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .new_expressions import (
    SimpleExpression, NotificationExpression, SubscriptionExpression,
    UpdateExpression, DelegationExpression
)


def op_simple(cmpnt, attr, func, identifiers):
    """ The default Enaml operator for '=' expressions. It binds an
    instance of SimpleExpression to the component.

    """
    expr = SimpleExpression(func, identifiers)
    cmpnt._bind_expression(attr, expr)


def op_notify(cmpnt, attr, func, identifiers):
    """ The default Enaml operator for '::' expressions. It binds an
    instance of NotificationExpression to the component.

    """
    expr = NotificationExpression(func, identifiers)
    cmpnt._bind_listener(attr, expr)


def op_update(cmpnt, attr, func, identifiers):
    """ The default Enaml operator for '>>' expressions. It binds an
    instance of UpdateExpression to the component.

    """
    expr = UpdateExpression(func, identifiers)
    cmpnt._bind_listener(attr, expr)


def op_subscribe(cmpnt, attr, func, identifiers):
    """ The default Enaml operator for '<<' expressions. It binds an
    instance of SubscriptionExpression to the component using monitors
    which understand traits attribute access via dotted notation and
    the builtin getattr function.

    """
    expr = SubscriptionExpression(func, identifiers)
    cmpnt._bind_expression(attr, expr)


def op_delegate(cmpnt, attr, func, identifiers):
    """ The default Enaml operator for ':=' expressions. It binds an
    instance of DelegationExpression to the component using monitors
    which understand traits attribute access via dotted notation and
    the builtin getattr function, and inverters which understand the
    dotted attribute access, implicit attribute access, and also the
    builtin getattr function.

    """
    expr = DelegationExpression(func, identifiers)
    cmpnt._bind_expression(attr, expr)
    cmpnt._bind_listener(attr, expr)


OPERATORS = {
    '__operator_Equal__': op_simple,
    '__operator_LessLess__': op_subscribe,
    '__operator_ColonEqual__': op_delegate,
    '__operator_ColonColon__': op_notify,
    '__operator_GreaterGreater__': op_update,
}

