#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from PySide.QtGui import QWidget

from qt_client_widget import QtClientWidget


class QtWindow(QtClientWidget):

    def create(self, parent):
        self.widget = QWidget(parent)
        self.widget.show()

    def initialize(self, init_attrs):
        self.set_title(init_attrs.get('title', ''))

    def receive_set_title(self, ctxt):
        title = ctxt.get('value')
        if title is not None:
            self.set_title(title)
    
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_title(self, title):
        self.widget.setWindowTitle(title)

