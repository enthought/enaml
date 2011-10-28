#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx.html

from .wx_control import WXControl
from ..html import AbstractTkHtml

class WXHtml(WXControl, AbstractTkHtml):
    """ A wxPython implementation of IHtml.

    The WXHtml widget renders html source using a wx.html.HtmlWindow.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying html control.

        """
        # XXX GetBestSize on the HtmlWindow returns (0, 0)
        # So for now, we just set the min size to something sensible.
        self.widget = wx.html.HtmlWindow(self.parent_widget(), size=(300, 200))

    def initialize(self):
        """ Initializes the attributes of the control.

        """
        shell = self.shell_obj
        self.set_page_source(shell.source)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def shell_source_changed(self, source):
        """ The change handler for the 'source' attribute.
        """
        self.set_page_source(source)

    def set_page_source(self, source):
        """ Sets the page source for the underlying control.

        """
        self.widget.SetPage(source)

