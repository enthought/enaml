#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_container import QtContainer

from ..window import AbstractTkWindow


class QtWindow(QtContainer, AbstractTkWindow):
    """ A Qt implementation of a Window.

    QtWindow uses a QFrame to create a simple top level window which
    contains other child widgets and layouts.

    """
    _initializing = False

    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def initialize(self):
        """ Intializes the attributes on the QWindow.

        """
        self._initializing = True
        try:
            super(QtWindow, self).initialize()
            self.set_title(self.shell_obj.title)
        finally:
            self._initializing = False

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_title_changed(self, title):
        """ The change handler for the 'title' attribute. Not meant for
        public consumption.

        """
        self.set_title(title)

    def set_title(self, title):
        """ Sets the title of the QFrame. Not meant for public
        consumption.

        """
        if self.widget:
            self.widget.setWindowTitle(title)

    def set_visible(self, visible):
        """ Show or hide the window.

        If we are initializing, don't show yet.
        """
        if not self._initializing:
            if visible:
                self.widget.show()
                self.widget.raise_()
            else:
                self.widget.hide()
