#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QMdiArea
from .qt_constraints_widget import QtConstraintsWidget
from .qt_mdi_window import QtMdiWindow


class QtMdiArea(QtConstraintsWidget):
    """ A Qt implementation of an Enaml MdiArea.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying QMdiArea widget.

        """
        return QMdiArea(parent)

    def init_layout(self):
        """ Initialize the layout for the underlying control.

        """
        super(QtMdiArea, self).init_layout()
        widget = self.widget()
        for child in self.children():
            if isinstance(child, QtMdiWindow):
                widget.addSubWindow(child.widget())

