import wx.html

from traits.api import implements, Str

from .wx_element import WXElement

from ..i_html import IHtml


class WXHtml(WXElement):
    """ A wxWidgets implementation of IHtml.
    
    Attributes
    ----------
    html : Str
        The HTML to be rendered.
    
    """
    implements(IHtml)

    #===========================================================================
    # IHtml interface
    #===========================================================================
    source = Str

    #===========================================================================
    # Implementation
    #===========================================================================

    #---------------------------------------------------------------------------
    # Initialization
    #---------------------------------------------------------------------------
    def create_widget(self):
        self.widget = wx.html.HtmlWindow(self.parent_widget())

    def init_attributes(self):
        self.set_page_source(self.source)

    def init_meta_handlers(self):
        pass

    #---------------------------------------------------------------------------
    # Notification
    #---------------------------------------------------------------------------
    def _source_changed(self, source):
        self.set_page_source(source)

    #---------------------------------------------------------------------------
    # Widget update
    #---------------------------------------------------------------------------
    def set_page_source(self, source):
        self.widget.SetPage(source)

