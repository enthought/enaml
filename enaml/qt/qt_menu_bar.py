#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import sys

from .qt.QtGui import QMainWindow, QMenuBar, QMenu
from .qt_widget_component import QtWidgetComponent


class QtMenuBar(QtWidgetComponent):
    """ A Qt implementation of an Enaml MenuBar.

    """
    #: Storage for the menu ids.
    _menu_ids = []

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

    def create(self, tree):
        """ Create and initialize the underlying control.

        """
        super(QtMenuBar, self).create(tree)
        self.set_menu_ids(tree['menu_ids'])

    def init_layout(self):
        """ Initialize the layout for the underlying control.

        """
        super(QtMenuBar, self).init_layout()
        widget = self.widget()
        find_child = self.find_child
        for menu_id in self._menu_ids:
            child = find_child(menu_id)
            if child is not None:
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
                temp = children[index + 1].widget()
                if isinstance(temp, QMenu):
                    before = temp.menuAction()
            widget = self.widget()
            child_widget = child.widget()
            if isinstance(child_widget, QMenu):
                widget.insertMenu(before, child_widget)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_menu_ids(self, menu_ids):
        """ Set the menu ids for the underlying control.

        """
        self._menu_ids = menu_ids

