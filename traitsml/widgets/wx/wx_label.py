import wx

from traits.api import implements, Str

from .wx_element import WXElement

from ..i_label import ILabel

class WXLabel(WXElement):
    """ A wxWidgets implementation of ILabel.

    Attributes
    ----------
    text : Str
        The text in the label.

    
    See Also
    --------
    ILabel

    """
    implements(ILabel)

 	#--------------------------------------------------------------------------
    # ILabel interface
    #--------------------------------------------------------------------------
    text = Str

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def create_widget(self, parent):
        self.widget = wx.StaticText(parent.widget)

    def init_attributes(self):
        self.widget.SetLabel(self.text)

    def init_meta_handlers(self):
        pass

    def _text_changed(self, text):
        self.widget.SetLabel(text)