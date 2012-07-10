#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QMenuBar
from .qt_widget_component import QtWidgetComponent

class QtMenuBar(QtWidgetComponent):
    """ A Qt implementation of a menu bar

    """
    def create(self):
        """ Create the underlying widget. We do not give it a parent,
        as this is the responsibility of the main window

        """
        self.widget = QMenuBar()

    def initialize(self, attrs):
        """ Initialize the widget attributes

        """
        super(QtMenuBar, self).initialize(attrs)
        self.set_menus(attrs['menus'])

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_message_set_menus(self, payload):
        """ Message handler for set_menus

        """
        self.set_menus(payload['menus'])
        
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_menus(self, menu_list):
        """ Set the menus within the menu bar

        """
        self.widget.clear()
        print menu_list
        for menu in menu_list:
            self.widget.addMenu(menu.widget)
