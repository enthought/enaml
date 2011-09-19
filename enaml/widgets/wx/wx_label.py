#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from traits.api import implements

from .wx_control import WXControl

from ..label import ILabelImpl


class WXLabel(WXControl):
    """ A wxPython implementation of Label.

    A WXLabel displays static text using a wx.StaticText control.

    See Also
    --------
    Label

    """
    implements(ILabelImpl)

    #---------------------------------------------------------------------------
    # ILabelImpl interface 
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying text control.

        """
        self.widget = widget = wx.StaticText(self.parent_widget())
        widget.SetDoubleBuffered(True)
        
    def initialize_widget(self):
        """ Initializes the attributes on the underlying control.

        """
        self.set_label(self.parent.text)

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

