#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import implements

from .qt_component import QtComponent
from .styling import set_qwidget_bgcolor, set_qwidget_fgcolor
from .qt_layout_item import QtLayoutItem

from ..control import IControlImpl


class QtControl(QtComponent, QtLayoutItem):

    implements(IControlImpl)

    #--------------------------------------------------------------------------
    # IControlImpl interface
    #--------------------------------------------------------------------------
    def initialize_widget(self):
        pass
        
    def initialize_layout(self):
        """ Ensures that the control does not contain children. Special
        control subclasses that do allow for children should reimplement
        this method.

        """
        pass

    def preferred_size(self):
        size_hint = self.widget.sizeHint()
        return (size_hint.width(), size_hint.height())

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

