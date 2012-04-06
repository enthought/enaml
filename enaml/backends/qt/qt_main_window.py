#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui, QtCore
from .qt_window import QtWindow

from ...components.main_window import AbstractTkMainWindow


class _QMainWindow(QtGui.QMainWindow):
    """ A QMainWindow subclass which converts a close event into a 
    closed signal.

    """
    closed = QtCore.Signal()

    def closeEvent(self, event):
        super(_QMainWindow, self).closeEvent(event)
        self.closed.emit()


class QtMainWindow(QtWindow, AbstractTkMainWindow):
    """ A Qt implementation of a MainWindow.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QMainWindow object.

        """
        self.widget = _QMainWindow(parent)

    def initialize(self):
        super(QtMainWindow, self).initialize()
        shell = self.shell_obj
        self.set_menu_bar(shell.menu_bar)

    def bind(self):
        """ Bind the signal handlers for the QMainWindow.

        """
        super(QtMainWindow, self).bind()
        self.widget.closed.connect(self._on_close)

    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def shell_menu_bar_changed(self, menu_bar):
        """ The change handler for the 'menu_bar' attribute on the shell
        object.

        """
        self.set_menu_bar(menu_bar)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def _on_close(self):
        """ Emits the closed event on the shell object when the main 
        window is closed.

        """
        self.shell_obj.closed()
    
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_menu_bar(self, menu_bar):
        """ Updates the menu bar in the main window with the given Enaml
        MenuBar instance.

        """
        if menu_bar is not None:
            self.widget.setMenuBar(menu_bar.toolkit_widget)
        else:
            self.widget.setMenuBar(None)

    def set_central_widget(self, central_widget):
        """ Re-implemented parent class method to set the central widget
        on the underlying QMainWindow.

        """
        # It's possible for the central widget component to be None.
        # This must be allowed since the central widget may be generated
        # by an Include component, in which case it will not exist 
        # during initialization. However, we must have a central widget
        # for the MainWindow, and in that case we just fill it with a
        # dummy widget.
        if central_widget is None:
            child_widget = QtGui.QWidget()
        else:
            child_widget = central_widget.toolkit_widget
        self.widget.setCentralWidget(child_widget)

    def set_visible(self, visible):
        """ Overridden from the parent class to raise the window to
        the front if it should be shown.

        """
        widget = self.widget
        if visible:
            widget.setVisible(True)
            widget.raise_()
            widget.activateWindow()
        else:
            widget.setVisible(False)

