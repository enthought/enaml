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
    """ A Qt4 implementation of an Enaml ScrollArea.

    """
    def create(self):
        """ Create the underlying QScrollArea widget.

        """
        self.widget = QScrollArea(self.parent_widget)
        # XXX we may want to make this an option in the future.
        # For now, it's hard coded since the most common child
        # of a scroll area is a Container, which should be resized.
        self.widget.setWidgetResizable(True)

    def initialize(self, attrs):
        """ Initialize the widget attributes

        """
        super(QtScrollArea, self).initialize(attrs)
        self.set_horizontal_scrollbar(attrs['horizontal_scrollbar'])
        self.set_vertical_scrollbar(attrs['vertical_scrollbar'])

    def post_initialize(self):
        """ Handle post initialization for the scroll area.

        This methods adds the first child as the scrolled widget.
        Specifying more than one child of a scroll area will result
        in undefined behavior.

        """
        children = self.children
        if children:
            self.widget.setWidget(children[0].widget)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_horizontal_scrollbar(self, content):
        """ Handle the 'set_horizontal_scrollbar' action from the Enaml
        widget.

        """
        policy = content['horizontal_scrollbar']
        self.set_horizontal_scrollbar(policy)

    def on_action_set_vertical_scrollbar(self, content):
        """ Handle the 'set_vertical_scrollbar' action from the Enaml
        widget.

        """
        policy = content['vertical_scrollbar']
        self.set_vertical_scrollbar(policy)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_horizontal_scrollbar(self, policy):
        """ Set the horizontal scrollbar policy of the widget.

        """
        self.widget.setHorizontalScrollBarPolicy(SCROLLBAR_MAP[policy])

    def set_vertical_scrollbar(self, policy):
        """ Set the vertical scrollbar policy of the widget.

        """
        self.widget.setVerticalScrollBarPolicy(SCROLLBAR_MAP[policy])

