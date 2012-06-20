#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Instance, Enum, on_trait_change

from .constraints_widget import ConstraintsWidget

from ..exceptions import ShellExceptionContext, ShellNotificationContext


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

    @on_trait_change('error, show_focus_rect')
    def sync_object_state(self, name, new):
        """ Notify the client component of updates to the object state.

        """
        msg = 'set_' + name
        self.send(msg, {'value': new})

    def initial_attrs(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        super_attrs = super(Control, self).initial_attrs()
        attrs = {'error':self.error, 'show_focus_rect':self.show_focus_rect}
        attrs.update(super_attrs)
        return attrs
        
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

