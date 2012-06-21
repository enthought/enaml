#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .base_component import BaseComponent
from .operator_context import OperatorContext


class EnamlDef(object):
    """ An EnamlDef is an object created by the keyword 'enamldef'.

    An EnamlDef instance is callable from Python using standard Python 
    calling conventions. It also provides the __enaml_call__ protocol
    so that it can be used as a child component in Enaml trees.

    """
    def __init__(self, func):
        self.__func__ = func
        self.__doc__ = func.__doc__
        self.__name__ = func.__name__
        self.__module__ = func.__module__

    def __repr__(self):
        return '%s.%s' % (self.__module__, self.__name__)

    def __instancecheck__(self, instance):
        """ Overrides isinstance(obj, cls) for instances of this class.
        This allows one check if a component instance was created by a 
        enamldef using standard Python idioms.

        """
        if isinstance(instance, BaseComponent):
            return self in instance._bases
        return False

    def __call__(self, **kwargs):
        """ Invokes the underlying Enaml building function and applies 
        the given keyword arguments as attributes to the result. 

        This a convienence method which makes the enamldef callable
        from Python code. This method will not be called by the Enaml
        runtime.

        Paramters
        ---------
        **kwargs
            The initial attribute values to apply to the component after 
            it as been instantiated.

        Returns
        -------
        result : BaseComponent
            The BaseComponent instance that was created.

        """
        component = self.__enaml_call__()
        component.trait_set(**kwargs)
        return component

    def __enaml_call__(self, identifiers=None, operators=None):
        """ Invokes the underlying Enaml building function, creating 
        the local identifiers scope if necessary and loading the 
        current operator context.

        Parameters
        ----------
        identifiers : dict or None, optional
            The dict of identifiers to use when binding expressions
            on the component. If None, a new dict will be created.

        operators : OperatorContext or None, optional
            The operator context to use when building the component.
            If None, the current operator context will be retrieved.

        Returns
        -------
        result : BaseComponent
            The BaseComponent instance that was created.

        """
        if identifiers is None:
            identifiers = {}
        if operators is None:
            operators = OperatorContext.active_context()
        component = self.__func__(identifiers, operators)
        component._bases.insert(0, self)
        return component

