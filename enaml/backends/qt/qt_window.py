#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_widget_component import QtWidgetComponent

from ...components.window import AbstractTkWindow


class QtWindow(QtWidgetComponent, AbstractTkWindow):
    """ A Qt4 implementation of Window.
     
    """
    def create(self, parent):
        """ Creates the underlying Qt widget.

        """
        msg = 'A QtWindow is a base class and cannot be used directly'
        raise NotImplementedError(msg)

    def initialize(self):
        """ Intializes the attributes on the underlying Qt widget.

        """
        super(QtWindow, self).initialize()
        self.set_title(self.shell_obj.title)
        self.update_central_widget()

    def maximize(self):
        """ Maximizes the window to fill the screen.

        """
        self.widget.showMaximized()
            
    def minimize(self):
        """ Minimizes the window to the task bar.

        """
        self.widget.showMinimized()
            
    def normalize(self):
        """ Restores the window after it has been minimized or maximized.

        """
        self.widget.showNormal()

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
    
    def update_central_widget(self):
        """ Updates the central widget from the value on the shell 
        object. This method must be implemented by subclasses.

        """
        raise NotImplementedError

    def set_title(self, title):
        """ Sets the title of the underlying widget.

        """
        self.widget.setWindowTitle(title)

