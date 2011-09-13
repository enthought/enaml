import wx

from traits.api import implements, Instance

from .wx_component import WXComponent
from .styling import wx_color_from_color

from ..control import IControlImpl

from ...style_sheet import StyleHandler
from ...style_converters import color_from_color_style


class WXControlStyleHandler(StyleHandler):

    widget = Instance(wx.Window)

    def style_background_color(self, color_style):
        color = color_from_color_style(color_style)
        wx_color = wx_color_from_color(color)
        self.widget.SetBackgroundColour(wx_color)
        self.widget.Refresh()

    def style_color(self, color_style):
        color = color_from_color_style(color_style)
        wx_color = wx_color_from_color(color)
        self.widget.SetForegroundColour(wx_color)
        self.widget.Refresh()


class WXControl(WXComponent):

    implements(IControlImpl)

    style_handler = Instance(WXControlStyleHandler)

    #---------------------------------------------------------------------------
    # IControlImpl interface
    #---------------------------------------------------------------------------
    def initialize_style(self):
        style_handler = WXControlStyleHandler(widget=self.widget)
        style = self.parent.style
        bgcolor = style.get_property('background_color')
        style_handler.style_background_color(bgcolor)
        style_handler.style_node = style
        self.style_handler = style_handler
        
    def layout_child_widgets(self):
        """ Ensures that the control does not contain children. Special
        control subclasses that do allow for children should reimplement
        this method.

        """
        if list(self.child_widgets()):
            raise ValueError('Standard controls cannot have children.')

