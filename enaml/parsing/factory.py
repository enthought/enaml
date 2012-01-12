#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

from ..expressions import ExpressionLocals
from ..toolkit import Toolkit
from ..widgets.base_component import BaseComponent


class EnamlFactory(object):
    """ An abstract base class that defines the interface required
    to instantiate and Enaml declarative component. This class handles
    registering a factory as a virtual base class of the component
    instance and makes sure that a component is associated with a
    proper toolkit.

    """
    __metaclass__ = ABCMeta

    def __call__(self, **kwargs):
        """ Invokes the underlying Enaml build function and applies the
        given keyword arguments as attributes to the result. 

        This a convienence method of the factory which makes is callable
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

    def __enaml_call__(self, f_locals=None, toolkit=None):
        """ Invokes the underlying Enaml build function, creating the 
        locals and toolkit if necessary.

        Parameters
        ----------
        f_locals : ExpressionLocals or None, optional
            The ExpressionLocals object to use when binding expressions
            on the component. If None, a new instance will be created.
        
        toolkit : Toolkit or None, optional
            The Toolkit to use when building the object tree. If None,
            the currently active toolkit will be used.

        Returns
        -------
        result : BaseComponent
            The BaseComponent instance that was created.

        """
        if f_locals is None:
            f_locals = ExpressionLocals()
        if toolkit is None:
            toolkit = Toolkit.active_toolkit()
        component = self.__enaml_build__(f_locals, toolkit)
        component.toolkit = toolkit
        component._bases.insert(0, self)
        return component

    def __instancecheck__(self, instance):
        """ Overrides isinstance(obj, ctor) for instances of this factory
        class. This allows one check if a component instance was created 
        by a given factory instance using standard Python idioms.

        """
        if isinstance(instance, BaseComponent):
            return self in instance._bases
        return False

    @abstractmethod
    def __enaml_build__(self, f_locals, toolkit):
        """ An abstract method which must be implemented by subclasses
        to build an return an instance of BaseComponent.

        Parameters
        ----------
        f_locals : ExpressionLocals
            The ExpressionLocals object to use when binding expressions
            on the component.
        
        toolkit : Toolkit
            The Toolkit to use when building the object tree.

        Returns
        -------
        result : BaseComponent
            The BaseComponent instance that was created.

        """
        raise NotImplementedError

