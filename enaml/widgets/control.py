#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Instance, List

from .base_component import BaseComponent
from .component import Component, AbstractTkComponent
from ..exceptions import ShellExceptionContext, ShellNotificationContext


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

    def capture_exceptions(self):
        """ Return a ShellExceptionContext that will capture error state automatically.
        
        """
        return ShellExceptionContext(self)
    
    def capture_notification_exceptions(self, handler=None, reraise_exceptions=True,
            main=False, locked=False):
        """ Return a ShellNotificationContext that will set error state automatically,
        including TraitErrors in listeners.
        
        """
        return ShellNotificationContext(self, handler, reraise_exceptions, main,
            locked)

