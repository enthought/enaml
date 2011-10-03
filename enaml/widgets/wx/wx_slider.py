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

    #: Internal backup valid posistion value used to guard against errors
    #: with the from_slider and to_slider functions
    _backup = Float

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
        self._backup = parent.value
        self.set_value(parent.value)
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
        parent = self.parent
        new_value = self.convert_position()
        parent.value = new_value

    def parent_to_slider_changed(self, to_slider):
        """ Update the slider position with based on the new function

        Arguments
        ---------
        to_slider : Callable
            A function that takes one argument to convert from a Python
            value to the appropriate slider position.

        """
        parent = self.parent
        position = self.validate(parent.value)
        self.set_in_widget(position)

    def parent_value_changed(self, value):
        """ Update the slider position value

        Update the `slider_pos` to respond to the `value` change. The
        assignment to the slider_pos might fail because `value` is out
        of range. In that case the last known good value is given back
        to the value attribute.

        """
        self.set_value(value)

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
        new_value = self.convert_position()
        parent.value = new_value
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

    def set_value(self, value):
        """ Validate and set the slider widget position to the new value

        The assignment fail because `value` is out of range or the
        conversion through `to_slider` returns an exception. In that case
        the last known good value is given back to the parent.value
        attribute.

        """
        parent = self.parent

        position = self.validate(value, reset_errors = False)
        # the `value` and `position` variables will be different if the
        # validation failed.
        if value == position:
            self.set_in_widget(position)
            if position != self._backup:
                parent.moved = position
            self._backup = position
            self.reset_errors()
        else:
            exception = parent.exception
            parent.value = position
            parent.error = True
            parent.exception = exception

    def validate(self, value, reset_errors=True):
        """ Validate the position value.

        The method checks if the output of the :meth:`to_slider` function
        returns a value that can be converted to float and is in the range
        of [0.0, 1.0]. If the validation is not succesful it sets the
        `error` and `exception` attributes and returns the previous known
        good value.

        If the :attr:`reset_errors` is False then the method does not
        reset the error and exception attributes (unless there is an
        exception ofcourse)
        """
        parent = self.parent

        if reset_errors:
            self.reset_errors()

        try:
            position = float(parent.to_slider(parent.value))

            if not (0.0 <= position <= 1.0):
                raise ValueError('to_slider() must return a value '
                                            'between 0.0 and 1.0, but instead'
                                            ' returned %s'  % repr(position))
        except Exception as raised_exception:
            self.notify(raised_exception)
            position = self._backup

        return position

    def convert_position(self, reset_errors=True):
        """ Convert and return the slider position coming from the widget.

        The method checks if the :meth:`from_slider` function
        does not raise an exception. If the converison is not successful
        it sets the `error` and `exception` attributes and returns the
        current enaml component position.

        If the :attr:`reset_errors` is False then the method does not
        reset the error and exception attributes (unless there is an
        exception ofcourse).

        """
        parent = self.parent

        if reset_errors:
            self.reset_errors()

        value = self.retrieve_from_widget()

        try:
            position = parent.from_slider(value)
        except Exception as raised_exception:
            self.notify(raised_exception)
            position = parent.value

        return position

    def reset_errors(self):
        """ Reset the error attributes of the component.

        """
        parent = self.parent
        parent.error = False
        parent.exception = None

    def notify(self, exception):
        """ Update the error attributes of the component.

        """
        parent = self.parent
        parent.error = True
        parent.exception = exception

    def retrieve_from_widget(self):
        """ Get the slider position from the widget and convert to the
        enaml component internal representation.

        """
        return self.widget.GetValue() / float(SLIDER_MAX)


    def set_in_widget(self, value):
        """ set the slider position to the widget and convert to the
        enaml internal representation.

        """
        self.widget.SetValue(value * SLIDER_MAX)

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
##        print "Mouse position is {0}".format(point)
        widget = self.widget

        slider_position = self.parent.value
##        print "Slider position {0}".format(slider_position)
        thumb = widget.GetThumbLength()
##        print "Thumb length {0}".format(thumb)
        width, height = [float(x) for x in widget.GetClientSizeTuple()]
##        print "Size of the widget is".format(width,height)

        if widget.HasFlag(wx.SL_VERTICAL):
            position = point[1] / height
            thumb = thumb / height

        else:
            position = point[0] / width
            thumb = thumb / width

##        print "Translated mouse position is {0}".format(position)

        minimum = slider_position - thumb
        maximum = slider_position + thumb

##        print "Maximum and minimum are {0},{1}".format(maximum, minimum)
        return (minimum <= position <= maximum)
