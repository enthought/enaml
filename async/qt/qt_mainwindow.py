#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from PySide.QtGui import QMainWindow
from qt_window import QtWindow

class QtMainWindow(QtWindow):
    """ A Qt implementation of a main window
    
    """
    def create(self, parent):
        """ Create the underlying widget

        """
        self.widget = QMainWindow(parent)
        self.widget.show()

    def bind(self):
        """ Bind Qt signals to their respective slots

        """
        self.widget.closed.connect(self.on_closed)
        
    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_closed(self):
        """ The event handler for the closed event

        """
        self.send('closed', {})
