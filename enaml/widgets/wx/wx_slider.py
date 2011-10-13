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
        self.widget = widget = wx.Slider(parent=self.parent_widget())
        widget.SetDoubleBuffered(True)

    def initialize_widget(self):
        """ Initializes the attributes of the toolkit widget.

        """
        parent = self.parent
        parent._down = False

        # We hard-coded range for the widget since we are managing the
        # conversion.
        self.set_range(0, SLIDER_MAX)
        self.set_position(parent.value)
        self.set_orientation(parent.orientation)
        self.set_tick_position(parent.tick_position)
        self.set_tick_frequency(parent.tick_interval)
        self.set_single_step(parent.single_step)
        self.set_page_step(parent.page_step)
        self.set_tracking(parent.tracking)

        self.bind()

    def parent_converter_changed(self, converter):
        """ Update the slider when the converter class changes.

        """
        self.parent.value = self.get_position()

    def parent_value_changed(self, value):
        """ Update the slider position

        The method validates the value before assigment. If it is out of
        range (0.0, 1.0), truncate the value and updates the component value
        attribute. No change notification is fired by these actions.

        If other exceptions are fired during the assigments the component
        value does not change and the widget position is unknown.

        """
        parent = self.parent
        self.set_position(value)
        self.parent.moved = value

    def parent_tracking_changed(self, tracking):
        """ Set the tracking event in the widget

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
        """ Respond to a (possible) change in value from the ui.

        Updated the value of the slider_pos based on the possible change
        from the wxWidget. The `slider_pos` trait will fire the moved
        event only if the value has changed.

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

        Checks if the `down` attribute was set. In that case the
        function calls the `_on_slider_changed` function, fires the
        release event and sets the `down` attribute to false.

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
            the number of steps (in tick intervals) to move the slider
            when the user uses the arrow keys.

        """
        tick_interval = self.widget.GetTickFreq()
        self.widget.SetLineSize(tick_interval * step)

    def set_page_step(self, step):
        """ Set the page step attribute in the wx widget.

        Arguments
        ---------
        step: int
            The number of steps (in tick intervals) to move the slider
            when the user uses the page-up / page-down key. This is also
            used when the user clicks on the left or the right of the
            thumb.

        """
        tick_interval = self.widget.GetTickFreq()
        self.widget.SetPageSize(tick_interval * step)

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
        minimum : int
            The minimum value

        maximum : int
            The maximum value

        """

        self.widget.SetTickFreq(interval * SLIDER_MAX)

    def set_position(self, value):
        """ set the position value.

        The method checks if the value that can be converted to float and
        is in the range of [0.0, 1.0]. If the validation is not succesful
        it sets the `error` and `exception` attributes and truncates the
        assing value in range.

        """
        parent = self.parent
        self.reset_errors()
        try:
            position = parent.converter.to_component(value)
        except Exception as raised_exception:
            self.notify(raised_exception)
        else:
            self.widget.SetValue(position * SLIDER_MAX)

    def get_position(self):
        """ Get the slider position from the widget.

        If error occurs during the conversion it is recorded in the
        `error` and `exception` attributes. The return value in that case
        is None since the value is undefined.

        """
        parent = self.parent
        value = None
        try:
            position = self.widget.GetValue() / float(SLIDER_MAX)
            value = parent.converter.from_component(position)
        except Exception as raised_exception:
            self.notify(raised_exception)
        return value

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

        """
        widget = self.widget

        slider_position = self.parent.value
        thumb = widget.GetThumbLength()
        width, height = [float(x) for x in widget.GetClientSizeTuple()]

        if widget.HasFlag(wx.SL_VERTICAL):
            position = point[1] / height
            thumb = thumb / height

        else:
            position = point[0] / width
            thumb = thumb / width


        minimum = slider_position - thumb
        maximum = slider_position + thumb

        return (minimum <= position <= maximum)

    def reset_errors(self):
        """ Reset the error attributes of the component.

        """
        parent = self.parent
        parent.error = False
        parent.exception = None

    def notify(self, exception):
        """ Update the error attributes of the component.

        """
        warnings.warn("caught exception in slider: {0}".format(exception),
                      RuntimeWarning)
        parent = self.parent
        parent.error = True
        parent.exception = exception
