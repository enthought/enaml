#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_test_assistant import WXTestAssistant, skip_nonwindows

from .. import spin_box


@skip_nonwindows
class TestWxSpinBox(WXTestAssistant, spin_box.TestSpinBox):
    """ WXSpinBox tests. """

    def get_value(self, widget):
        """ Get a spin box's value.

        """
        return widget.GetValue()

    def get_low(self, widget):
        """ Get a spin box's minimum value.

        """
        return widget.GetLow()

    def get_high(self, widget):
        """ Get a spin box's maximum value.

        """
        return widget.GetHigh()

    def get_step(self, widget):
        """ Get a spin box's step size.

        """
        return widget.GetStep()

    def get_wrap(self, widget):
        """ Check if a spin box wraps around at the edge values.

        """
        return widget.GetWrap()

    def get_text(self, widget):
        """ Get the text displayed in a spin box.

        """
        return widget._value_string

    def spin_up_event(self, widget):
        """ Simulate a click on the 'up' spin button.

        """
        event = wx.SpinEvent(wx.EVT_SPIN_UP.typeId)
        widget.OnSpinUp(event)
        self.process_wx_events(wx.GetApp())

    def spin_down_event(self, widget):
        """ Simulate a click on the 'down' spin button.

        """
        event = wx.SpinEvent(wx.EVT_SPIN_DOWN.typeId)
        widget.OnSpinDown(event)
        self.process_wx_events(wx.GetApp())

