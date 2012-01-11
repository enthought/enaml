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

