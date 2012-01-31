#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .expressions import (
    SimpleExpression, NotificationExpression, SubscriptionExpression, 
    DelegationExpression, UpdateExpression,
)
from .inverters import (
    GenericAttributeInverter, GetattrInverter, ImplicitAttrInverter,
)
from .monitors import TraitAttributeMonitor, TraitGetattrMonitor


#------------------------------------------------------------------------------
# Builtin Enaml Operators
#------------------------------------------------------------------------------
#: Operators are passed a number of arguments from the Enaml runtime 
#: engine in order to perform their work. The arguments are, in order:
#:
#:      cmpnt : BaseComponent
#:          The BaseComponent instance which owns the expression which
#:          is being bound.
#:
#:      attr : string
#:          The name of the attribute on the component which is being
#:          bound.
#:
#:      code : types.CodeType
#:          The compiled code object for the Python expression given
#:          given by the user. It is compiled with mode='eval'.
#:
#:      identifiers : dict
#:          The dictionary of identifiers available to the expression.
#:          This dictionary is shared amongs all expressions within
#:          a given lexical scope. It should therefore not be modified
#:          or copied since identifiers may continue to be added to 
#:          this dict as runtime execution continues.
#:
#:      f_globals : dict
#:          The dictionary of globals available to the  expression. 
#:          The same rules about sharing and copying that apply to
#:          the identifiers dict, apply here as well.
#:
#:      toolkit : Toolkit
#:          The toolkit instance that is in scope for the expression.
#:          The same rules about sharing and copying that apply to
#:          the identifiers dict, apply here as well.
#:
#: Operators may do whatever they please with the information provided
#: to them. The default operators in Enaml use this information to 
#: create and bind Enaml expression objects to the component. However,
#: this is not a requirement and developers who are extending enaml
#: are free to get creative with the operators.


def op_simple(cmpnt, attr, code, identifiers, f_globals, toolkit):
    """ The default Enaml operator for '=' expressions. It binds an
    instance of SimpleExpression to the component.

    """
    expr = SimpleExpression(cmpnt, attr, code, identifiers, f_globals, toolkit)
    cmpnt.bind_expression(attr, expr)


def op_notify(cmpnt, attr, code, identifiers, f_globals, toolkit):
    """ The default Enaml operator for '::' expressions. It binds an
    instance of NotificationExpression to the component.

    """
    expr = NotificationExpression(cmpnt, attr, code, identifiers, f_globals, toolkit)
    cmpnt.bind_expression(attr, expr, notify_only=True)


def op_update(cmpnt, attr, code, identifiers, f_globals, toolkit):
    """ The default Enaml operator for '>>' expressions. It binds an
    instance of UpdateExpression to the component.

    """
    inverters = [GenericAttributeInverter, GetattrInverter, ImplicitAttrInverter]
    expr = UpdateExpression(inverters, cmpnt, attr, code, identifiers, f_globals, toolkit)
    cmpnt.bind_expression(attr, expr, notify_only=True)


def op_subscribe(cmpnt, attr, code, identifiers, f_globals, toolkit):
    """ The default Enaml operator for '<<' expressions. It binds an
    instance of SubscriptionExpression to the component using monitors
    which understand traits attribute access via dotted notation and
    the builtin getattr function.

    """
    monitors = [TraitAttributeMonitor, TraitGetattrMonitor]
    expr = SubscriptionExpression(monitors, cmpnt, attr, code, identifiers, f_globals, toolkit)
    cmpnt.bind_expression(attr, expr)


def op_delegate(cmpnt, attr, code, identifiers, f_globals, toolkit):
    """ The default Enaml operator for ':=' expressions. It binds an
    instance of DelegationExpression to the component using monitors
    which understand traits attribute access via dotted notation and
    the builtin getattr function, and inverters which understand the
    dotted attribute access, implicit attribute access, and also the
    builtin getattr function.

    """
    inverters = [GenericAttributeInverter, GetattrInverter, ImplicitAttrInverter]
    monitors = [TraitAttributeMonitor, TraitGetattrMonitor]
    expr = DelegationExpression(inverters, monitors, cmpnt, attr, code, identifiers, f_globals, toolkit)
    cmpnt.bind_expression(attr, expr)


OPERATORS = {
    '__operator_Equal__': op_simple,
    '__operator_LessLess__': op_subscribe,
    '__operator_ColonEqual__': op_delegate,
    '__operator_ColonColon__': op_notify,
    '__operator_GreaterGreater__': op_update,
}

