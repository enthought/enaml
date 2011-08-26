from traits.api import implements, Str

import wx

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

    # IHtml interface
    html = Str

    # Notification methods
    def _html_changed(self):
        self.widget.SetPage(self.html)


