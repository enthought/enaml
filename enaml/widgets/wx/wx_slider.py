#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_control import WXControl

from ..slider import AbstractTkSlider


#: A map from Enaml constants to wxSlider TickPosition values for a
#: horizontal slider.
HORIZ_TICK_POS_MAP = {'top': wx.SL_TOP, 
                      'bottom': wx.SL_BOTTOM,
                      'both': wx.SL_BOTH}


#: A map from Enaml constants to wxSlider TickPosition values for a
#: vertical slider.
VERT_TICK_POS_MAP = {'left': wx.SL_LEFT, 
                     'right': wx.SL_RIGHT,
                     'both': wx.SL_BOTH}


#: A map that adapts horizontal positions to vertical positions
ADAPT_HORIZ_TICK = {'left': 'top', 'right': 'bottom'}


#: A map that adapts vertical positions to horizontal positions
ADAPT_VERT_TICK = {'top': 'left', 'bottom': 'right'}


class WXSlider(WXControl, AbstractTkSlider):
    """ A wxPython implementation of Slider.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying wx.Slider control.

        """
        self.widget = wx.Slider(parent=parent)

    def initialize(self):
        """ Initializes the attributes of the toolkit widget.

        """
        super(WXSlider, self).initialize()
        # Setting double buffered reduces flicker on Windows
        self.widget.SetDoubleBuffered(True)
        shell = self.shell_obj
        shell._down = False
        self.set_range(shell.minimum, shell.maximum)
        self.set_position(shell.value)
        self.set_orientation(shell.orientation)
        self.set_tick_position(shell.tick_position)
        self.set_tick_frequency(shell.tick_interval)
        self.set_single_step(shell.single_step)
        self.set_page_step(shell.page_step)

    def bind(self):
        """ Binds the event handlers for the slider widget.

        """
        super(WXSlider, self).bind()
        widget = self.widget
        widget.Bind(wx.EVT_SCROLL_THUMBTRACK, self._on_slider_moved)
        widget.Bind(wx.EVT_SCROLL_TOP, self._on_slider_keyed)
        widget.Bind(wx.EVT_SCROLL_BOTTOM, self._on_slider_keyed)
        widget.Bind(wx.EVT_SCROLL_LINEUP, self._on_slider_keyed)
        widget.Bind(wx.EVT_SCROLL_LINEDOWN, self._on_slider_keyed)
        widget.Bind(wx.EVT_SCROLL_PAGEUP, self._on_slider_keyed)
        widget.Bind(wx.EVT_SCROLL_PAGEDOWN, self._on_slider_keyed)
        widget.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        widget.Bind(wx.EVT_LEFT_UP, self._on_thumb_released)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_minimum_changed(self, minimum):
        """ The change handler for the 'minimum' attribute on the shell
        object.

        """
        self.set_range(minimum, self.shell_obj.maximum)

    def shell_maximum_changed(self, maximum):
        """ The change handler for the 'maximum' attribute on the shell
        object.
        
        """
        self.set_range(self.shell_obj.minimum, maximum)

    def shell_value_changed(self, value):
        """ The change handler for the 'value' attribute on the shell
        object.
        
        """
        self.set_position(value)

    def shell_tracking_changed(self, tracking):
        """ The change handler for the 'tracking' attribute on the shell
        object.

        """
        # wx doesn't support tracking modes, so we fake it when we 
        # receive a scroll event.
        pass

    def shell_single_step_changed(self, single_step):
        """ The change handler for the 'single_step' attribute on the 
        shell object.
        
        """        
        self.set_single_step(single_step)

    def shell_page_step_changed(self, page_step):
        """ The change handler for the 'page_step' attribute on the 
        shell object.

        """
        self.set_page_step(page_step)

    def shell_tick_interval_changed(self, tick_interval):
        """ The change handler for the 'tick_interval' attribute on the
        shell object.

        """
        shell = self.shell_obj
        self.set_tick_frequency(tick_interval)
        # This extra calls are made since the range trait on 
        # shell object may clip the values to fit within the 
        # range without firing a changed notification.
        self.set_single_step(shell.single_step)
        self.set_page_step(shell.page_step)

    def shell_tick_position_changed(self, tick_position):
        """ The change handler for the 'tick_position' attribute on the
        shell object.

        """
        self.set_tick_position(tick_position)
        self.shell_obj.size_hint_updated()

    def shell_orientation_changed(self, orientation):
        """ The change handler for the 'orientation' attribute on the 
        shell object.

        """
        self.set_orientation(orientation)
        self.shell_obj.size_hint_updated()

    #--------------------------------------------------------------------------
    # Event Handlers 
    #--------------------------------------------------------------------------
    def _on_slider_moved(self, event):
        """ The event handler for a slider drag event.

        """
        shell = self.shell_obj
        value = self.widget.GetValue()

        # Update the value only if tracking is turned on.
        if shell.tracking:
            shell.value = value
        
        # Since this event is only fired when the drag handle is 
        # moved with the mouse, it's safe to fire the move event
        # with no further checks.
        shell.moved(value)

        event.Skip()

    def _on_slider_keyed(self, event):
        """ The event handler for the user changing the value of the 
        slider through a key.

        """
        self.shell_obj.value = self.widget.GetValue()
        event.Skip()

    def _on_left_down(self, event):
        """ The event handler for the left mouse button being pressed.
        This estimates the position of the drag handle and then checks 
        if the mouse was pressed over it and then fires the `pressed` 
        event and sets the `down` attribute.

        """
        # Wx does not provide an event for detecting a mouse press
        # on the drag handle. So we have to estimate it by doing a
        # bit of geometry. This is not very accurate but probably
        # sufficient for most use cases.
        shell = self.shell_obj
        widget = self.widget
        mouse_position = event.GetPosition()
        slider_position = widget.GetValue()
        thumb = widget.GetThumbLength() / 2.0
        width, height = widget.GetClientSizeTuple()

        if widget.HasFlag(wx.SL_VERTICAL):
            position = mouse_position[1] / float(height)
        else:
            position = mouse_position[0] / float(width)

        slider_length = float(widget.GetMax() - widget.GetMin()) + 1.0
        minimum = (slider_position - thumb) / slider_length
        maximum = (slider_position + thumb) / slider_length

        hit = minimum <= position <= maximum

        if hit:
            shell._down = True
            shell.pressed()
        
        event.Skip()

    def _on_thumb_released(self, event):
        """ The event handler for drag handle being released. It
        updates the value in the shell and fires the appropriate
        events.

        """
        shell = self.shell_obj
        value = self.widget.GetValue()
        shell.value = value
        if shell._down:
            shell._down = False
            shell.released()
        event.Skip()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_single_step(self, step):
        """ Set the single step attribute in the wx widget.

        """
        self.widget.SetLineSize(step)

    def set_page_step(self, step):
        """ Set the page step attribute in the wx widget.

        """
        self.widget.SetPageSize(step)

    def set_tick_position(self, ticks):
        """ Apply the tick position in the widget.

        """
        shell = self.shell_obj
        widget = self.widget
        style = widget.GetWindowStyle()
        style &= ~(wx.SL_TOP | wx.SL_BOTTOM | wx.SL_LEFT | wx.SL_RIGHT | 
                   wx.SL_BOTH | wx.SL_AUTOTICKS | wx.SL_TICKS)

        if shell.orientation == 'vertical':
            if ticks in ADAPT_VERT_TICK:
                shell.tick_position = ADAPT_VERT_TICK[ticks]
                return
            if ticks in VERT_TICK_POS_MAP:
                style |= (VERT_TICK_POS_MAP[ticks] | wx.SL_AUTOTICKS)
        else:
            if ticks in ADAPT_HORIZ_TICK:
                shell.tick_position = ADAPT_HORIZ_TICK[ticks]
                return
            if ticks in HORIZ_TICK_POS_MAP:
                style |= (HORIZ_TICK_POS_MAP[ticks] | wx.SL_AUTOTICKS)

        widget.SetWindowStyle(style)
        
        # There seems to be a bug in wx where the tick interval needs 
        # to be applied again for it to appear properly
        widget.SetTickFreq(shell.tick_interval)

    def set_orientation(self, orientation):
        """ Set the slider orientation.

        """
        widget = self.widget
        shell = self.shell_obj

        style = widget.GetWindowStyle()
        style &= ~(wx.SL_HORIZONTAL | wx.SL_VERTICAL)

        if orientation == 'vertical':
            style |= wx.SL_VERTICAL
        else:
            style |= wx.SL_HORIZONTAL

        widget.SetWindowStyle(style)
        self.set_tick_position(shell.tick_position)

    def set_range(self, minimum, maximum):
        """ Set the slider widget range.

        """
        self.widget.SetRange(minimum, maximum)

    def set_tick_frequency(self, interval):
        """ Set the slider widget tick mark fequency.

        """
        self.widget.SetTickFreq(interval)

    def set_position(self, value):
        """ set the position value.

        """
        self.widget.SetValue(value)

