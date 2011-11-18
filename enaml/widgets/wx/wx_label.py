#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_control import WXControl

from ..label import AbstractTkLabel


class WXLabel(WXControl, AbstractTkLabel):
    """ A wxPython implementation of Label.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying wx.StaticText control.

        """
        self.widget = wx.StaticText(self.parent_widget())

    def initialize(self):
        """ Initializes the attributes on the underlying control.

        """
        super(WXLabel, self).initialize()
        self.set_label(self.shell_obj.text)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_text_changed(self, text):
        """ The change handler for the 'text' attribute.

        """
        self.set_label(text)
        # If the text in the label changes, then the size hint of
        # label will have changed, and the layout system needs to
        # be informed.
        self.shell_obj.size_hint_updated = True
        
    def set_label(self, label):
        """ Sets the label on the underlying control.

        """
        self.widget.SetLabel(label)

