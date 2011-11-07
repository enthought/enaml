import wx

from .wx_component import WXComponent

from ..container import AbstractTkContainer


class WXContainer(WXComponent, AbstractTkContainer):
    """ A wxPython implementation of Container.

    WXContainer is usually to be used as a base class for other container
    widgets. However, it may also be used directly as an undecorated container
    for widgets for layout purposes.

    """
    def bind(self):
        """Bind the widget to the wx.EVT_SIZE.

        """
        super(WXContainer, self).bind()
        widget = self.widget
        widget.Bind(wx.EVT_SIZE, self.on_resize)

    def size_hint(self):
        """ Return default value (-1,-1) as a size hint for the generic
        containers in wx backend.

        """
        return (-1, -1)

