#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Instance

from .layout_component import LayoutComponent, AbstractTkLayoutComponent

from ..exceptions import ShellExceptionContext, ShellNotificationContext


class AbstractTkControl(AbstractTkLayoutComponent):
    pass


class Control(LayoutComponent):
    """ The base class of all leaf widgets in Enaml. Controls cannot
    have subcomponents and attempt to add a subcomponent to a control 
    will raise an exception.

    """
    #: A boolean which indicates whether an exception was raised through 
    #: user interaction or setting a value trait on the Control.
    error = Bool(False)

    #: The exception object that was raised to create the error state.
    exception = Instance(Exception)

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkControl)

    def capture_exceptions(self):
        """ Return a ShellExceptionContext that will capture error state 
        automatically.
        
        """
        return ShellExceptionContext(self)
    
    def capture_notification_exceptions(
        self, handler=None, reraise_exceptions=True, main=False, locked=False):
        """ Return a ShellNotificationContext that will set error state 
        automatically, including TraitErrors in listeners.
        
        """
        res = ShellNotificationContext(
            self, handler, reraise_exceptions, main, locked,
        )
        return res

