#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_control import WXControl

from ..push_button import AbstractTkPushButton


class WXPushButton(WXControl, AbstractTkPushButton):
    """ A wxPython implementation of PushButton.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying wx.Button control.

        """
        self.widget = wx.Button(parent)

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(WXPushButton, self).initialize()
        self.set_label(self.shell_obj.text)

    def bind(self):
        """ Binds the event handlers for the push button.

        """
        super(WXPushButton, self).bind()
        widget = self.widget
        widget.Bind(wx.EVT_BUTTON, self.on_clicked)
        widget.Bind(wx.EVT_LEFT_DOWN, self.on_pressed)
        widget.Bind(wx.EVT_LEAVE_WINDOW, self.on_released)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def shell_text_changed(self, text):
        """ The change handler for the 'text' attribute.

        """
        self.set_label(text)
        # If the text of the button changes, the size hint has likely
        # change and the layout system needs to be informed.
        self.shell_obj.size_hint_updated()

    def on_clicked(self, event):
        """ The event handler for the button's clicked event.

        """
        shell = self.shell_obj
        shell._down = False
        shell.clicked()
        event.Skip()

    def on_pressed(self, event):
        """ The event handlers for the button's pressed event.

        """
        shell = self.shell_obj
        shell._down = True
        shell.pressed()
        event.Skip()

    def on_released(self, event):
        """ The event handler for the button's leave window event.

        """
        # The wxButton doesn't emit an EVT_LEFT_UP even though it
        # emits an EVT_LEFT_DOWN. So in order to reset the down
        # flag when the mouse leaves the button and then releases,
        # we need to hook the EVT_LEAVE_WINDOW
        shell = self.shell_obj
        if shell._down:
            shell._down = False
            shell.released()
        event.Skip()

    def set_label(self, label):
        """ Sets the label on the button control.

        """
        self.widget.SetLabel(label)

