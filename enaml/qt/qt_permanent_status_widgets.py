#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import sys

from .qt_object import QtObject
from .qt_widget import QtWidget

class QtPermanentStatusWidgets(QtObject):
    """ A Qt implementation of the permanent children of an Enaml StatusBar

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ This is a virtual widget - return the parent status bar widget

        """
        return parent

    def init_layout(self):
        """ Initialize the layout for the underlying control.

        """
        super(QtPermanentStatusWidgets, self).init_layout()
        widget = self.widget()
        for child in self.children():
            if isinstance(child, QtWidget):
                widget.addPermanentWidget(child.widget())

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """ Handle the child removed event for a QtWidgetBar.

        """
        if isinstance(child, QtWidget):
            self.widget().removeWidget(child.widget())

    def child_added(self, child):
        """ Handle the child added event for a QtWidgetBar.

        """
        if isinstance(child, QtWidget):
            index = self.index_of(child)
            self.widget().insertPermanentWidget(index, child.widget())

