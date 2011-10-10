#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_test_assistant import WXTestAssistant
from .. import spin_box


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

    def get_prefix(self, widget):
        """ Get a spin box's text prefix.

        """
        return widget.GetPrefix()

    def get_suffix(self, widget):
        """ Get a spin box's text suffix.

        """
        return widget.GetSuffix()

    def get_special_value_text(self, widget):
        """ Get a spin box's special value text, displayed at the minimum value.

        """
        return widget.GetSpecialValueText()

    def get_text(self, widget):
        """ Get the text displayed in a spin box.

        """
        value = widget.GetValue()
        return widget.ComputeValueString(value)

    def spin_up_event(self, widget):
        """ Simulate a click on the 'up' spin button.

        """
        event = wx.SpinEvent(wx.EVT_SPIN_UP.typeId)
        widget.GetEventHandler().ProcessEvent(event)
        self.process_wx_events(widget)

    def spin_down_event(self, widget):
        """ Simulate a click on the 'down' spin button.

        """
        event = wx.SpinEvent(wx.EVT_SPIN_DOWN.typeId)
        widget.GetEventHandler().ProcessEvent(event)
        self.process_wx_events(widget)
