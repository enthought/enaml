#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui
from .qt_window import QtWindow

from ..main_window import AbstractTkMainWindow


class QtMainWindow(QtWindow, AbstractTkMainWindow):
    """ A Qt implementation of a MainWindow.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QMainWindow object.

        """
        self.widget = QtGui.QMainWindow(parent)

    def initialize(self):
        """ Initialize the QMainWindow object.

        """
        super(QtMainWindow, self).initialize()
        self.update_menu_bar()

    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    def shell_menu_bar_changed(self, menu_bar):
        """ Update the menu bar of the window with the new value from
        the shell object.

        """
        self.update_menu_bar()

    #--------------------------------------------------------------------------
    # Abstract Implementation
    #--------------------------------------------------------------------------
    def menu_bar_height(self):
        """ Returns the height of the menu bar in pixels. If the menu
        bar does not have an effect on the height of the main window,
        this method returns Zero.

        """
        # XXX The size hint is off by 1 pixel on Windows. What about
        # other platforms? Calling menuBar.height() here doesn't work
        # because the value is completely wrong unless the menu bar
        # is visible on the screen.

        # Get the menu bar from layout since that will not automatically
        # create one if it doesn't exist, unlike QMainWindow.menuBar()
        menu_bar = self.widget.layout().menuBar()
        if menu_bar is None:
            res = 0
        else:
            # FIXME - QMacStyle doesn't exist on non osx builds
            try:
                ismac = isinstance(menu_bar.style(), QtGui.QMacStyle)
            except AttributeError:
                ismac = False
            if ismac:
                res = 0
            elif menu_bar.isVisible():
                res = menu_bar.height()
            else:
                res = menu_bar.sizeHint().height()
                if res > 0:
                    res += 1
        return res

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def update_menu_bar(self):
        """ Updates the menu bar in the main window with the value
        from the shell object.

        """
        menu_bar = self.shell_obj.menu_bar
        if menu_bar is not None:
            self.widget.setMenuBar(menu_bar.toolkit_widget)
        else:
            self.widget.setMenuBar(None)

    def update_central_widget(self):
        """ Updates the central widget in the main window with the 
        value from the shell object.

        """
        # It's possible for the central widget component to be None.
        # This must be allowed since the central widget may be generated
        # by an Include component, in which case it will not exist 
        # during initialization. However, we must have a central widget
        # for the MainWindow, and in that case we just fill it with a
        # dummy widget.
        central_widget = self.shell_obj.central_widget
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

