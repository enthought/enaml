#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from unittest import expectedFailure
import wx

from .wx_test_assistant import WXTestAssistant, skip_nonwindows

from .. import slider


# A map from wxSlider constants to Enaml TickPosition values.
TICK_POS_MAP = {wx.SL_BOTTOM: 'bottom',
                wx.SL_LEFT: 'left' ,
                wx.SL_RIGHT: 'right',
                wx.SL_TOP: 'top',
                wx.SL_BOTTOM: 'bottom',
                wx.SL_BOTH: 'both',
                wx.SL_TICKS: 'Ticks'}

# A map from Wx constants to Enaml enums for horizontal or vertical orientation.
ORIENTATION_MAP = {wx.SL_HORIZONTAL: 'horizontal',
                   wx.SL_VERTICAL: 'vertical'}

# Map event actions to WX constants
EVENT_MAP = {slider.TestEvents.PRESSED: wx.EVT_LEFT_DOWN,
             slider.TestEvents.RELEASED: wx.EVT_LEFT_UP,
             slider.TestEvents.HOME: wx.EVT_SCROLL_BOTTOM,
             slider.TestEvents.END: wx.EVT_SCROLL_TOP,
             slider.TestEvents.STEP_UP: wx.EVT_SCROLL_LINEUP,
             slider.TestEvents.STEP_DOWN: wx.EVT_SCROLL_LINEDOWN,
             slider.TestEvents.PAGE_UP: wx.EVT_SCROLL_PAGEUP,
             slider.TestEvents.PAGE_DOWN: wx.EVT_SCROLL_PAGEDOWN}


@skip_nonwindows
class TestWXSlider(WXTestAssistant, slider.TestSlider):
    """ QtLabel tests. """

    def setUp(self):
        """ Setup the slider testing based on the wx backend.

        Special care is needed because we need to have a specific size
        of the wx slider in order to properly check the firing of the
        pressed thumb event.

        """
        super(TestWXSlider, self).setUp()
        self.widget.SetSize(wx.Size(200,20))

    # This test fails on windows under wx because the underlying size of the
    # of the widget is not reliable. So the precomputed mouse position for
    # the mouse event which is sent can be wrong.
    @expectedFailure
    def test_releasing_the_thumb(self):
        super(TestWXSlider, self).test_relleasing_the_thumb(self)

    def get_value(self, widget):
        """ Get a slider's position.

        """
        return widget.GetValue()

    def get_minimum(self, widget):
        """ Get the Slider's minimum value.

        """
        return widget.GetMin()

    def get_maximum(self, widget):
        """ Get the Slider's maximum value.

        """
        return widget.GetMax()

    def get_tick_interval(self, widget):
        """ Get the Slider's tick_interval value.

        """
        return widget.GetTickFreq()

    def get_tick_position(self, widget):
        """ Get the Slider's tick position style.

        Assertion errors are raised when it is not posible to estimate the
        tick positiosn.

        """
        style = widget.GetWindowStyle()
        flags = []
        for flag in TICK_POS_MAP.keys():
            if flag & style:
                flags.append(TICK_POS_MAP[flag])

        number_of_flags = len(flags)
        if number_of_flags == 0:
            return 'no_ticks'
        elif number_of_flags == 1:
            self.fail('The tick position style is expected to have at least'
                      ' two style bits set when the ticks are visible')
        elif number_of_flags == 2:
            self.assertIn('Ticks', flags, 'When the ticks are visible'
                      ' the position style is expected to have the wx.SL_TICKS'
                      ' bit set')
            flags.pop(flags.index('Ticks'))
        else:
            self.fail('More than two tick position style flags are set')

        return flags[0]

    def get_orientation(self, widget):
        """ Get the Slider's orientation.

        """
        style = widget.GetWindowStyle()
        flags = []
        for flag in ORIENTATION_MAP.keys():
            if flag & style:
                flags.append(ORIENTATION_MAP[flag])

        number_of_flags = len(flags)

        if number_of_flags == 0:
            self.fail('Orientation should be always set in the widget')
        elif number_of_flags > 1:
            self.fail('More than one orientation style flags are set')

        return flags[0]

    def get_single_step(self, widget):
        """ Get the Slider's single step value.

        """
        return widget.GetLineSize()

    def get_page_step(self, widget):
        """ Get the Slider's page step value.

        """
        return widget.GetPageSize()

    def get_tracking(self, widget):
        """ Get the Slider's tracking status.

        """
        return self.component.tracking

    def send_event(self, widget, event):
        """ Send an event to the Slider programmatically.

        Arguments
        ---------
        widget :
            The widget to sent the event to.

        event :
            The desired event to be proccessed.

        """
        event_type = EVENT_MAP[event]
        if  event_type in (wx.EVT_LEFT_DOWN, wx.EVT_LEFT_UP):
            position = wx.Point(100,10)
            self.send_wx_mouse_event(widget, event_type, position=position)
        else:
            value = widget.GetValue()
            if event_type == wx.EVT_SCROLL_BOTTOM:
                value = widget.GetMin()
            elif event_type == wx.EVT_SCROLL_TOP:
                value = widget.GetMax()
            elif event_type == wx.EVT_SCROLL_LINEUP:
                value += widget.GetLineSize()
            elif event_type == wx.EVT_SCROLL_LINEDOWN:
                value -= widget.GetLineSize()
            elif event_type == wx.EVT_SCROLL_PAGEUP:
                value += widget.GetPageSize()
            elif event_type == wx.EVT_SCROLL_PAGEDOWN:
                value -= widget.GetPageSize()

            widget.SetValue(value)
            event = wx.ScrollEvent(event_type.typeId, widget.GetId())
            widget.GetEventHandler().ProcessEvent(event)
        self.process_wx_events(self.app)
