#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QTabWidget
from .qt_constraints_widget import QtConstraintsWidget


TAB_POSITIONS = {
    'top': QTabWidget.North,
    'bottom': QTabWidget.South,
    'left': QTabWidget.West,
    'right': QTabWidget.East,
}


DOCUMENT_MODES = {
    'document': True,
    'preferences': False,
}


class QtNotebook(QtConstraintsWidget):
    """ A Qt4 implementation of an Enaml Notebook.

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
        super(QtNotebook, self).initialize(attrs)
        self.set_tab_position(attrs['tab_position'])
        self.set_tab_style(attrs['tab_style'])
        self.set_tabs_closable(attrs['tabs_closable'])
        self.set_tabs_movable(attrs['tabs_movable'])
        self.widget.tabCloseRequested.connect(self.on_tab_close_requested)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_message_set_tab_position(self, payload):
        """ Handle the 'set-tab_position' action from the Enaml widget.

        """
        self.set_tab_position(payload['tab_position'])
        
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

    def on_message_open_tab(self, payload):
        """ Handle the 'open-tab' action from the Enaml widget.

        """
        target_id = payload['target_id']
        for child in self.children:
            if child.target_id == target_id:
                idx = self.widget.indexOf(child.widget)
                if idx == -1:
                    self.widget.addTab(child.widget, child.get_title())
                return

    def on_message_close_tab(self, payload):
        """ Handle the 'close-page' action from the Enaml widget.

        """
        target_id = payload['target_id']
        for child in self.children:
            if child.target_id == target_id:
                idx = self.widget.indexOf(child.widget)
                if idx != -1:
                    self.widget.removeTab(idx)
                return

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_tab_close_requested(self, index):
        """ The signal handler for the 'tabCloseRequested' signal.

        """
        widget = self.widget.widget(index)
        self.widget.removeTab(index)
        for child in self.children:
            if widget == child.widget:
                target_id = child.target_id
                payload = {'action': 'tab-closed', 'target_id': target_id}
                self.send_message(payload)
                return

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_tab_position(self, position):
        """ Set the position of the tab bar in the widget.

        """
        self.widget.setTabPosition(TAB_POSITIONS[position])

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

