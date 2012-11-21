#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import types
from .code_tracing import transform_code
from .new_expressions import (
    SimpleExpression, NotificationExpression, SubscriptionExpression,
    UpdateExpression,
)


_cached_code = {}


def op_simple(cmpnt, attr, code, identifiers, f_globals, operators):
    """ The default Enaml operator for '=' expressions. It binds an
    instance of SimpleExpression to the component.

    """
    if code in _cached_code:
        func = _cached_code[code]
    else:
        c = transform_code(code, False)
        func = _cached_code[code] = types.FunctionType(c, f_globals)
    expr = SimpleExpression(func, identifiers)
    cmpnt._bind_expression(attr, expr)


def op_notify(cmpnt, attr, code, identifiers, f_globals, operators):
    """ The default Enaml operator for '::' expressions. It binds an
    instance of NotificationExpression to the component.

    """
    if code in _cached_code:
        func = _cached_code[code]
    else:
        c = transform_code(code, False)
        func = _cached_code[code] = types.FunctionType(c, f_globals)
    expr = NotificationExpression(func, identifiers)
    cmpnt._bind_listener(attr, expr)


def op_update(cmpnt, attr, code, identifiers, f_globals, operators):
    """ The default Enaml operator for '>>' expressions. It binds an
    instance of UpdateExpression to the component.

    """
    return


def op_subscribe(cmpnt, attr, code, identifiers, f_globals, operators):
    """ The default Enaml operator for '<<' expressions. It binds an
    instance of SubscriptionExpression to the component using monitors
    which understand traits attribute access via dotted notation and
    the builtin getattr function.

    """
    if code in _cached_code:
        func = _cached_code[code]
    else:
        c = transform_code(code, True)
        func = _cached_code[code] = types.FunctionType(c, f_globals)
    expr = SubscriptionExpression(func, identifiers)
    cmpnt._bind_expression(attr, expr)


def op_delegate(cmpnt, attr, code, identifiers, f_globals, operators):
    """ The default Enaml operator for ':=' expressions. It binds an
    instance of DelegationExpression to the component using monitors
    which understand traits attribute access via dotted notation and
    the builtin getattr function, and inverters which understand the
    dotted attribute access, implicit attribute access, and also the
    builtin getattr function.

    """
    return


OPERATORS = {
    '__operator_Equal__': op_simple,
    '__operator_LessLess__': op_subscribe,
    '__operator_ColonEqual__': op_delegate,
    '__operator_ColonColon__': op_notify,
    '__operator_GreaterGreater__': op_update,
}

