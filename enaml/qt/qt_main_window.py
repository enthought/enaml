#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import Qt, Signal
from .qt.QtGui import QMainWindow
from .qt_container import QtContainer
from .qt_dock_pane import QtDockPane
from .qt_menu_bar import QtMenuBar
from .qt_tool_bar import QtToolBar
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
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying widget QMainWindow widget.

        """
        widget = QCustomMainWindow(parent)
        widget.setDocumentMode(True)
        widget.setDockNestingEnabled(True)
        return widget

    def init_layout(self):
        """ Initialize the layout for the underlying widget.

        """
        # The superclass' init_layout() method is explicitly not called
        # since the layout initialization for Window is not appropriate 
        # for MainWindow.
        main_window = self.widget()

        menu_bars = []
        tool_bars = []
        dock_panes = []
        containers = []
        for child in self.children():
            if isinstance(child, QtMenuBar):
                menu_bars.append(child)
            elif isinstance(child, QtToolBar):
                tool_bars.append(child)
            elif isinstance(child, QtDockPane):
                dock_panes.append(child)
            elif isinstance(child, QtContainer):
                containers.append(child)

        # Setup the menu bar
        for child in menu_bars:
            main_window.setMenuBar(child.widget())
            break

        # Setup the central widget
        for child in containers:
            main_window.setCentralWidget(child.widget())
            break

        # Setup the tool bars
        for child in tool_bars:
            bar_widget = child.widget()
            # XXX slight hack. When adding the toolbar to the main 
            # window, it is forcibly unfloated. In order for the 
            # initial floating state to be maintained, it must be
            # re-floating after being added. We do the refloating
            # in the future, so that the main window shows up first.
            floating = bar_widget.isFloating()
            main_window.addToolBar(bar_widget.toolBarArea(), bar_widget)
            if floating:
                QtMainWindow.deferred_call(bar_widget.setFloating, True)

        # Setup the dock panes
        for child in dock_panes:
            dock_widget = child.widget()
            main_window.addDockWidget(dock_widget.dockArea(), dock_widget)

        # Setup the status bar

