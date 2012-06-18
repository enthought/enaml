#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod
from traits.api import Bool, Instance, Enum

from .constraints_widget import (
    ConstraintsWidget, AbstractTkConstraintsWidget,
)

from ..exceptions import ShellExceptionContext, ShellNotificationContext


class AbstractTkControl(AbstractTkConstraintsWidget):
    """ The abstract toolkit Control interface.

    """
    @abstractmethod
    def shell_show_focus_rect_changed(self, show):
        """ The change handler for the 'show_focus_rect' attribute.

        """
        raise NotImplementedError


class Control(ConstraintsWidget):
    """ The base class of all leaf widgets in Enaml.

    """
    #: A boolean which indicates whether an exception was raised through 
    #: user interaction or setting a value trait on the Control.
    error = Bool(False)

    #: The exception object that was raised to create the error state.
    exception = Instance(Exception)

    #: A flag indicating whether or not to draw a focus rectangle around
    #: a control. Support for this may not be implemented on all controls
    #: or on all platforms or all backends.
    show_focus_rect = Enum('default', True, False)

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

