#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import (
    Unicode, Property, Bool, cached_property
    )

from .widget import Widget
from .permanent_status_widgets import PermanentStatusWidgets
from .transient_status_widgets import TransientStatusWidgets

class StatusBar(Widget):
    """ A widget used as a status bar in a MainWindow.

    """

    #: Should the size grip in the bottom right corner be shown
    grip_enabled = Bool(True)

    #: Permanent and transient children
    widgets = Property(depends_on='children')

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dict for the DockPane.

        """
        snap = super(StatusBar, self).snapshot()
        snap['grip_enabled'] = self.grip_enabled
        return snap

    def bind(self):
        """ Bind the change handlers for the StatusBar.

        """
        super(StatusBar, self).bind()
        attrs = (
            'grip_enabled',
        )
        self.publish_attributes(*attrs)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_widgets(self):
        """ The getter for the 'widgets' property.

        Returns
        -------
        result : tuple
            The tuple of Widgets defined as children of this StatusBar.

        """
        isinst = isinstance
        allowed = (PermanentStatusWidgets, TransientStatusWidgets)
        widgets = (child for child in self.children if isinst(child, allowed))
        return tuple(widgets)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def show_message(self, message, timeout=0):
        """ Send the 'show_message' action to the client widget.

        """
        content = {'message': message, 'timeout': timeout}
        self.send_action('show_message', content)

    def clear_message(self):
        """ Send the 'clear_message' action to the client widget.

        """
        self.send_action('clear_message', {})

