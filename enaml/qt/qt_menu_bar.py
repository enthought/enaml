#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import sys

from .qt.QtGui import QMainWindow, QMenuBar
from .qt_menu import QtMenu
from .qt_widget import QtWidget


class QtMenuBar(QtWidget):
    """ A Qt implementation of an Enaml MenuBar.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying menu bar widget.

        """
        # On OSX, there is a weird issue where creating a QMenuBar with
        # a parent will cause the menu bar to not show up when its added
        # to the main window. On that platform we work around the issue
        # by having the QMainWindow create the menu bar for us, or by
        # creating it without a parent. This issue is even more weird,
        # because in the C++ code for QMainWindow::menuBar() the newly
        # created menu bar is given the QMainWindow as its parent...
        if sys.platform == 'darwin':
            if isinstance(parent, QMainWindow):
                menu_bar = parent.menuBar()
            else:
                menu_bar = QMenuBar()
        else:
            menu_bar = QMenuBar(parent)
        return menu_bar

    def init_layout(self):
        """ Initialize the layout for the underlying control.

        """
        super(QtMenuBar, self).init_layout()
        widget = self.widget()
        for child in self.children():
            if isinstance(child, QtMenu):
                widget.addMenu(child.widget())

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """ Handle the child removed event for a QtMenuBar.

        """
        if isinstance(child, QtMenu):
            self.widget().removeAction(child.widget().menuAction())

    def child_added(self, child):
        """ Handle the child added event for a QtMenuBar.

        """
        if isinstance(child, QtMenu):
            before = self.find_next_action(child)
            self.widget().insertMenu(before, child.widget())

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def find_next_action(self, child):
        """ Get the QAction instance which comes immediately after the
        actions of the given child.

        Parameters
        ----------
        child : QtMenu
            The child menu of interest.

        Returns
        -------
        result : QAction or None
            The QAction which comes immediately after the actions of the
            given child, or None if no actions follow the child.

        """
        # The target action must be tested for membership against the
        # current actions on the menu bar itself, since this method may
        # be called after a child is added, but before the actions for
        # the child have actually added to the menu.
        index = self.index_of(child)
        if index != -1:
            actions = set(self.widget().actions())
            for child in self.children()[index + 1:]:
                if isinstance(child, QtMenu):
                    target = child.widget().menuAction()
                    if target in actions:
                        return target

