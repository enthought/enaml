#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_control import WXControl
from ..label import AbstractTkLabel


class WXLabel(WXControl, AbstractTkLabel):
    """ A wxPython implementation of Label.

    A WXLabel displays static text using a wx.StaticText control.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying text control.

        """
        self.widget = widget = wx.StaticText(self.parent_widget())

    def initialize(self):
        """ Initializes the attributes on the underlying control.

        """
        super(WXLabel, self).initialize()
        shell = self.shell_obj
        self.set_label(shell.text)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_text_changed(self, text):
        """ The change handler for the 'text' attribute.

        """
        self.set_label(text)
        self.shell_obj.size_hint_updated = True

    def set_label(self, label):
        """ Sets the label on the underlying control.

        """
        self.widget.SetLabel(label)

