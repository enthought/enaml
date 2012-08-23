#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QScrollArea
from .qt.QtCore import Qt
from .qt_constraints_widget import QtConstraintsWidget


SCROLLBAR_MAP = {
    'as_needed' : Qt.ScrollBarAsNeeded,
    'always_off' : Qt.ScrollBarAlwaysOff,
    'always_on' : Qt.ScrollBarAlwaysOn
}


class QtScrollArea(QtConstraintsWidget):
    """ A Qt implementation of an Enaml ScrollArea.

    """
    #: Storage for the scroll widget id
    _scroll_widget_id = None

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying QScrollArea widget.

        """
        widget = QScrollArea(parent)
        # XXX we may want to make this an option in the future.
        widget.setWidgetResizable(True)
        return widget

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtScrollArea, self).create(tree)
        self.set_scroll_widget_id(tree['scroll_widget_id'])
        self.set_horizontal_scrollbar(tree['horizontal_scrollbar'])
        self.set_vertical_scrollbar(tree['vertical_scrollbar'])

    def init_layout(self):
        """ Initialize the layout of the underlying widget.

        """
        child = self.find_child(self._scroll_widget_id)
        if child is not None:
            self.widget().setWidget(child.widget())

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_horizontal_scrollbar(self, content):
        """ Handle the 'set_horizontal_scrollbar' action from the Enaml
        widget.

        """
        self.set_horizontal_scrollbar(content['horizontal_scrollbar'])

    def on_action_set_vertical_scrollbar(self, content):
        """ Handle the 'set_vertical_scrollbar' action from the Enaml
        widget.

        """
        self.set_vertical_scrollbar(content['vertical_scrollbar'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_scroll_widget_id(self, widget_id):
        """ Set the scroll widget id for the underlying widget.

        """
        self._scroll_widget_id = widget_id
    
    def set_horizontal_scrollbar(self, policy):
        """ Set the horizontal scrollbar policy of the widget.

        """
        self.widget().setHorizontalScrollBarPolicy(SCROLLBAR_MAP[policy])

    def set_vertical_scrollbar(self, policy):
        """ Set the vertical scrollbar policy of the widget.

        """
        self.widget().setVerticalScrollBarPolicy(SCROLLBAR_MAP[policy])

