#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .expressions import (SimpleExpression, UpdatingExpression, 
                          DelegatingExpression, NotifyingExpression)
from .widgets.setup_hooks import ExpressionSetupHook


def op_Equal(component, attr_name, py_ast, code, globals_f, locals_f):
    expression = SimpleExpression(component, attr_name, py_ast, code,
                                  globals_f, locals_f)
    hook = ExpressionSetupHook(attr_name, expression)
    component.setup_hooks.append(hook)


def op_LessLess(component, attr_name, py_ast, code, globals_f, locals_f):
    expression = UpdatingExpression(component, attr_name, py_ast, code,
                                    globals_f, locals_f)
    hook = ExpressionSetupHook(attr_name, expression)
    component.setup_hooks.append(hook)


def op_ColonEqual(component, attr_name, py_ast, code, globals_f, locals_f):
    expression = DelegatingExpression(component, attr_name, py_ast, code,
                                      globals_f, locals_f)
    hook = ExpressionSetupHook(attr_name, expression)
    component.setup_hooks.append(hook)


def op_GreaterGreater(component, attr_name, py_ast, code, globals_f, locals_f):
    expression = NotifyingExpression(component, attr_name, py_ast, code,
                                     globals_f, locals_f)
    hook = ExpressionSetupHook(attr_name, expression, eval_default=False)
    component.setup_hooks.append(hook)


OPERATORS = {
    '__operator_Equal__': op_Equal,
    '__operator_LessLess__': op_LessLess,
    '__operator_ColonEqual__': op_ColonEqual,
    '__operator_GreaterGreater__': op_GreaterGreater,
}

