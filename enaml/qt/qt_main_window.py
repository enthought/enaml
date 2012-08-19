#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import Qt, Signal
from .qt.QtGui import QMainWindow
from .qt_window import QtWindow


class QCustomMainWindow(QMainWindow):

    closed = Signal()


class QtMainWindow(QtWindow):
    """ A Qt implementation of an Enaml MainWindow.
    
    """
    #: Storage for the menu bar id.
    _menu_bar_id = None

    #: Storage for the widget ids of the tool bars.
    _tool_bar_ids = []

    #: Storage for the widget ids of the dock panes.
    _dock_pane_ids = []

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying widget QMainWindow widget.

        """
        return QCustomMainWindow(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtMainWindow, self).create(tree)
        self.set_menu_bar_id(tree['menu_bar_id'])
        self.set_dock_pane_ids(tree['dock_pane_ids'])
        self.set_tool_bar_ids(tree['tool_bar_ids'])

    def init_layout(self):
        """ Initialize the layout for the underlying widget.

        """
        # The superclass' init_layout() method is explicitly not called
        # since the layout initialization for Window is not appropriate 
        # for MainWindow.
        main_window = self.widget()
        find_child = self.find_child

        # Setup the menu bar
        menu_bar = find_child(self._menu_bar_id)
        if menu_bar is not None:
            main_window.setMenuBar(menu_bar.widget())

        # Setup the central widget
        central_child = find_child(self._central_widget_id)
        if central_child is not None:
            main_window.setCentralWidget(central_child.widget())

        # Set up the tool bars
        for tool_bar_id in self._tool_bar_ids:
            tool_bar = find_child(tool_bar_id)
            if tool_bar is not None:
                main_window.addToolBar(tool_bar.widget())

        # Setup the dock panes
        for dock_id in self._dock_pane_ids:
            dock_pane = find_child(dock_id)
            if dock_pane is not None:
                main_window.addDockWidget(Qt.LeftDockWidgetArea, dock_pane.widget())

        # Setup the status bar

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_menu_bar_id(self, menu_bar_id):
        """ Set the menu bar id for the underlying widget.

        """
        self._menu_bar_id = menu_bar_id

    def set_dock_pane_ids(self, pane_ids):
        """ Set the dock pane ids for the underlying widget.

        """
        self._dock_pane_ids = pane_ids

    def set_tool_bar_ids(self, bar_ids):
        """ Set the tool bar ids for the underlying widget.

        """
        self._tool_bar_ids = bar_ids

