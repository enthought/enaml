#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from traits.api import implements

from .wx_control import WXControl

from ..push_button import IPushButtonImpl


class WXPushButton(WXControl):
    """ A wxPython implementation of PushButton.

    WXPushButton uses a wx.Button control.

    See Also
    --------
    PushButton

    """
    implements(IPushButtonImpl)

    #---------------------------------------------------------------------------
    # IPushButtonImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying wx.Button control.

        """
        self.widget = widget = wx.Button(self.parent_widget())
        widget.SetDoubleBuffered(True)
        
    def initialize_widget(self):
        """ Intializes the widget with the attributes of this instance.

        """
        self.set_label(self.parent.text)
        self.bind()

    def parent_text_changed(self, text):
        """ The change handler for the 'text' attribute. Not meant for
        public consumption.

        """
        self.set_label(text)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def bind(self):
        """ Binds the event handlers for the push button.

        """
        widget = self.widget
        widget.Bind(wx.EVT_BUTTON, self.on_clicked)
        widget.Bind(wx.EVT_LEFT_DOWN, self.on_pressed)
        widget.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_window)

    def on_clicked(self, event):
        """ The event handler for the button's clicked event. Not meant
        for public consumption.

        """
        parent = self.parent
        parent._down = False
        parent.clicked = True
        event.Skip()

    def on_pressed(self, event):
        """ The event handlers for the button's pressed event. Not meant
        for public consumption.

        """
        parent = self.parent
        parent._down = True
        parent.pressed = True
        event.Skip()

    def on_leave_window(self, event):
        """ The event handler for the button's leave window event. Not
        meant for public consumption.

        """
        # The wxButton doesn't emit an EVT_LEFT_UP even though it 
        # emits an EVT_LEFT_DOWN (ugh!) So in order to reset the down 
        # flag when the mouse leaves the button and then releases,
        # we need to hook the EVT_LEAVE_WINDOW 
        parent = self.parent
        if parent._down:
            parent._down = False
            parent.released = True
        event.Skip()

    def set_label(self, label):
        """ Sets the label on the button control. Not meant for public
        consumption.

        """
        self.widget.SetLabel(label)

