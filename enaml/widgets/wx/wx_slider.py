#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import warnings

import wx

from traits.api import implements, Bool, Enum, TraitError

from .wx_control import WXControl

from ..slider import ISliderImpl

from ...enums import Orientation, TickPosition

SLIDER_MAX = 10000


class WXSlider(WXControl):
    """ A wxPython implementation of Slider.

    The WXSlider uses the wx.Slider control.

    See Also
    --------
    Slider

    """
    implements(ISliderImpl)

    #: A mechanism to prevent update cycles when syncing `parent.value` with
    #: `parent.slider_pos`.
    _setting = Bool

    #---------------------------------------------------------------------------
    # ISliderImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """Initialisation of ISlider based on wxWidget

        The method create the wxPython Slider widget and binds the ui events
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
        self.set_position()
        self.set_orientation(parent.orientation)
        self.set_tick_position(parent.tick_position)
        self.set_tick_frequency(parent.tick_interval)
        self.set_single_step(parent.single_step)
        self.set_page_step(parent.page_step)
        self.set_tracking(parent.tracking)

        self.bind()

    def parent_from_slider_changed(self, from_slider):
        """ Update the slider value with based on the new function

        Arguments
        ---------
        from_slider : Callable
            A function that takes one argument to convert from the slider
            postion to the appropriate Python value.

        """
        position = self.get_position()
        parent = self.parent
        parent.value = parent.from_slider(position)

    def parent_to_slider_changed(self, to_slider):
        """ Update the slider position with based on the new function

        Arguments
        ---------
        to_slider : Callable
            A function that takes one argument to convert from a Python
            value to the appropriate slider position.

        """
        self.set_position()

    def parent_value_changed(self, value):
        """ Update the slider position value

        Update the `slider_pos` to respond to the `value` change. The
        assignment to the slider_pos might fail because `value` is out
        of range. In that case the last known good value is given back
        to the value attribute.

        """
        self.set_position()

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
        widget.Bind(wx.EVT_LEFT_UP, self._on_left_up)

    def _on_slider_changed(self, event):
        """ Respond to a (possible) change in value from the ui.

        Updated the value of the slider_pos based on the possible change
        from the wxWidget. The `slider_pos` trait will fire the moved
        event only if the value has changed.

        """
        position = self.get_position()
        parent = self.parent
        parent.value = parent.from_slider(position)
        event.Skip()

    def _on_thumb_track(self, event):
        """ Update `slider_pos` when the thumb is dragged.

        The slider_pos attribute is updated during a dragging if the
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
        if self._is_thumb_hit(mouse_position, wx_position):
            parent._down = True
            parent.pressed = True
        event.Skip()

    def _on_left_up(self, event):
        """ Update if the left button was released

        Checks if the `down` attribute was set. In that case the
        function calls the `_on_slider_changed` function, fires the
        release event and sets the `down` attribute to false.

        """
        parent = self.parent
        if parent._down:
            self._on_slider_changed(event)
            parent._down = False
            parent.released = True
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

    def set_position(self):
        """Set the slider position based on the value and to_slider().

        Changes the position of the slider in the widget if necessary.
        We use a larger range in the Qt widget for fine-grained control.
        The value is validated and if there are errors during the validation
        the slider position reverted.

        """
        if self._setting:
            return # no need to do anything the values have been already syncronised
        else:
            self._setting = True

        parent = self.parent

        position = self._validate(parent.value)

        if position is not None:
            wx_position = position * SLIDER_MAX
            if wx_position != self.widget.GetValue():
                self.widget.SetValue(wx_position)
        else:
            self.get_position()

        self._setting = False

    def get_position(self):
        """Get the slider position.

        Read the slider position from the widget and convert it to the
        enaml slider representation.

        """
        parent = self.parent

        try:
            wx_position = float(self.widget.GetValue())
            value = parent.from_slider(wx_position / SLIDER_MAX)
        except Exception as raised_exception:
            parent.exception = raised_exception
            parent.error = True
        else:
            parent.value = value
            # reset errors only if we are not syncronising
            if not self._setting:
                parent.exception = None
                parent.error = False

    def set_tick_position(self, ticks):
        """ Apply the tick position in the widget.

        Arguments
        ---------
        ticks : TickPosition
            The tick position

        Returns
        -------
        result : boolean
            True if the new value was valid. False if the value is
            invalid.

        """
        widget = self.widget
        style = widget.GetWindowStyle()
        style &= ~(wx.SL_TOP | wx.SL_BOTTOM |
                  wx.SL_LEFT | wx.SL_RIGHT | wx.SL_BOTH)

        if widget.HasFlag(wx.SL_VERTICAL):
            if ticks == TickPosition.LEFT:
                style |= wx.SL_LEFT | wx.SL_AUTOTICKS
            elif ticks == TickPosition.RIGHT:
                style |= wx.SL_RIGHT | wx.SL_AUTOTICKS
            elif ticks == TickPosition.BOTH:
                style |= wx.SL_BOTH | wx.SL_AUTOTICKS
            elif ticks == TickPosition.NO_TICKS:
                style &= ~wx.SL_AUTOTICKS
            elif ticks == TickPosition.DEFAULT:
                style |= wx.SL_AUTOTICKS
            else:
                warnings.warn('Option {0} is incompatible with the vertical'
                              ' orientation and is ignored'.\
                              format(str(ticks)))
                return False

        else:
            if ticks == TickPosition.TOP:
                style |= wx.SL_TOP | wx.SL_AUTOTICKS
            elif ticks == TickPosition.BOTTOM:
                style |= wx.SL_BOTTOM | wx.SL_AUTOTICKS
            elif ticks == TickPosition.BOTH:
                style |= wx.SL_BOTH | wx.SL_AUTOTICKS
            elif ticks == TickPosition.NO_TICKS:
                style &= ~wx.SL_AUTOTICKS
            elif ticks == TickPosition.DEFAULT:
                style |= wx.SL_AUTOTICKS
            else:
                warnings.warn('Option {0} is incompatible with the horizontal'
                              ' orientation and is ignored'.\
                              format(str(ticks)))
                return False

        widget.SetWindowStyle(style)

        return True

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
            widget.SetWindowStyle(style)

            if tick_position in (TickPosition.TOP, TickPosition.DEFAULT):
                parent.tick_position = TickPosition.LEFT
            elif tick_position == TickPosition.BOTTOM:
                parent.tick_position = TickPosition.RIGHT
        else:
            style |= wx.SL_HORIZONTAL
            widget.SetWindowStyle(style)

            if tick_position in (TickPosition.LEFT, TickPosition.DEFAULT):
                parent.tick_position = TickPosition.TOP
            elif tick_position == TickPosition.RIGHT:
                parent.tick_position = TickPosition.BOTTOM

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

    def _is_thumb_hit(self, point, slider_position):
        """ Is the point in the thumb area.

        Arguments
        ---------
        point : tuple (x,y)
            The point in the widget pixel coordinates.
        slider_postion : float
            The position in the widget scale.

        Returns
        -------
        result : boolean
            True if the point is inside the thumb area.

        """
        widget = self.widget

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

        return minimum <= position <= maximum

    def _validate(self, value):
        """ Validate the value attribute

        The method checks if the output of the :meth:`to_slider` function
        returns a value that can be converted to float and is in the range
        of [0.0, 1.0]. If the validation is not succesful it sets the
        `error` and `exception` attributes and returns None. It returns the
        value to be used for the slider widget if the validation passed.

        """
        parent = self.parent

        parent.error = False
        parent.exception = None

        try:
            position = float(parent.to_slider(parent.value))

            if not 0.0 <= position <= 1.0:
                raise ValueError('to_slider() must return a value '
                                            'between 0.0 and 1.0, but instead'
                                            ' returned %s'  % repr(position))
        except Exception as raised_exception:
            parent.error = True
            parent.exception = raised_exception
            position = None

        return position
