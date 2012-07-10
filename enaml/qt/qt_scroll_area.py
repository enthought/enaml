#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QScrollArea, QWidget
from .qt.QtCore import Qt
from .qt_constraints_widget import QtConstraintsWidget

_SCROLLBAR_POLICY_MAP = {
    'as_needed' : Qt.ScrollBarAsNeeded,
    'always_off' : Qt.ScrollBarAlwaysOff,
    'always_on' : Qt.ScrollBarAlwaysOn
}

class QtScrollArea(QtConstraintsWidget):
    """ A Qt implementation of a scroll area

    """
    def create(self):
        """ Create the underlying widget.

        """
        self.widget = QScrollArea(self.parent_widget)

    def initialize(self, attrs):
        """ Initialize the widget attributes

        """
        super(QtScrollArea, self).initialize(attrs)
        self.set_horizontal_scroll_policy(attrs['horizontal_scroll_policy'])
        self.set_preferred_size(attrs['preferred_size'])
        self.set_scroll_position(attrs['scroll_position'])
        self.set_scrolled_component(attrs['scrolled_component'])
        self.set_vertical_scroll_policy(attrs['vertical_scroll_policy'])
    
    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_message_set_horizontal_scroll_policy(self, payload):
        """ Message handler for set_horizontal_scroll_policy

        """
        self.set_horizontal_scroll_policy(
            payload['horizontal_scroll_policy'])

    def on_message_set_preferred_size(self, payload):
        """ Message handler for set_preferred_size

        """
        self.set_preferred_size(payload['preferred_size'])

    def on_message_set_scroll_position(self, payload):
        """ Message handler for set_scroll_position

        """
        self.set_scroll_position(payload['scroll_position'])

    def on_message_set_scrolled_component(self, payload):
        """ Message handler for set_scrolled_component

        """
        self.set_scrolled_component(payload['scrolled_component'])

    def on_message_set_vertical_scroll_policy(self, payload):
        """ Message handler for set_vertical_scroll_policy

        """
        self.set_vertical_scroll_policy(payload['vertical_scroll_policy'])
        
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_horizontal_scroll_policy(self, policy):
        """ Set the horizontal scroll policy of the widget

        """
        self.widget.setHorizontalScrollBarPolicy(_SCROLLBAR_POLICY_MAP[policy])

    def set_preferred_size(self, size):
        """ Set the preferred size of the widget

        """
        # XXX
        pass
    
    def set_scroll_position(self, pos):
        """ Set the scroll position of the widget

        """
        horizontal_pos, vertical_pos = pos
        self.widget.horizontalScrollBar().setValue(horizontal_pos)
        self.widget.verticalScrollBar().setValue(vertical_pos)

    def set_scrolled_component(self, comp):
        """ Set the component to be scrolled of the widget

        """
        self.widget.setViewport(comp)

    def set_vertical_scroll_policy(self, policy):
        """ Set the vertical scroll policy of the widget

        """
        self.widget.setVerticalScrollBarPolicy(_SCROLLBAR_POLICY_MAP[policy])
