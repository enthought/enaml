import wx

from . import send_wx_event

from ..test_push_button import TestPushButton


class TestWxPushButton(TestPushButton):
    """ WXPushButton tests. """
    
    def test_button_pressed(self):
        """ Press the button programmatically.
        
        """
        send_wx_event(self.widget, wx.EVT_LEFT_DOWN)
        self.button_pressed()
    
    def test_button_released(self):
        """ Release the button programmatically.
        
        """
        widget = self.widget
        send_wx_event(widget, wx.EVT_LEFT_UP)
        send_wx_event(widget, wx.EVT_LEAVE_WINDOW)
        self.button_released()

    def test_button_clicked(self):
        """ Click the button programmatically.
        
        """
        send_wx_event(self.widget, wx.EVT_BUTTON)
        self.button_clicked()
        
    def test_button_down(self):
        """ Test the button's `down` attribute.
        
        """
        component = self.component
        widget = self.widget
        
        self.assertEqual(component.down, False)
        send_wx_event(widget, wx.EVT_LEFT_DOWN)
        self.assertEqual(component.down, True)
        send_wx_event(widget, wx.EVT_LEFT_UP)
        send_wx_event(widget, wx.EVT_LEAVE_WINDOW)
        self.assertEqual(component.down, False)

    def test_button_all_events(self):
        """ Simulate press, release, and click events.
        
        """
        widget = self.widget
        send_wx_event(widget, wx.EVT_LEFT_DOWN)
        send_wx_event(widget, wx.EVT_LEFT_UP)
        send_wx_event(widget, wx.EVT_BUTTON)
        self.button_all_events()
