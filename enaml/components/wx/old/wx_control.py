#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import implements

from .wx_component import WXComponent
from .styling import set_wxwidget_bgcolor, set_wxwidget_fgcolor

from ..control import IControlImpl


class WXControl(WXComponent):

    implements(IControlImpl)

    #---------------------------------------------------------------------------
    # IControlImpl interface
    #---------------------------------------------------------------------------
    def initialize_style(self):
        pass
    
    def parent_bgcolor_changed(self, bgcolor):
        self.set_bgcolor(bgcolor)
    
    def parent_fgcolor_changed(self, fgcolor):
        self.set_fgcolor(fgcolor)

    def layout_child_widgets(self):
        """ Ensures that the control does not contain children. Special
        control subclasses that do allow for children should reimplement
        this method.

        """
        if list(self.child_widgets()):
            raise ValueError('Standard controls cannot have children.')

    #--------------------------------------------------------------------------
    # Widget Update 
    #--------------------------------------------------------------------------
    def set_bgcolor(self, bgcolor):
        """ Set the background color of the widget.

        """
        set_wxwidget_bgcolor(self.widget, bgcolor)
    
    def set_fgcolor(self, fgcolor):
        """ Set the foreground color of the widget.

        """
        set_wxwidget_fgcolor(self.widget, fgcolor)

