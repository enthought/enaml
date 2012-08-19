#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import Qt, Signal
from .qt.QtGui import QMainWindow
from .qt_utils import deferred_call
from .qt_window import QtWindow


class QCustomMainWindow(QMainWindow):
    """ A custom QMainWindow which adds some Enaml specific features.

    """
    #: A signal emitted when the window is closed by the user
    closed = Signal()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def closeEvent(self, event):
        """ A close event handler which emits the 'closed' signal.

        """
        super(QCustomMainWindow, self).closeEvent(event)
        self.closed.emit()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def setDockWidgetArea(self, area, dock_widget):
        """ Set the dock area for the given dock widget.

        If the dock widget has not been added to the main window, this
        method is a no-op.

        Parameters
        ----------
        area : QDockWidgetArea
            The dock area to use for the widget.

        dock_widget : QDockWidget
            The dock widget to move to the given area.

        """
        curr = self.dockWidgetArea(dock_widget)
        if curr != Qt.NoDockWidgetArea:
            if curr != area:
                visible = dock_widget.isVisible()
                self.removeDockWidget(dock_widget)
                self.addDockWidget(area, dock_widget)
                dock_widget.setVisible(visible)

    def setToolBarArea(self, area, tool_bar):
        """ Set the tool bar area for the given tool bar.

        If the tool bar has not been added to the main window, this
        method is a no-op.

        Parameters
        ----------
        area : QToolBarArea
            The tool bar area to use for the widget.

        tool_bar : QToolBar
            The tool bar to move to the given area.

        """
        curr = self.toolBarArea(tool_bar)
        if curr != Qt.NoToolBarArea:
            if curr != area:
                visible = tool_bar.isVisible()
                floating = tool_bar.isFloating()
                tool_bar.setVisible(False)
                self.removeToolBar(tool_bar)
                self.addToolBar(area, tool_bar)
                tool_bar.resize(tool_bar.sizeHint())
                tool_bar.setFloating(floating)
                tool_bar.setVisible(visible)


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
        widget = QCustomMainWindow(parent)
        widget.setDocumentMode(True)
        return widget

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
                bar_widget = tool_bar.widget()
                # XXX slight hack. When adding the toolbar to the main 
                # window, it is forcibly unfloated. In order for the 
                # initial floating state to be maintained, it must be
                # re-floating after being added. We do the refloating
                # in the future, so that the main window shows up first.
                floating = bar_widget.isFloating()
                main_window.addToolBar(bar_widget.toolBarArea(), bar_widget)
                if floating:
                    deferred_call(bar_widget.setFloating, True)

        # Setup the dock panes
        for dock_id in self._dock_pane_ids:
            dock_pane = find_child(dock_id)
            if dock_pane is not None:
                dock_widget = dock_pane.widget()
                main_window.addDockWidget(dock_widget.dockArea(), dock_widget)

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

