#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import sys

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
    #: A private flag used to track the visible state changes sent from
    #: the Enaml widget. This is needed on OSX when dynamically adding
    #: a tool bar in order to work around a visibility bug in Qt.
    _visible_hint = False

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

        # Setup the menu bar. All but the first are ignored.
        for child in menu_bars:
            main_window.setMenuBar(child.widget())
            break

        # Setup the central widget. All but the first are ignored.
        for child in containers:
            main_window.setCentralWidget(child.widget())
            break

        # Setup the tool bars.
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

        # Setup the dock panes.
        for child in dock_panes:
            dock_widget = child.widget()
            main_window.addDockWidget(dock_widget.dockArea(), dock_widget)

        # Setup the status bar

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """ Handle the child removed event for a QtMainWindow.

        """
        main_window = self.widget()
        if isinstance(child, QtDockPane):
            main_window.removeDockWidget(child.widget())
        elif isinstance(child, QtToolBar):
            main_window.removeToolBar(child.widget())

    def child_added(self, child):
        """ Handle the child added event for a QtMainWindow.

        """
        # XXX there is quite a bit of duplicated code here. It would
        # be nice to clean this up at some point.
        main_window = self.widget()

        # Add a child QtMenuBar. It's not known if the given child is
        # the first QtMenuBar child in the list of children. So, the
        # list is scanned and the first one found is set as the menu
        # bar for the window.
        if isinstance(child, QtMenuBar):
            for child in self.children():
                if isinstance(child, QtMenuBar):
                    main_window.setMenuBar(child.widget())
                    break

        # Add a child QtContainer. It's not known if the given child is
        # the first QtContainer child in the list of children. So, the
        # list is scanned and the first one found is set as the central
        # widget for the window.
        elif isinstance(child, QtContainer):
            for child in self.children():
                if isinstance(child, QtContainer):
                    main_window.setCentralWidget(child.widget())
                    break

        # Add a child QtToolBar. There are two hacks involved in adding
        # a tool bar. The first is the same hack that is perfomed in the
        # `init_layout` method for a floating tool bar. The second is
        # specific to OSX. On the platform, adding a tool bar to main
        # window which is already visible but does not have any current
        # tool bars will cause the main window to be hidden. This will
        # only occur the *first* time a tool bar is added to the window.
        # The hack below is workaround which should be sufficient for
        # most use cases. A bug should really be filed against Qt for
        # this one, as it's reproducible outside of Enaml.
        elif isinstance(child, QtToolBar):
            bar_widget = child.widget()
            reshow = False
            if sys.platform == 'darwin':
                reshow = self._visible_hint and not main_window.isVisible()
            floating = bar_widget.isFloating()
            main_window.addToolBar(bar_widget.toolBarArea(), bar_widget)
            if floating:
                QtMainWindow.deferred_call(bar_widget.setFloating, True)
            if reshow:
                main_window.setVisible(True)

        # Add a child QtDockPane.
        elif isinstance(child, QtDockPane):
            dock_widget = child.widget()
            main_window.addDockWidget(dock_widget.dockArea(), dock_widget)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_visible(self, visible):
        """ Set the visibility of the underlying control.

        This is an overridden parent class method which keeps track of
        the visible flag set by the Enaml widget.

        """
        self._visible_hint = visible
        super(QtMainWindow, self).set_visible(visible)

