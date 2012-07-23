#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_constraints_widget import QtConstraintsWidget
from .qt.QtGui import QTabBar


DOCUMENT_MODES = {
    'document': True,
    'preferences': False,
}


class QtTabBar(QtConstraintsWidget):
    """ A Qt4 implementation of an Enaml TabBar.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Create the underlying widget.

        """
        self.widget = QTabBar(self.parent_widget)

    def initialize(self, attrs):
        """ Initialize the widget attributes

        """
        super(QtTabBar, self).initialize(attrs)
        self.set_tab_style(attrs['tab_style'])
        self.set_tabs_closable(attrs['tabs_closable'])
        self.set_tabs_movable(attrs['tabs_movable'])

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_message_set_tab_style(self, payload):
        """ Handle the 'set-tab_style' action from the Enaml widget.

        """
        self.set_tab_style(payload['tab_style'])

    def on_message_set_tabs_closable(self, payload):
        """ Handle the 'set-tabs_closable' action from the Enaml widget.

        """
        self.set_tabs_closable(payload['tabs_closable'])

    def on_message_set_tabs_movable(self, payload):
        """ Handle the 'set-tabs_movable' action from the Enaml widget.

        """
        self.set_tabs_movable(payload['tabs_movable'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_tab_style(self, style):
        """ Set the tab style for the tab bar in the widget.

        """
        self.widget.setDocumentMode(DOCUMENT_MODES[style])

    def set_tabs_closable(self, closable):
        """ Set whether or not the tabs are closable.

        """
        self.widget.setTabsClosable(closable)

    def set_tabs_movable(self, movable):
        """ Set whether or not the tabs are movable.

        """
        self.widget.setMovable(movable)
