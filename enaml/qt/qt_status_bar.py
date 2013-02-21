#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import sys

from .qt.QtGui import QMainWindow, QStatusBar
from .qt_widget import QtWidget
from .qt_permanent_status_widgets import QtPermanentStatusWidgets
from .qt_transient_status_widgets import QtTransientStatusWidgets

class QtStatusBar(QtWidget):
    """ A Qt implementation of an Enaml StatusBar.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying status bar widget.

        """
        return QStatusBar(parent)

    def create(self, tree):
        """ Create and initialize the underlying status bar control

        """
        super(QtStatusBar, self).create(tree)
        self.set_grip_enabled(tree['grip_enabled'])

    def init_layout(self):
        """ Initialize the layout for the underlying status bar control.

        """
        super(QtStatusBar, self).init_layout()
        widget = self.widget()
        for child in self.children():
            if isinstance(child, QtPermanentStatusWidgets):
                for subchild in child.children():
                    widget.addPermanentWidget(subchild.widget())
            if isinstance(child, QtTransientStatusWidgets):
                for subchild in child.children():
                    widget.addWidget(subchild.widget())

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """ Handle the child removed event for a QtStatusBar.

        """
        if isinstance(child, (QtPermanentStatusWidgets, QtTransientStatusWidgets)):
            for subchild in child.children():
                self.widget().removeWidget(subchild.widget())

    def child_added(self, child):
        """ Handle the child added event for a QtStatusBar.

        """
        if isinstance(child, QtPermanentStatusWidgets):
            for subchild in child.children():
                widget.addPermanentWidget(subchild.widget())
        elif isinstance(child, QtTransientStatusWidget):
            before = self.find_next_child(child)
            self.widget().insertWidget(before, child.widget())


    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_grip_enabled(self, content):
        """ Handle the 'set_grip_enabled' action from the Enaml widget.

        """
        self.set_grip_enabled(content['grip_enabled'])

    def on_action_show_message(self, content):
        """ Handle the 'show_message' action from the Enaml widget

        """
        self.show_message(content['message'], content['timeout'])

    def on_action_clear_message(self, content):
        """ Handle the 'clear_message' action from the Enaml widget

        """
        self.clear_message()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_grip_enabled(self, grip_enabled):
        """ Set the size grip enabled on the underlying widget.

        """
        self.widget().setSizeGripEnabled(grip_enabled)

    def show_message(self, message, timeout=None):
        """ Show a message on the status bar

        Parameters
        ----------
        message: Str
            The message to show
        timeout: Int
            How long to show the message in seconds

        """
        self.widget().showMessage(message, timeout)

    def clear_message(self):
        """ Clear the current message on the status bar

        """
        self.widget().clearMessage()
