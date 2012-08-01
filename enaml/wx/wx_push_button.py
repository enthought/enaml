#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_abstract_button import WxAbstractButton


class WxPushButton(WxAbstractButton):
    """ A Wx implementation of the Enaml PushButton.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying wx.Button control.

        """
        self.widget = wx.Button(self.parent_widget)

    def initialize(self, attrs):
        """ Intializes the attributes of the widget and binds the event
        handlers.
        
        """
        super(WxPushButton, self).initialize(attrs)
        self.set_text(self.shell_obj.text)
        widget = self.widget
        widget.Bind(wx.EVT_BUTTON, self.on_clicked)

    #--------------------------------------------------------------------------
    # Abstract API Implementation 
    #--------------------------------------------------------------------------
    def set_checkable(self, checkable):
        """ Sets whether or not the widget is checkable.

        """
        # XXX ignore this for now, wx has a completely separate control
        # wx.ToggleButton for handling this, that we'll need to swap
        # out dynamically.
        pass

    def get_checked(self):
        """ Returns the checked state of the widget.

        """
        return False

    def set_checked(self, checked):
        """ Sets the widget's checked state with the provided value.

        """
        pass

