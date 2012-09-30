#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import sys

from .qt.QtGui import QMainWindow, QMenuBar
from .qt_menu import QtMenu
from .qt_widget_component import QtWidgetComponent


class QtMenuBar(QtWidgetComponent):
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
    def child_added(self, child):
        """ Handle the child added event for a QtMenuBar.

        This handler ensures that the child is inserted in the proper
        place in the menu bar.

        """
        child.initialize()
        index = self.index_of(child)
        if index != -1:
            before = None
            children = self.children()
            if index < len(children) - 1:
                temp = children[index + 1]
                if isinstance(temp, QtMenu):
                    before = temp.widget().menuAction()
            widget = self.widget()
            if isinstance(child, QtMenu):
                widget.insertMenu(before, child.widget())

