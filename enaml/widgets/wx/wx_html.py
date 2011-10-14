#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx.html

from traits.api import implements

from .wx_control import WXControl

from ..html import IHtmlImpl


class WXHtml(WXControl):
    """ A wxPython implementation of IHtml.
    
    The WXHtml widget renders html source using a wx.html.HtmlWindow.

    See Also
    --------
    IHtml
    
    """
    implements(IHtmlImpl)

    #---------------------------------------------------------------------------
    # IHtmlImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying html control.

        """
        # XXX GetBestSize on the HtmlWindow returns (0, 0) (wtf?)
        # So for now, we just set the min size to something sensible.
        self.widget = widget = wx.html.HtmlWindow(self.parent_widget(), 
                                                  size=(300, 200))
        widget.SetDoubleBuffered(True)

    def initialize_widget(self):
        """ Initializes the attributes of the control.

        """
        self.set_page_source(self.parent.source)
    
    def parent_source_changed(self, source):
        """ The change handler for the 'source' attribute. Not meant for
        public consumption.

        """
        self.set_page_source(source)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def set_page_source(self, source):
        """ Sets the page source for the underlying control. Not meant 
        for public consumption.

        """
        self.widget.SetPage(source)

