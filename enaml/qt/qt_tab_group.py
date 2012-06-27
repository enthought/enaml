#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QTabWidget
from .qt_constraints_widget import QtConstraintsWidget

_TAB_POS_MAP = {
    'top': QTabWidget.North,
    'bottom': QTabWidget.South,
    'left': QTabWidget.West,
    'right': QTabWidget.East,
}

class QtTabGroup(QtConstraintsWidget):
    """ A Qt implementation of a tab group

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Create the underlying widget.

        """
        self.widget = QTabWidget(self.parent_widget)

    def initialize(self, init_attrs):
        """ Initialize the widget attributes

        """
        self.set_selected_index(init_attrs.get('selected_index', 0))
        self.set_tab_position(init_attrs.get('tab_position', 'top'))
    
    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_set_selected_index(self, ctxt):
        """ Message handler for set_selected_index

        """
        return self.set_selected_index(ctxt['value'])

    def receive_set_tab_position(self, ctxt):
        """ Message handler for set_tab_position

        """
        return self.set_tab_position(ctxt['value'])
        
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_selected_index(self, index):
        """ Set the widget's selected index

        """
        self.widget.setCurrentIndex(index)
        return True

    def set_tab_position(self, pos):
        """ Set the widget's tab position (top, bottom, left, or right)

        """
        self.widget.setTabPosition(_TAB_POS_MAP[pos])
        return True
