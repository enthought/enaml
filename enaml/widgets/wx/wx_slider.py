#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import warnings

import wx

from traits.api import implements, Enum, TraitError, Float

from .wx_control import WXControl

from ..slider import ISliderImpl

from ...enums import Orientation, TickPosition

SLIDER_MAX = 10000

# A map from Enaml constants to wxSlider TickPosition values to simulate
# the behaviour of QSlider
HOR_TICK_POS_MAP = {TickPosition.TOP: wx.SL_TOP,
                     TickPosition.BOTTOM: wx.SL_BOTTOM,
                     TickPosition.BOTH: wx.SL_BOTH}

VERT_TICK_POS_MAP = {TickPosition.LEFT: wx.SL_LEFT,
                    TickPosition.RIGHT: wx.SL_RIGHT,
                    TickPosition.BOTH: wx.SL_BOTH}

ADAPT_HOR_TICK = {TickPosition.LEFT: TickPosition.TOP,
                  TickPosition.RIGHT: TickPosition.BOTTOM}

ADAPT_VERT_TICK = {TickPosition.TOP: TickPosition.LEFT,
                  TickPosition.BOTTOM: TickPosition.RIGHT}


class WXSlider(WXControl):
    """ A wxPython implementation of Slider.

    The WXSlider uses the wx.Slider control.

    See Also
    --------
    Slider

    """
    implements(ISliderImpl)

    #---------------------------------------------------------------------------
    # ISliderImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """Initialisation of ISlider based on wxWidget

        The method creates the wxPython Slider widget and binds the ui events
        to WXSlider.

        """
        widget = wx.Slider(parent=self.parent_widget())
        self.widget = widget

    def initialize_widget(self):
        """ Initializes the attributes of the toolkit widget.

        """
        parent = self.parent
        parent._down = False

        # We hard-coded range for the widget since we are managing the
        # conversion.
        self.set_range(parent.minimum, parent.maximum)
        self.set_position(parent.value)
        self.set_orientation(parent.orientation)
        self.set_tick_position(parent.tick_position)
        self.set_tick_frequency(parent.tick_interval)
        self.set_single_step(parent.single_step)
        self.set_page_step(parent.page_step)
        self.set_tracking(parent.tracking)

        self.bind()

    def parent__minimum_changed(self, minimum):
        """ Update the slider when the converter class changes.

        """
        parent = self.parent
        self.set_range(minimum, parent.maximum)

    def parent__maximum_changed(self, maximum):
        """ Update the slider when the converter class changes.

        """
        parent = self.parent
        self.set_range(parent.minimum, maximum)

    def parent_value_changed(self, value):
        """ Update the slider position.

        """
        parent = self.parent
        self.set_position(value)
        self.parent.moved = value

    def parent_tracking_changed(self, tracking):
        """ Set the tracking event in the widget.

        """
        self.set_tracking(tracking)

    def parent_single_step_changed(self, single_step):
        """ Update the the line step in the widget.

        """
        self.set_single_step(single_step)

    def parent_page_step_changed(self, page_step):
        """ Update the widget due to change in the line step.

        """
        self.set_page_step(page_step)

    def parent_tick_interval_changed(self, tick_interval):
        """ Update the tick marks interval.

        """
        parent = self.parent
        self.set_tick_frequency(tick_interval)
        self.set_single_step(parent.single_step)
        self.set_page_step(parent.page_step)

    def parent_tick_position_changed(self, tick_position):
        """ Update the widget due to change in the tick position

        The method ensures that the tick position style can be applied
        and reverts to the last value if the request is invalid.

        """
        self.set_tick_position(tick_position)

    def parent_orientation_changed(self, orientation):
        """ Update the widget due to change in the orientation attribute

        The method applies the orientation style and fixes the tick position
        option if necessary.

        """
        self.set_orientation(orientation)
        # FIXME: we need to relayout the widget in order to make space for the
        # ticks.
        self.widget.GetParent().Layout()

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def bind(self):
        """ Binds the event handlers for the slider widget.

        Individual event binding was preferred instead of events that
        are platform specific (e.g. wx.EVT_SCROLL_CHANGED) or group
        events (e.g. wx.EVT_SCROLL), to facilitate finer control on
        the behaviour of the widget.

        """
        widget = self.widget
        widget.Bind(wx.EVT_SCROLL_TOP, self._on_slider_changed)
        widget.Bind(wx.EVT_SCROLL_BOTTOM, self._on_slider_changed)
        widget.Bind(wx.EVT_SCROLL_LINEUP, self._on_slider_changed)
        widget.Bind(wx.EVT_SCROLL_LINEDOWN, self._on_slider_changed)
        widget.Bind(wx.EVT_SCROLL_PAGEUP, self._on_slider_changed)
        widget.Bind(wx.EVT_SCROLL_PAGEDOWN, self._on_slider_changed)
        widget.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        widget.Bind(wx.EVT_LEFT_UP, self._on_thumb_released)

    def _on_slider_changed(self, event):
        """ Respond to change in value from the ui.

        """
        parent = self.parent
        new_value = self.get_position()
        parent.value = new_value
        event.Skip()

    def _on_thumb_track(self, event):
        """ Update `slider_pos` when the thumb is dragged.

        The value attribute is updated during a dragging if the
        self.tracking attribute is True. This will also fire a moved
        event for every change. The event is not skipped.

        """
        self._on_slider_changed(event)

    def _on_left_down(self, event):
        """ Update if the left button was pressed.

        Estimates the position of the thumb and then checks if the mouse
        was pressed over it to fire the `pressed` event and sets the
        `down` attribute.

        """
        parent = self.parent
        mouse_position = event.GetPosition()
        if self.is_thumb_hit(mouse_position):
            parent._down = True
            parent.pressed = True
        event.Skip()

    def _on_thumb_released(self, event):
        """ Update if the left button was released

        """
        parent = self.parent
        if parent._down:
            parent._down = False
            parent.released = True
            parent.value = self.get_position()
        event.Skip()

    def set_single_step(self, step):
        """ Set the single step attribute in the wx widget.

        Arguments
        ---------
        step: int
            the number of steps to move the slider when the user uses the
            arrow keys.

        """
        self.widget.SetLineSize(step)

    def set_page_step(self, step):
        """ Set the page step attribute in the wx widget.

        Arguments
        ---------
        step: int
            The number of steps to move the slider when the user uses the
            page-up / page-down key. This is also used when the user
            clicks on the left or the right of the thumb.

        """
        self.widget.SetPageSize(step)

    def set_tick_position(self, ticks):
        """ Apply the tick position in the widget.

        Arguments
        ---------
        ticks : TickPosition
            The tick position

        """
        parent = self.parent
        widget = self.widget
        style = widget.GetWindowStyle()
        style &= ~(wx.SL_TOP | wx.SL_BOTTOM | wx.SL_LEFT |
                   wx.SL_RIGHT | wx.SL_BOTH | wx.SL_AUTOTICKS |
                   wx.SL_TICKS)

        if parent.orientation == Orientation.VERTICAL:
            if ticks in ADAPT_VERT_TICK:
                parent.tick_position = ADAPT_VERT_TICK[ticks]
                return

            if ticks in VERT_TICK_POS_MAP:
                style |= VERT_TICK_POS_MAP[ticks] | wx.SL_AUTOTICKS
        else:
            if ticks in ADAPT_HOR_TICK:
                parent.tick_position = ADAPT_HOR_TICK[ticks]
                return

            if ticks in HOR_TICK_POS_MAP:
                style |= HOR_TICK_POS_MAP[ticks] | wx.SL_AUTOTICKS

        widget.SetWindowStyle(style)
        # FIXME: there is a problem with the wxSlider where some times the tick
        # interval needs to be applied again for it to appear properly
        widget.SetTickFreq(parent.tick_interval)

    def set_orientation(self, orientation):
        """ Set the slider orientation

        Arguments
        ---------
        orientation : Orientation
            The orientation of the slider.

        """
        widget = self.widget
        parent = self.parent


        tick_position = parent.tick_position
        style = widget.GetWindowStyle()
        style &= ~(wx.SL_HORIZONTAL | wx.SL_VERTICAL)

        if orientation == Orientation.VERTICAL:
            style |= wx.SL_VERTICAL
        else:
            style |= wx.SL_HORIZONTAL

        widget.SetWindowStyle(style)
        self.set_tick_position(parent.tick_position)

    def set_tracking(self, tracking):
        """ Bind/Unbind the trakcing event

        Arguments
        ---------
        tracking : boolean
            When true the event is bound to the enaml class

        """
        if tracking:
            self.widget.Bind(wx.EVT_SCROLL_THUMBTRACK, self._on_thumb_track)
        else:
            self.widget.Unbind(wx.EVT_SCROLL_THUMBTRACK)

    def set_range(self, minimum, maximum):
        """ Set the slider widget range

        Arguments
        ---------
        minimum : int
            The minimum value

        maximum : int
            The maximum value

        """
        self.widget.SetRange(minimum, maximum)

    def set_tick_frequency(self, interval):
        """ Set the slider widget tick marg fequency

        Arguments
        ---------
        interval : int
            The interval in slider units between ticks.

        """
        self.widget.SetTickFreq(interval)

    def set_position(self, value):
        """ set the position value.

        """
        self.widget.SetValue(value)

    def get_position(self):
        """ Get the slider position from the widget.

        If error occurs during the conversion it is recorded in the
        `error` and `exception` attributes. The return value in that case
        is None since the value is undefined.

        """
        return  self.widget.GetValue()

    def is_thumb_hit(self, point):
        """ Is the point in the thumb area.

        Arguments
        ---------
        point : tuple (x,y)
            The point in the widget pixel coordinates.

        Returns
        -------
        result : boolean
            True if the point is inside the thumb area.

        .. note:: The current implementation is not very accurate. The native
            slider widget that is wrapped by wxWidgets places a default border
            between the edges. Thus the thumb hit is out by a few pixels.

        """
        widget = self.widget

        thumb = widget.GetThumbLength() / 2.0
        # FIXME: get e better estimate of the actual size of the slider
        width, height = widget.GetClientSizeTuple()

        if widget.HasFlag(wx.SL_VERTICAL):
            position = point[1] / float(height)
        else:
            position = point[0] / float(width)

        slider_position = widget.GetValue()
        slider_length = float(widget.GetMax() - widget.GetMin()) + 1.0

        minimum = (slider_position - thumb) / slider_length
        maximum = (slider_position + thumb) / slider_length


        return (minimum <= position <= maximum)
