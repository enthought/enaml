#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Instance

from .constraints_widget import (
    ConstraintsWidget, AbstractTkConstraintsWidget,
)

from ..exceptions import ShellExceptionContext, ShellNotificationContext


class AbstractTkControl(AbstractTkConstraintsWidget):
    """ The abstract toolkit Control interface.

    """
    pass


class Control(ConstraintsWidget):
    """ The base class of all leaf widgets in Enaml.

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

