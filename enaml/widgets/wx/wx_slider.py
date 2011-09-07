import warnings

import wx

from traits.api import implements, Bool, Enum, TraitError

from .wx_control import WXControl

from ..slider import ISliderImpl

from ...enums import Orientation, TickPosition


class WXSlider(WXControl):
    """ A wxPython implementation of Slider.

    The WXSlider uses the wx.Slider control.

    See Also
    --------
    Slider

    """
    implements(ISliderImpl)

    #: When set to True, the enaml widget is still initialising. 
    #: It is mainly used to control the event firing behaviour 
    #: of the widget during initialisation
    _initialising = Bool

    #: holds the last tick_style known to be valid
    _tick_style = Enum(*TickPosition.values())

    #---------------------------------------------------------------------------
    # ISliderImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """Initialisation of ISlider based on wxWidget

        The method create the wxPython Slider widget and binds the ui events
        to WXSlider. 

        """
        self.widget = wx.Slider(parent=self.parent_widget())

    def initialize_widget(self):
        """ Initializes the attributes of the widget. 

        """
        self._initialising = True

        parent = self.parent
        parent._down = False

        # We hard coded range for the widget since we are managing the 
        # conversion.
        self.widget.SetRange(0, 10000)

        # tick marks
        wx_interval = self._convert_for_wx(parent.tick_interval)
        self.widget.SetLineSize(parent.single_step * wx_interval)
        self.widget.SetPageSize(parent.page_step * wx_interval)

        # slider position
        parent.slider_pos = parent.to_slider(parent.value)
        wx_position = self._convert_for_wx(parent.slider_pos)
        self.widget.SetValue(wx_position)

        # orientation
        if parent.orientation == Orientation.VERTICAL:
            self.widget.SetWindowStyle(wx.SL_VERTICAL)
        else:
            self.widget.SetWindowStyle(wx.SL_HORIZONTAL)

        # ticks style
        self._apply_tick_position(parent.tick_position)
        self.widget.SetTickFreq(wx_interval)

        # Bind the event handlers
        self.bind()

        self._initialising = False

    def parent_from_slider_changed(self, from_slider):
        pass
    
    def parent_to_slider_changed(self, to_slider):
        pass
    
    def parent_slider_pos_changed(self, slider_pos):
        """ Update the position in the slider widget

        there are a lot of conversions taking place due to the three
        different variables (value, slider.pos, widget value) that need to
        be in sync.

        .. note:: The wx widget uses integers for the slider range. This
            requires to convert the decimal values in the `slider_pos`
            attribute to an integer.

        """
        parent = self.parent

        # check and update the wxSlider
        position = self._convert_for_wx(slider_pos)
        if position != self.widget.GetValue():
            self.widget.SetValue(position)

        parent.value = value = parent.from_slider(slider_pos)

        # the move event is not fired during initialisation
        if not self._initialising:
            parent.moved = value

    def parent_value_changed(self, value):
        """ Update the slider position

        Update the `slider_pos` to respond to the `value` change. The
        assignment to the slider_pos might fail because `value` is out 
        of range. In that case the last known good value is given back 
        to the value attribute, because we need to keep the `value` 
        attribute in sync with the `slider_pos` and **valid**

        """
        # The try...except block is required because we need to keep the
        # `value` attribute in sync with the `slider_pos` and **valid**
        parent = self.parent
        try:
            parent.slider_pos = parent.to_slider(value)
        except TraitError as ex:
            # revert value
            parent.value = parent.from_slider(parent.slider_pos)
            parent.invalid_value = ex
    
    def parent_tracking_changed(self, tracking):
        pass

    def parent_single_step_changed(self, single_step):
        """ Update the the line step in the widget.

        """
        parent = self.parent
        wx_interval = self._convert_for_wx(parent.tick_interval)
        self.widget.SetLineSize(single_step * wx_interval)

    def parent_page_step_changed(self, page_step):
        """ Update the widget due to change in the line step.

        """
        parent = self.parent
        wx_interval = self._convert_for_wx(parent.tick_interval)
        self.widget.SetPageSize(page_step * wx_interval)

    def parent_tick_interval_changed(self, tick_interval):
        """ Update the tick marks interval.

        """
        wx_interval = self._convert_for_wx(tick_interval)
        self.widget.SetTickFreq(wx_interval)
    
    def parent_tick_position_changed(self, tick_position):
        """ Update the widget due to change in the tick position

        The method ensures that the tick position style can be applied 
        and reverts to the last value if the request is invalid.

        """
        if self._apply_tick_position(tick_position):
            # keep a copy of the last know valid
            self._tick_style = tick_position
        else:
            # change to the last know valid value
            self.parent.tick_position = self._tick_style

    def parent_orientation_changed(self, orientation):
        """ Update the widget due to change in the orientation attribute

        The method applies the orientation style and fixes the tick position
        option if necessary.

        """
        parent = self.parent
        ticks = parent.tick_position

        if orientation == Orientation.VERTICAL:
            style = self.widget.GetWindowStyle() | wx.SL_VERTICAL
            self.widget.SetWindowStyle(style)

            if ticks in (TickPosition.TOP, TickPosition.DEFAULT):
                parent.tick_position = TickPosition.LEFT

            elif ticks == TickPosition.BOTTOM:
                parent.tick_position = TickPosition.LEFT
        
        else:
            style = self.widget.GetWindowStyle() | wx.SL_HORIZONTAL
            self.widget.SetWindowStyle(style)

            if ticks in (TickPosition.LEFT, TickPosition.DEFAULT):
                parent.tick_position = TickPosition.TOP

            elif ticks == TickPosition.RIGHT:
                parent.tick_position = TickPosition.BOTTOM

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
        widget.Bind(wx.EVT_SCROLL_THUMBTRACK, self._on_thumb_track)
        widget.Bind(wx.EVT_SCROLL_TOP, self._on_slider_changed)
        widget.Bind(wx.EVT_SCROLL_BOTTOM, self._on_slider_changed)
        widget.Bind(wx.EVT_SCROLL_LINEUP, self._on_slider_changed)
        widget.Bind(wx.EVT_SCROLL_LINEDOWN, self._on_slider_changed)
        widget.Bind(wx.EVT_SCROLL_PAGEUP, self._on_slider_changed)
        widget.Bind(wx.EVT_SCROLL_PAGEDOWN, self._on_slider_changed)
        widget.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        widget.Bind(wx.EVT_LEFT_UP, self._on_left_up)

    def _convert_for_wx(self, value):
        """ Converts the float value to an integer suitable for the
        wx.Slider.

        """
        position = int(value * 10000)
        return position

    def _convert_from_wx(self, value):
        """ Converts the value to an integer suitable for the wx.Slider.

        """
        position = value / 10000.0
        return position

    def _apply_tick_position(self, value):
        """ Converts the tick position into style flags.

        Attempts to apply the requested tick position option. Returns 
        True if the new value was valid.

        """
        style = self.widget.GetWindowStyle()
        orientation = self.parent.orientation

        if orientation == Orientation.VERTICAL:
            if value == TickPosition.LEFT:
                style |= wx.SL_LEFT | wx.SL_AUTOTICKS
            elif value == TickPosition.RIGHT:
                style |= wx.SL_RIGHT | wx.SL_AUTOTICKS
            elif value == TickPosition.BOTH:
                warnings.warn('Option not implemented in wxPython')
            elif value == TickPosition.NO_TICKS:
                pass
            elif value == TickPosition.DEFAULT:
                style |= wx.SL_AUTOTICKS
            else:
                warnings.warn('Option {0} is incompatible with the current'
                              ' orientation {1} and is ignored'.\
                              format(str(value), str(orientation)))
                return False

        else:
            if value == TickPosition.TOP:
                style |= wx.SL_TOP | wx.SL_AUTOTICKS
            elif value == TickPosition.BOTTOM:
                style |= wx.SL_BOTTOM | wx.SL_AUTOTICKS
            elif value == TickPosition.BOTH:
                warnings.warn('Option not implemented in wxPython')
            elif value == TickPosition.NO_TICKS:
                pass
            elif value == TickPosition.DEFAULT:
                style |= wx.SL_AUTOTICKS
            else:
                warnings.warn('Option {0} is incompatible with the current'
                              ' orientation {1} and is ignored'.\
                              format(str(value), str(orientation)))
                return False

        self.widget.SetWindowStyle(style)

        return True

    def _thumb_hit(self, point):
        """ Is the point in the thumb area.

        """
        parent = self.parent

        # the relative position of the mouse
        width, height = [float(x) for x in self.widget.GetClientSizeTuple()]
        if parent.orientation == Orientation.VERTICAL:
            mouse = point[1] / height
            thumb = self.widget.GetThumbLength() / height

        else:
            mouse = point[0] / width
            thumb = self.widget.GetThumbLength() / width

        # minimum and maximum position (edges) of the thumb
        minimum = parent.slider_pos - thumb
        maximum = parent.slider_pos + thumb

        return minimum <= mouse <= maximum

    def _on_slider_changed(self, event):
        """ Respond to a (possible) change in value from the ui.

        Updated the value of the slider_pos based on the possible change 
        from the wxwidget. The `slider_pos` trait will fire the moved 
        event only if the value has changed.

        """
        new_position = self.widget.GetValue()
        self.parent.slider_pos = self._convert_from_wx(new_position)
        event.Skip()

    def _on_thumb_track(self, event):
        """ Update `slider_pos` when the thumb is dragged.

        The slider_pos attribute is updated during a dragging if the
        self.tracking attribute is True. This will also fire a moved 
        event for a very change. The event is not skipped.

        """
        if self.parent.tracking:
            self._on_slider_changed(event)

    def _on_left_down(self, event):
        """ Check if the mouse was pressed over the thumb.

        Estimates the position of the thumb and then checks if the mouse 
        was pressed over it to fire the `pressed` event and sets the 
        `down` attribute.

        """
        parent = self.parent
        mouse_position = event.GetPosition()
        if self._thumb_hit(mouse_position):
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

