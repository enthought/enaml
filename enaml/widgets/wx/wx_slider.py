# -*- coding: utf-8 -*-
import warnings

import wx
from traits.api import (implements, Bool, Event, Str, Enum, Float, Any,
                        Range, Callable, TraitError)

from .wx_element import WXElement
from ..i_slider import ISlider
from ...enums import Orientation, TickPosition


class WXSlider(WXElement):
    """A simple slider widget.

    A slider can be used to select from a continuous range of values.
    The slider's range is fixed at 0.0 to 1.0. Therefore, the position
    of the slider can be viewed as a percentage. To facilitate various
    ranges, you can specify from_pos and to_pos callables to convert to
    and from the position the value.

    Attributes
    ----------
    down : Bool
        Whether or not the slider is pressed down.

    from_slider : Callable
        A function that takes one argument to convert from the slider
        position to the appropriate Python value.

    to_slider : Callable
        A function that takes one argument to convert from a Python
        value to the appropriate slider position.

    slider_pos : Float
        The floating point percentage (0.0 - 1.0) which is the position
        of the slider. This value is always updated while the slider is
        moving.

    value : Any
        The value of the slider. This is set to the value of
        from_slider(slider_pos).

    tracking : Bool
        If True, the value is updated while sliding. Otherwise, it is
        only updated when the slider is released. Defaults to True.

    tick_interval : Float
        The slider_pos interval to put between tick marks. Default is `0.1`.

    ticks : TickPosition Enum value
        A TickPosition enum value indicating how to display the tick
        marks. Please note that the orientation takes precedence over the
        tick mark position and if for example the user sets the tick to an
        invalid value it is ignored. The ticks option BOTH is not supported yet
        in the wx widget, and will be also ingored.

    orientation : Orientation Enum value
        The orientation of the slider. The default orientation is horizontal.
        When the orientation is flipped the tick positions (if set) also adapt
        to reflect the changes  (e.g. the LEFT becomes TOP when the orientation
        becomes horizontal).

    pressed : Event
        Fired when the slider is pressed.

    released : Event
        Fired when the slider is released.

    moved : Event
        Fired when the slider is moved.

    invalid_value: Event
        Fired when there was an attempt to assign an invalid (out of range)
        value to the slider.

    .. note:: The slider enaml widget changes the attributes and fires the
        necessary events in sequence based on their priority as given below
        (from highest to lowest):

            # update `slider_pos` (when changed by the ui) or `value` (when
              changed programmatically).
            # fire `invalid_value`.
            # fire `moved`.
            # update `down`.
            # fire pressed.
            # fire released.

    """

    implements(ISlider)

    #--------------------------------------------------------------------------
    # ISlider interface
    #--------------------------------------------------------------------------

    down = Bool

    from_slider = Callable(lambda pos: pos)

    to_slider = Callable(lambda val: val)

    slider_pos = Range(0.0, 1.0)

    value = Any

    tracking = Bool(True)

    tick_interval = Float(0.1)

    ticks = Enum(*TickPosition.values())

    orientation = Enum(*Orientation.values())

    pressed = Event

    released = Event

    moved = Event

    invalid_value = Event

    #==========================================================================
    # Implementation
    #==========================================================================

    def create_widget(self):
        """Initialization of ISlider based on wxWidget

        The method create the wxPython Slider widget and binds the ui events
        to WXSlider. Individual event binding was preferred instead of events
        that are platform specific (e.g. wx.EVT_SCROLL_CHANGED) or group
        events (e.g. wx.EVT_SCROLL), to facilitate finer control on the
        behaviour of the widget.
        """
        # create widget
        widget = wx.Slider(parent=self.parent_widget())

        # Bind class functions to wx widget events

        # We treat the top, bottom and track events in their own way
        widget.Bind(wx.EVT_SCROLL_THUMBTRACK, self._on_thumb_track)

        # Generic events
        widget.Bind(wx.EVT_SCROLL_TOP, self._on_slider_changed)
        widget.Bind(wx.EVT_SCROLL_BOTTOM, self._on_slider_changed)
        widget.Bind(wx.EVT_SCROLL_LINEUP, self._on_slider_changed)
        widget.Bind(wx.EVT_SCROLL_LINEDOWN, self._on_slider_changed)
        widget.Bind(wx.EVT_SCROLL_PAGEUP, self._on_slider_changed)
        widget.Bind(wx.EVT_SCROLL_PAGEDOWN, self._on_slider_changed)

        # Capture mouse events for pressed and released left button
        widget.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        widget.Bind(wx.EVT_LEFT_UP, self._on_left_up)

        # associate widget
        self.widget = widget

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------

    def init_attributes(self):
        """initialize WXSlider attributes"""

        # down
        self.down = False

        minimum = self._convert_for_wx(0.0)
        maximum = self._convert_for_wx(1)
        self.widget.SetRange(minimum, maximum)

        # slider position
        self.value = self.from_slider(self.slider_pos)

        # orientation
        self._apply_orientation(self.orientation)
        # ticks
        self._apply_tick_position(self.ticks)

        return

    def init_meta_handlers(self):
        """initialize WXSlider meta styles"""
        return

    #--------------------------------------------------------------------------
    # Private methods
    #--------------------------------------------------------------------------

    def _convert_for_wx(self, value):
        """Converts the value to an integer suitable for the wxSlider"""
        position = int(round(value / self.tick_interval))
        return position

    def _convert_from_wx(self, value):
        """Converts the value to an integer suitable for the wxSlider"""
        position = value * self.tick_interval
        return position

    def _apply_tick_position(self, value):
        """Converts the `ticks` position into style flags"""

        if self.orientation == Orientation.VERTICAL:
            style = wx.SL_VERTICAL
            if value == TickPosition.LEFT:
                style |= wx.SL_LEFT | wx.SL_AUTOTICKS
            elif value == TickPosition.RIGHT:
                style |= wx.SL_RIGHT | wx.SL_AUTOTICKS
            elif value == TickPosition.BOTH:
                warnings.warn('Option not implemented in wxPython')
            elif value == TickPosition.NO_TICKS:
                pass
            else:
                style |= wx.SL_AUTOTICKS

        else:
            style = wx.SL_HORIZONTAL
            if value == TickPosition.TOP:
                style |= wx.SL_TOP | wx.SL_AUTOTICKS
            elif value == TickPosition.BOTTOM:
                style |= wx.SL_BOTTOM | wx.SL_AUTOTICKS
            elif value == TickPosition.BOTH:
                warnings.warn('Option not implemented in wxPython')
            elif value == TickPosition.NO_TICKS:
                style = wx.SL_HORIZONTAL
            else:
                style |= wx.SL_AUTOTICKS

        self.widget.SetWindowStyle(style)

        return

    def _apply_orientation(self, value):
        """Converts the `orientation` into style flags"""

        if self.widget.HasFlag(wx.SL_AUTOTICKS):
            style = wx.SL_AUTOTICKS
        else:
            style = 0

        if value == Orientation.VERTICAL:
            if self.widget.HasFlag(wx.SL_TOP):
                style |= wx.SL_LEFT

            elif self.widget.HasFlag(wx.SL_BOTTOM):
                style |= wx.SL_RIGHT

            style |= wx.SL_VERTICAL

        else:
            if self.widget.HasFlag(wx.SL_LEFT):
                style |= wx.SL_TOP

            elif self.widget.HasFlag(wx.SL_RIGHT):
                style |= wx.SL_BOTTOM

            style |= wx.SL_HORIZONTAL

        self.widget.SetWindowStyle(style)

        return

    def _thumb_hit(self, point):
        """Is the point in the thumb area"""

        # the relative position of the mouse
        width, height = [float(x) for x in self.widget.GetClientSizeTuple()]
        if self.orientation == Orientation.VERTICAL:
            mouse = point[1] / height
            thumb = self.widget.GetThumbLength() / height
        else:
            mouse = point[0] / width
            thumb = self.widget.GetThumbLength() / width

        # minimum and maximum position (edges) of the thumb
        minimum = self.slider_pos - thumb
        maximum = self.slider_pos + thumb

        return minimum <= mouse <= maximum

    #--------------------------------------------------------------------------
    # Notification
    #--------------------------------------------------------------------------

    def _value_changed(self):
        """Update the slider position

        Update the `slider_pos` to respond to the `value` change. The
        assignment to the slider_pos might fail because 'value' is out of
        range. In that case the last known good value is given back to the
        value attribute, because we need to keep the `value` attribute in
        sync with the `slider_pos` and **valid**
        """
        # The try...except block is required because we need to keep the
        # `value` attribute in sync with the `slider_pos` and **valid**
        try:
            self.slider_pos = self.to_slider(self.value)
        except TraitError as ex:
            # revert value
            self.value = self.from_slider(self.slider_pos)
            self.invalid_value = ex
        return

    def _slider_pos_changed(self):
        """Update the position in the slider widget

        there are a lot of conversions taking place due to the three
        different variables (value, slider.pos, widget value) that need to
        be in sync.

        .. note:: The wx widget uses integers for the slider range. This
            requires to convert the decimal values in the `slider_pos`
            attribute to an integer.
        """

        # check and update the wxSlider
        position = self._convert_for_wx(self.slider_pos)
        if position != self.widget.GetValue():
            self.widget.SetValue(position)

        self.value = self.from_slider(self.slider_pos)
        self.moved = self.value
        return

    def _orientation_changed(self):
        """Update the widget due to change in the orientation attribute"""
        self._apply_orientation(self.orientation)
        return

    def _ticks_changed(self):
        """Update the widget due to change in the orientation attribute"""
        self._apply_tick_position(self.ticks)
        return

    #--------------------------------------------------------------------------
    # Event handlers
    #--------------------------------------------------------------------------

    def _on_slider_changed(self, event):
        """Respond to a (possible) change in value from the ui.

        Updated the value of the slider_pos based on the possible change from
        the wxwidget. The `slider_pos` trait will fire the moved event only if
        the value has changed"""

        new_position = self.widget.GetValue()
        self.slider_pos = self._convert_from_wx(new_position)
        event.Skip()
        return

    def _on_thumb_track(self, event):
        """Update `slider_pos` when the thumb is dragged.

        The slider_pos attribute is updated during a dragging if the
        self.tracking attribute is True. This will also fire a moved event
        for a very change.

        The event is not skiped
        """
        if self.tracking:
            self._on_slider_changed(event)
        return

    def _on_left_down(self, event):
        """Check if the mouse was pressed over the thumb

        Estimates the position of the thumb and then checks if the mouse was
        pressed over it to fire the `pressed` event and sets the `down`
        attribute.
        """
        mouse_position = event.GetPosition()
        if self._thumb_hit(mouse_position):
            self.down = True
            self.pressed = event
        event.Skip()
        return

    def _on_left_up(self, event):
        """Update if the left button was released

        Checks if the `down` attribute was set. In that case the function calls
        the `_on_slider_changed` function, fires the release event and sets the
        `down` attribute to false.
        """
        if self.down:
            self._on_slider_changed(event)
            self.down = False
            self.released = event

        event.Skip()
        return

