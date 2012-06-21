#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from PySide.QtGui import QWidget
from PySide.QtCore import QSize

from qt_client_widget import QtClientWidget


class QtWindow(QtClientWidget):
    """ A Qt implementation of a window

    """
    def create(self, parent):
        """ Create the underlying widget

        """
        self.widget = QWidget(parent)
        self.widget.show()

    def initialize(self, init_attrs):
        """ Initialize the widget's attributes

        """
        self.set_title(init_attrs.get('title', ''))

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_maximize(self, ctxt):
        self.maximize()

    def receive_minimize(self, ctxt):
        self.minimize()

    def receive_restore(self, ctxt):
        self.restore()

    def receive_set_icon(self, ctxt):
        pass

    def receive_set_initial_size(self, ctxt):
        pass

    def receive_set_initial_size_default(self, ctxt):
        pass

    def receive_set_maximum_size(self, ctxt):
        size = ctxt.get('value')
        if size is not None:
            self.set_maximum_size(size)

    def receive_set_maximum_size_default(self, ctxt):
        pass

    def receive_set_minimum_size(self, ctxt):
        size = ctxt.get('value')
    
    def receive_set_title(self, ctxt):
        title = ctxt.get('value')
        if title is not None:
            self.set_title(title)
    
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def maximize(self):
        """ Maximize the window

        """
        self.widget.showMaximized()

    def minimize(self):
        """ Minimize the window

        """
        self.widget.showMinimized()

    def restore(self):
        """ Restore the window after a minimize or maximize

        """
        self.widget.showNormal()

    def set_icon(self, icon):
        """ Set the window icon

        """
        pass

    def set_initial_size(self, size):
        """ Set the initial size of the window

        """
        pass

    def set_initial_size_default(self, size):
        """ Set the default initial size of the window

        """
        pass

    def set_maximum_size(self, size):
        """ Set the maximum size of the window

        """
        self.widget.setMaximumSize(QSize(*size))

    def set_maximum_size_default(self, size):
        """ Set the default maximum size of the window

        """
        pass

    def set_minimum_size(self, size):
        """ Set the minimum size of the window

        """
        self.widget.setMinimumSize(QSize(*size))

    def set_minimum_size_default(self, size):
        """ Set the default minimum size of the window

        """
        pass
    
    def set_title(self, title):
        """ Set the title of the window

        """
        self.widget.setWindowTitle(title)

    def show(self):
        """ Show the window

        """
        self.widget.show()
