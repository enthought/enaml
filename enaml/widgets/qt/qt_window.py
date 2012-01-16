#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_component import QtComponent

from ..window import AbstractTkWindow


class QtWindow(QtComponent, AbstractTkWindow):
    """ A Qt4 implementation of a Window. It serves as a base class for 
    QtMainWindow and QtDialog. It is not meant to be used directly.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Create the underlying Qt widget.

        """
        msg = 'A QtWindow is a base class and cannot be used directly'
        raise NotImplementedError(msg)

    def initialize(self):
        """ Intializes the attributes on the QWindow.

        """
        super(QtWindow, self).initialize()
        self.set_title(self.shell_obj.title)
        self.update_central_widget()

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_title_changed(self, title):
        """ The change handler for the 'title' attribute on the shell
        object.

        """
        self.set_title(title)
    
    def shell_central_widget_changed(self, central_widget):
        """ The change handler for the 'central_widget' attribute on 
        the shell object.

        """
        self.update_central_widget()
    
    #--------------------------------------------------------------------------
    # Widget Update Methods 
    #--------------------------------------------------------------------------
    def update_central_widget(self):
        """ Updates the central widget from the value on the shell 
        object. This method must be implemented by subclasses.

        """
        raise NotImplementedError

    def set_title(self, title):
        """ Sets the title of the underlying widget.

        """
        self.widget.setWindowTitle(title)

