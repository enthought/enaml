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

    def initialize(self, init_attrs):
        """ Initialize the attributes of the widget

        """
        self.set_title(init_attrs.get('title', ''))

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
        self.send("about_to_hide", {})

    def on_about_to_show(self):
        """ Event handler for about_to_show

        """
        self.send("about_to_show", {})
    
    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_set_title(self, ctxt):
        """ Message handler for set_title

        """
        return self.set_title(ctxt['value'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_title(self, title):
        """ Set the title of the menu

        """
        self.widget.setTitle(title)
        return True
