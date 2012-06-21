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
        self.set_icon(init_attrs.get('icon'))
        self.set_maximum_size(init_attrs.get('maximum_size'))
        self.set_minimum_size(init_attrs.get('minimum_size'))
        self.set_initial_size(init_attrs.get('initial_size'))

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_maximize(self, ctxt):
        """ Message handler for maximize

        """
        self.maximize()

    def receive_minimize(self, ctxt):
        """ Message handler for minimize

        """
        self.minimize()

    def receive_restore(self, ctxt):
        """ Message handler for restore

        """
        self.restore()

    def receive_set_icon(self, ctxt):
        """ Message handler for set_icon

        """
        pass

    def receive_set_initial_size(self, ctxt):
        """ Message handler for set_initial_size

        """
        size = ctxt.get('value')
        if size is not None:
            self.set_initial_size(size)

    def receive_set_maximum_size(self, ctxt):
        """ Message handler for set_maximum_size

        """
        size = ctxt.get('value')
        if size is not None:
            self.set_maximum_size(size)

    def receive_set_minimum_size(self, ctxt):
        """ Message handler for set_minimum_size

        """
        size = ctxt.get('value')
        if size is not None:
            self.set_minimum_size(size)

    def receive_set_title(self, ctxt):
        """ Message handler for set_title

        """
        title = ctxt.get('value')
        if title is not None:
            self.set_title(title)

    def receive_show(self, ctxt):
        """ Message handler for show

        """
        self.show()
    
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
        """ Set the initial window size

        """
        self.widget.resize(QSize(*size))

    def set_maximum_size(self, size):
        """ Set the maximum size of the window

        """
        self.widget.setMaximumSize(QSize(*size))

    def set_minimum_size(self, size):
        """ Set the minimum size of the window

        """
        self.widget.setMinimumSize(QSize(*size))
    
    def set_title(self, title):
        """ Set the title of the window

        """
        self.widget.setWindowTitle(title)

    def show(self):
        """ Show the window

        """
        self.widget.show()
