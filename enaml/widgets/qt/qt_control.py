#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Instance, implements

from .qt_component import QtComponent
from .styling import QtStyleHandler, qt_color

from ..control import IControlImpl


class QtControl(QtComponent):

    implements(IControlImpl)

    #---------------------------------------------------------------------------
    # IControlImpl interface
    #---------------------------------------------------------------------------
    def create_style_handler(self):
        """ Creates and sets the style handler for the widget. Must
        be implemented by subclasses.

        """
        style_handler = QtStyleHandler(widget=self.widget, tags=self.tags)
        style_handler.node = self.parent.style
        self.style_handler = style_handler

    def initialize_style(self):
        """ Initializes the style and style handler of a widget. Must
        be implemented by subclasses.

        """
        self.style_handler.initialize_style()

    def layout_child_widgets(self):
        """ Ensures that the control does not contain children. Special
        control subclasses that do allow for children should reimplement
        this method.

        """
        if list(self.child_widgets()):
            raise ValueError('Standard controls cannot have children.')


    style_handler = Instance(QtStyleHandler)
   
    tags = {
        'background_color': qt_color,
    }
