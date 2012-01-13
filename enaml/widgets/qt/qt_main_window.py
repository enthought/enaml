#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_resizing_widgets import QResizingMainWindow
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
        self.widget = QResizingMainWindow(parent)

    # Note: On Qt a MenuBar that is defined as a child of a MainWindow
    # will be automatically added as the menubar. There is no need
    # to explicitly call setMenuBar(...).

