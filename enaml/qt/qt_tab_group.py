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

    def initialize(self, attrs):
        """ Initialize the widget attributes

        """
        super(QtTabGroup, self).initialize(attrs)
        self.set_selected_index(attrs['selected_index'])
        self.set_tab_position(attrs['tab_position'])
    
    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_message_set_selected_index(self, payload):
        """ Message handler for set_selected_index

        """
        self.set_selected_index(payload['selected_index'])

    def on_message_set_tab_position(self, payload):
        """ Message handler for set_tab_position

        """
        self.set_tab_position(payload['tab_position'])
        
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_selected_index(self, index):
        """ Set the widget's selected index

        """
        self.widget.setCurrentIndex(index)

    def set_tab_position(self, pos):
        """ Set the widget's tab position (top, bottom, left, or right)

        """
        self.widget.setTabPosition(_TAB_POS_MAP[pos])
