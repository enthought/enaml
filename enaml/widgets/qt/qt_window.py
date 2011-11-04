#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtCore, QtGui
from .qt_container import QtContainer

from ..window import AbstractTkWindow


class QtWindow(QtContainer, AbstractTkWindow):
    """ A Qt implementation of a Window.

    QtWindow uses a QFrame to create a simple top level window which
    contains other child widgets and layouts.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------

    def initialize(self):
        """ Intializes the attributes on the QWindow.

        """
        super(QtWindow, self).initialize()
        shell = self.shell_obj
        self.set_title(shell.title)
        self.set_modality(shell.modality)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------

    def pos(self):
        """ Returns the position of the internal toolkit widget as an 
        (x, y) tuple of integers. The coordinates should be relative to
        the origin of the widget's parent.

        """
        # Use the geometry member to avoid window dressing.
        widget = self.widget
        geom = widget.geometry()
        return (geom.x(), geom.y())

    def show(self):
        """ Displays the window to the screen.

        """
        if self.widget:
            self.widget.show()
            self.widget.raise_()

    def hide(self):
        """ Hide the window from the screen.

        """
        if self.widget:
            self.widget.hide()

    def shell_title_changed(self, title):
        """ The change handler for the 'title' attribute. Not meant for
        public consumption.

        """
        self.set_title(title)

    def shell_modality_changed(self, modality):
        """ The change handler for the 'modality' attribute. Not meant
        for public consumption.

        """
        self.set_modality(modality)

    def set_title(self, title):
        """ Sets the title of the QFrame. Not meant for public
        consumption.

        """
        if self.widget:
            self.widget.setWindowTitle(title)

    def set_modality(self, modality):
        """ Sets the modality of the QMainWindow.

        """
        if self.widget:
            if modality == 'application_modal':
                self.widget.setWindowModality(QtCore.Qt.ApplicationModal)
            elif modality == 'window_modal':
                self.widget.setWindowModality(QtCore.Qt.WindowModal)
            else:
                self.widget.setWindowModality(QtCore.Qt.NonModal)


