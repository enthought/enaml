#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtCore, QtGui
from .qt_component import QtComponent

from ..window import AbstractTkWindow

from ...enums import Modality


class QtWindow(QtComponent, AbstractTkWindow):
    """ A Qt implementation of a Window.

    QtWindow uses a QFrame to create a simple top level window which
    contains other child widgets and layouts.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying QWindow control.

        """
        self.widget = QtGui.QFrame(self.parent_widget())
    
    def initialize(self):
        """ Intializes the attributes on the QWindow.

        """
        super(QtWindow, self).initialize()
        shell = self.shell_obj
        self.set_title(shell.title)
        self.set_modality(shell.modality)

        # XXX not sure the right place for this
        layout = QtGui.QVBoxLayout()
        for child in self.child_widgets():
            if isinstance(child, QtGui.QLayout):
                layout.addLayout(child, 1)
            else:
                layout.addWidget(child, 1)
        self.widget.setLayout(layout)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def show(self):
        """ Displays the window to the screen.
        
        """
        if self.widget:
            self.widget.show()

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
        """ Sets the modality of the QMainWindow. Not meant for public
        consumption.

        """
        if self.widget:
            if modality == Modality.APPLICATION_MODAL:
                self.widget.setWindowModality(QtCore.Qt.ApplicationModal)
            elif modality == Modality.WINDOW_MODAL:
                self.widget.setWindowModality(QtCore.Qt.WindowModal)
            else:
                self.widget.setWindowModality(QtCore.Qt.NonModal)

