import wx

from traits.api import implements

from .wx_control import WXControl

from ..label import ILabelImpl


class WXLabel(WXControl):
    """ A wxPython implementation of ILabel.

    A WXLabel displays static text using a wx.StaticText control.

    See Also
    --------
    ILabel

    """
    implements(ILabelImpl)

 	#---------------------------------------------------------------------------
    # ILabelImpl interface 
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying text control.

        This is called by the 'layout' method and is not meant for 
        public consumption.

        """
        self.widget = wx.StaticText(self.parent_widget())

    def initialize_widget(self):
        """ Initializes the attributes on the underlying control.

        This is called by the 'layout' method and is not meant for 
        public consumption.

        """
        self.set_label(self.text)

    def parent_text_changed(self, text):
        """ The change handler for the 'text' attribute. Not meant for
        public consumption.

        """
        self.set_label(text)

    #---------------------------------------------------------------------------
    # Widget update
    #---------------------------------------------------------------------------
    def set_label(self, label):
        """ Sets the label on the underlying control. Not meant for
        public consumption.

        """
        self.widget.SetLabel(label)

