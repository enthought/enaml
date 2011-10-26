#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Instance, List

from .base_component import BaseComponent
from .component import Component, AbstractTkComponent


class AbstractTkControl(AbstractTkComponent):
    pass


class Control(Component):
    """ The base class of all leaf widgets in Enaml. Controls cannot
    have children and attempts to add children to a control will
    raise an exception.

    """
    #: A boolean which indicates whether an exception was raised through 
    #: user interaction or setting a value trait on the Control.
    error = Bool

    #: The exception object that was raised to create the error state.
    exception = Instance(Exception)

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkControl)

    #: Overridden parent class trait
    children = List(BaseComponent, maxlen=0)

