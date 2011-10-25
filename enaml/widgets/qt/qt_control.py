#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_component import QtComponent
# from .styling import set_qwidget_bgcolor, set_qwidget_fgcolor
from .qt_layout_item import QtLayoutItem

from ..control import AbstractTkControl


class QtControl(QtComponent, QtLayoutItem, AbstractTkControl):
    pass #??? lol
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    
    # def shell_bgcolor_changed(self, bgcolor):
    #     """ The change handler for the 'bgcolor' attribute. Not meant
    #     for public consumption.

    #     """
    #     self.set_bgcolor(bgcolor)
     
    # def shell_fgcolor_changed(self, fgcolor):
    #     """ The change handler for the 'fgcolor' attribute. Not meant
    #     for public consumption.

    #     """
    #     self.set_fgcolor(fgcolor)
    
    # def set_bgcolor(self, bgcolor):
    #     """ Set the background color of the widget.

    #     """
    #     set_qwidget_bgcolor(self.widget, bgcolor)
    
    # def set_fgcolor(self, fgcolor):
    #     """ Set the foreground color of the widget.

    #     """
    #     set_qwidget_fgcolor(self.widget, fgcolor)

