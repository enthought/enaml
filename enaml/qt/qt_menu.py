#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QMenu
from .qt_widget_component import QtWidgetComponent

class QtMenu(QtWidgetComponent):
    """ A Qt implementation of a menu

    """
    def create(self):
        """ Create the underlying widget

        """
        self.widget = QMenu(self.parent_widget)

    def initialize(self, attrs):
        """ Initialize the attributes of the widget

        """
        super(QtMenu, self).initialize(attrs)
        self.set_title(attrs['title'])

    def bind(self):
        """ Bind the widget's events

        """
        self.widget.aboutToHide.connect(self.on_about_to_hide)
        self.widget.aboutToShow.connect(self.on_about_to_show)

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_about_to_hide(self):
        """ Event handler for about_to_hide

        """
        self.send_message({'action':'about_to_hide'})

    def on_about_to_show(self):
        """ Event handler for about_to_show

        """
        self.send_message({'action':'about_to_show'})
    
    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_message_set_title(self, payload):
        """ Message handler for set_title

        """
        self.set_title(payload['title'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_title(self, title):
        """ Set the title of the menu

        """
        self.widget.setTitle(title)
