#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Instance

from .component import Component, IComponentImpl


class IControlImpl(IComponentImpl):
    pass


class Control(Component):
    """ The base class of all concrete widgets in Enaml.

    Attributes
    ----------

    error : Bool
        A read only property which indicates whether an exception was raised
        through user interaction or setting a value trait on the Control.
    
    exception : Instance(Exception)
        A read only property which holds the exceptions raised if we are in an
        error state.
    """
    error = Bool

    exception = Instance(Exception)

    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IControlImpl)


Control.protect('error', 'exception')
