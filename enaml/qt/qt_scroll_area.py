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

    def initialize(self, init_attrs):
        """ Initialize the widget attributes

        """
        self.set_horizontal_scroll_policy(init_attrs.get(
            'horizontal_scroll_policy', 'as_needed'))
        self.set_preferred_size(init_attrs.get('preferred_size', (100, 100)))
        self.set_scroll_position(init_attrs.get('scroll_position', (0, 0)))
        self.set_scrolled_component(init_attrs.get('scrolled_component',
                                                   QWidget()))
        self.set_vertical_scroll_policy(init_attrs.get(
            'vertical_scroll_policy', 'as_needed'))
    
    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_set_horizontal_scroll_policy(self, ctxt):
        """ Message handler for set_horizontal_scroll_policy

        """
        return self.set_horizontal_scroll_policy(ctxt['value'])

    def receive_set_preferred_size(self, ctxt):
        """ Message handler for set_preferred_size

        """
        return self.set_preferred_size(ctxt['value'])

    def receive_set_scroll_position(self, ctxt):
        """ Message handler for set_scroll_position

        """
        return self.set_scroll_position(ctxt['value'])

    def receive_set_scrolled_component(self, ctxt):
        """ Message handler for set_scrolled_component

        """
        return self.set_scrolled_component(ctxt['value'])

    def receive_set_vertical_scroll_policy(self, ctxt):
        """ Message handler for set_vertical_scroll_policy

        """
        return self.set_vertical_scroll_policy(ctxt['value'])
        
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_horizontal_scroll_policy(self, policy):
        """ Set the horizontal scroll policy of the widget

        """
        self.widget.setHorizontalScrollBarPolicy(_SCROLLBAR_POLICY_MAP[policy])
        return True

    def set_preferred_size(self, size):
        """ Set the preferred size of the widget

        """
        # XXX
        return True

    def set_scroll_position(self, pos):
        """ Set the scroll position of the widget

        """
        horizontal_pos, vertical_pos = pos
        self.widget.horizontalScrollBar().setValue(horizontal_pos)
        self.widget.verticalScrollBar().setValue(vertical_pos)
        return True

    def set_scrolled_component(self, comp):
        """ Set the component to be scrolled of the widget

        """
        self.widget.setViewport(comp)
        return True

    def set_vertical_scroll_policy(self, policy):
        """ Set the vertical scroll policy of the widget

        """
        self.widget.setVerticalScrollBarPolicy(_SCROLLBAR_POLICY_MAP[policy])
        return True
