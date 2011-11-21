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
        """ The change handler for the 'title' attribute.

        """
        self.set_title(title)
    
    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def set_title(self, title):
        """ Sets the title of the QFrame.

        """
        self.widget.setWindowTitle(title)

    def set_visible(self, visible):
        """ Overridden from the parent class to raise the window to
        the front if it should be shown.

        """
        # Don't show the window if we're not initializing.
        if not self._initializing:
            if visible:
                self.widget.setVisible(True)
                self.widget.raise_()
            else:
                self.widget.setVisible(False)

