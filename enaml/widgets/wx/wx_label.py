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
    def create(self, parent):
        """ Creates the underlying wx.StaticText control.

        """
        self.widget = wx.StaticText(parent)

    def initialize(self):
        """ Initializes the attributes on the underlying control.

        """
        super(WXLabel, self).initialize()
        self.set_label(self.shell_obj.text)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_text_changed(self, text):
        """ The change handler for the 'text' attribute on the shell 
        component.

        """
        self.set_label(text)

    def shell_word_wrap_changed(self, wrap):
        """ The change handler for the 'word_wrap' attribute on the 
        shell component. Wx does not support word wrap, so this is 
        a no-op.

        """
        pass

    def set_label(self, label):
        """ Sets the label on the underlying control.

        """
        self.widget.SetLabel(label)

    