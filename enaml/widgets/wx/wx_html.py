#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx.html

from .wx_control import WXControl

from ..html import AbstractTkHtml


class WXHtml(WXControl, AbstractTkHtml):
    """ A wxPython implementation of Html

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying wx.html.HtmlWindow.

        """

        self.widget = wx.html.HtmlWindow(parent)

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

    def size_hint(self):
        """ Overridden parent class method to return a sensible size
        hint.

        """ 
        # wx returns (0, 0) for the best size of an HtmlWindow so we 
        # just return the same size hint as a QAbstractScrollArea
        return (256, 192)

