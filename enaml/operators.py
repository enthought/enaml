#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .expressions import (SimpleExpression, SubscriptionExpression, 
                          DelegatingExpression, NotifyingExpression)


def op_simple(cmpnt, attr, ast, code, identifiers, f_globals, toolkit):
    expr = SimpleExpression(cmpnt, attr, code, identifiers, f_globals, toolkit)
    cmpnt.bind_expression(attr, expr)


def op_subscribe(cmpnt, attr, ast, code, identifiers, f_globals, toolkit):
    expr = SubscriptionExpression(cmpnt, attr, code, identifiers, f_globals, toolkit)
    cmpnt.bind_expression(attr, expr)


def op_delegate(cmpnt, attr, ast, code, identifiers, f_globals, toolkit):
    expr = DelegatingExpression(cmpnt, attr, code, identifiers, f_globals, toolkit)
    cmpnt.bind_expression(attr, expr)


def op_notify(cmpnt, attr, ast, code, identifiers, f_globals, toolkit):
    NotifyingExpression(cmpnt, attr, code, identifiers, f_globals, toolkit)


#: The builtin Enaml expression operators
#: 
#:     '=' : A simple assignment expression
#:    '<<' : A dynamically updating expression
#:    ':=' : A dynamically delegating expression
#:    '>>' : A dynamically notifying expression
#:
OPERATORS = {
    '__operator_Equal__': op_simple,
    '__operator_LessLess__': op_subscribe,
    '__operator_ColonEqual__': op_delegate,
    '__operator_GreaterGreater__': op_notify,
}

