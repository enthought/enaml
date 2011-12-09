#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .expressions import (SimpleExpression, UpdatingExpression, 
                          DelegatingExpression, NotifyingExpression)
from .widgets.setup_hooks import ExpressionSetupHook


def operator_factory(expression_class, eval_default=True):
    """ A factory function which creates an Enaml operator function 
    for an implementor of enaml.expresssions.AbstractExpression. The
    created operator will setup an appropriate SetupHook for the 
    component so that the expression is properly bound at run time.

    """
    def operator(component, attr, ast, code, f_globals, toolkit, f_locals):
        """ The default Enaml expression operator. It uses an implementor
        of AbstractExpression to bind a python expression to a component
        at run time.

        """
        expression = expression_class(component, attr, ast, code,
                                      f_globals, toolkit, f_locals)
        hook = ExpressionSetupHook(attr, expression, eval_default)
        component.setup_hooks.append(hook)
    return operator


#: The builtin Enaml expression operators
#: 
#:     '=' : A simple assignment expression
#:    '<<' : A dynamically updating expression
#:    ':=' : A dynamically delegating expression
#:    '>>' : A dynamically notifying expression
#:
OPERATORS = {
    '__operator_Equal__': operator_factory(SimpleExpression),
    '__operator_LessLess__': operator_factory(UpdatingExpression),
    '__operator_ColonEqual__': operator_factory(DelegatingExpression),
    '__operator_GreaterGreater__': operator_factory(NotifyingExpression, False),
}

