import wx

from traits.api import implements, Str

from .wx_element import WXElement
from ..i_label import ILabel


class WXLabel(WXElement):
    """ A wxPython implementation of ILabel.

    Attributes
    ----------
    text : Str
        The text in the label.

    See Also
    --------
    ILabel

    """
    implements(ILabel)

 	#===========================================================================
    # ILabel interface 
    #===========================================================================
    text = Str

    #===========================================================================
    # Implementation
    #===========================================================================

    #---------------------------------------------------------------------------
    # Initialization
    #---------------------------------------------------------------------------
    def create_widget(self, parent):
        self.widget = wx.StaticText(self.parent_widget())

    def init_attributes(self):
        self.set_label(self.text)

    def init_meta_handlers(self):
        pass

    #---------------------------------------------------------------------------
    # Notification
    #---------------------------------------------------------------------------
    def _text_changed(self, text):
        self.set_label(text)

    #---------------------------------------------------------------------------
    # Widget update
    #---------------------------------------------------------------------------
    def set_label(self, label):
        self.widget.SetLabel(label)

