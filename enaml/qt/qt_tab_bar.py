#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_constraints_widget import QtConstraintsWidget
from .qt.QtGui import QTabBar, QPushButton
from .qt.QtCore import Signal


DOCUMENT_MODES = {
    'document': True,
    'preferences': False,
}


class EnamlQTabBar(QTabBar):
    """ A tab bar with an add button

    """
    tabAdded = Signal()

    def __init__(self, parent=None):
        super(EnamlQTabBar, self).__init__(parent)
        self.add_button = QPushButton("+", self)
        self.add_button.setFlat(True)
        self.add_button.clicked.connect(self.tabAdded)

    def resizeEvent(self, event):
        super(EnamlQTabBar, self).resizeEvent(event)
        x = self.size().width() - self.add_button.size().width()
        y = (self.size().height() - self.add_button.size().height()) / 2
        self.add_button.move(x, y)


class QtTabBar(QtConstraintsWidget):
    """ A Qt4 implementation of an Enaml TabBar.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Create the underlying widget.

        """
        self.widget = EnamlQTabBar(self.parent_widget)
        self.widget.tabMoved.connect(self.on_tab_moved)
        self.widget.currentChanged.connect(self.on_current_changed)
        self.widget.tabCloseRequested.connect(self.on_tab_close_requested)
        self.widget.tabAdded.connect(self.on_tab_added)

    def initialize(self, attrs):
        """ Initialize the widget attributes

        """
        super(QtTabBar, self).initialize(attrs)
        self.set_tabs(attrs['tabs'])
        self.set_tab_style(attrs['tab_style'])
        self.set_tabs_closable(attrs['tabs_closable'])
        self.set_tabs_movable(attrs['tabs_movable'])

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_message_set_tabs(self, payload):
        """ Handle the 'set-tabs' action from the Enaml widget.

        """
        self.set_tabs(payload['tabs'])

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

    def on_message_add_tab(self, payload):
        """ Handle the 'add-tab' action from the Enaml widget.

        """
        self.add_tab(payload['title'])

    def on_message_remove_tab(self, payload):
        """ Handle the 'remove-tab' action from the Enaml widget.

        """
        self.remove_tab(payload['index'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_tabs(self, tabs):
        """ Set the tabs of the tab bar

        """
        for i in range(self.widget.count()):
            self.widget.removeTab(i)
        for tab in tabs:
            self.widget.addTab(tab)

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

    def add_tab(self, title):
        """ Add a tab to the widget

        """
        self.widget.addTab(title)

    def remove_tab(self, index):
        """ Remove the tab at a given index

        """
        self.widget.removeTab(index)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_current_changed(self, index):
        """ The signal handler for the 'currentChanged' signal.

        """
        payload = {
            'action': 'tab-changed',
            'index': index
        }
        self.send_message(payload)

    def on_tab_close_requested(self, index):
        """ The signal handler for the 'tabCloseRequested' signal.

        """
        payload = {
            'action': 'tab-closed',
            'index': index
        }
        self.send_message(payload)

    def on_tab_added(self):
        """ The signal handler for the 'tabAdded' signal.

        """
        payload = {
            'action': 'tab-added'
        }
        self.send_message(payload)

    def on_tab_moved(self, new, old):
        """ The signal handler for the 'tabMoved' signal

        """
        payload = {
            'action': 'tab-moved',
            'old': old,
            'new': new
        }
        self.send_message(payload)
