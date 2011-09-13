import wx.html

from traits.api import implements, Instance

from .wx_control import WXControl, WXControlStyleHandler
from .styling import wx_color_from_color

from ..html import IHtmlImpl

from ...style_converters import color_from_color_style


class WXHtmlStyleHandler(WXControlStyleHandler):

    widget = Instance(wx.html.HtmlWindow)

    def style_background_color(self, color_style):
        """ Overridden from the parent class to style the default
        bgcolor as white instead of the window color. The wx default
        is white but doesn't reset properly when using NullColor.

        """
        color = color_from_color_style(color_style)
        wx_color = wx_color_from_color(color, wx.WHITE)
        self.widget.SetBackgroundColour(wx_color)
        self.widget.Refresh()


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
        self.widget = wx.html.HtmlWindow(self.parent_widget(), size=(300, 200))

    def initialize_widget(self):
        """ Initializes the attributes of the control.

        """
        self.set_page_source(self.parent.source)

    def initialize_style(self):
        """ Initializes the style handler and style of the widget.

        """
        style_handler = WXHtmlStyleHandler(widget=self.widget)
        style = self.parent.style
        bgcolor = style.get_property('background_color')
        style_handler.style_background_color(bgcolor)
        style_handler.style_node = style
        self.style_handler = style_handler

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

