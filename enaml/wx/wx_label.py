#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_constraints_widget import WxConstraintsWidget


class WxLabel(WxConstraintsWidget):
    """ A Wx implementation of an Enaml Label.

    """
    def create(self):
        """ Create the underlying widget.

        """
        self.widget = wx.StaticText(self.parent_widget)

    def initialize(self, attrs):
        """ Initialize the widget's attributes.

        """
        super(WxLabel, self).initialize(attrs)
        self.set_text(attrs['text'])

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_text(self, content):
        """ Handle the 'set_text' action from the Enaml widget.

        """
        # XXX trigger a relayout if the size hint has changed.
        self.set_text(content['text'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_text(self, text):
        """ Set the text in the underlying widget.

        """
        self.widget.SetLabel(text)

