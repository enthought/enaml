#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import implements

from .qt_component import QtComponent
from .styling import set_qwidget_bgcolor, set_qwidget_fgcolor

from ..control import IControlImpl


class QtControl(QtComponent):

    implements(IControlImpl)

    #--------------------------------------------------------------------------
    # IControlImpl interface
    #--------------------------------------------------------------------------
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
        
    def parent_bgcolor_changed(self, bgcolor):
        """ The change handler for the 'bgcolor' attribute. Not meant
        for public consumption.

        """
        self.set_bgcolor(bgcolor)
     
    def parent_fgcolor_changed(self, fgcolor):
        """ The change handler for the 'fgcolor' attribute. Not meant
        for public consumption.

        """
        self.set_fgcolor(fgcolor)
    
    #--------------------------------------------------------------------------
    # Widget Update 
    #--------------------------------------------------------------------------
    def set_bgcolor(self, bgcolor):
        """ Set the background color of the widget.

        """
        set_qwidget_bgcolor(self.widget, bgcolor)
    
    def set_fgcolor(self, fgcolor):
        """ Set the foreground color of the widget.

        """
        set_qwidget_fgcolor(self.widget, fgcolor)

