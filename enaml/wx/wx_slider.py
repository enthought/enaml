#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx
import wx.lib.newevent

from .wx_control import WxControl


#: Horizontal tick mapping
_TICK_POSITION_MAP = {
    'top': wx.SL_TOP | wx.SL_AUTOTICKS,
    'bottom': wx.SL_BOTTOM | wx.SL_AUTOTICKS,
    'left': wx.SL_LEFT | wx.SL_AUTOTICKS,
    'right': wx.SL_RIGHT | wx.SL_AUTOTICKS,
    'both': wx.SL_BOTH | wx.SL_AUTOTICKS,
}


#: An OR'd combination of all the tick flags.
_TICK_MASK = (
    wx.SL_TOP | wx.SL_BOTTOM | wx.SL_LEFT | wx.SL_RIGHT | wx.SL_BOTH |
    wx.SL_AUTOTICKS
)


#: A map adapting orientation to tick positions
_TICK_ADAPT_MAP = {
    'vertical': {
        'left': 'left',
        'right': 'right',
        'both': 'both',
        'top': 'left',
        'bottom': 'right',
    },
    'horizontal': {
        'left': 'top',
        'right': 'bottom',
        'both': 'both',
        'top': 'top',
        'bottom': 'bottom',
    },
}


#: A map from string orientation to wx slider orientation
_ORIENTATION_MAP = {
    'horizontal': wx.SL_HORIZONTAL,
    'vertical': wx.SL_VERTICAL,
}


#: An OR'd combination of all the orientation flags
_ORIENTATION_MASK = wx.SL_HORIZONTAL | wx.SL_VERTICAL


#: A new event emitted by the custom slider control
wxSliderEvent, EVT_SLIDER = wx.lib.newevent.NewEvent()


class wxProperSlider(wx.Slider):
    """ A wx.Slider subclass which supports tracking.

    """
    #: The event types for the frequent thumb track event
    _tracking_evt = wx.EVT_SCROLL_THUMBTRACK.evtType[0]

    #: The event type for the thumb release event.
    _release_evt = wx.EVT_SCROLL_THUMBRELEASE.evtType[0]

    #: The event type for the scroll end event.
    _end_evt = wx.EVT_SCROLL_CHANGED.evtType[0]

    def __init__(self, *args, **kwargs):
        """ Initialize a wxProperSlider.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments for initializing a
            wx.Slider.

        """
        super(wxProperSlider, self).__init__(*args, **kwargs)
        self._tracking = True
        self.Bind(wx.EVT_SCROLL, self.OnScroll)

    def OnScroll(self, event):
        """ An event handler which handles all scroll events.

        This handler determines whether or not a slider event sould be
        emitted for the scroll changed, based on whether tracking is
        enabled for the slider.

        """
        evt_type = event.EventType

        # We never emit on the _end_event since that is windows-only
        if evt_type == self._end_evt:
            return

        if self._tracking:
            if evt_type != self._release_evt:
                emit = True
            else:
                emit = False
        else:
            emit = evt_type != self._tracking_evt

        if emit:
            evt = wxSliderEvent()
            wx.PostEvent(self, evt)

    def GetTracking(self):
        """ Whether or not tracking is enabled for the slider.

        Returns
        -------
        result : bool
            True if tracking is enabled for the slider, False otherwise.

        """
        return self._tracking

    def SetTracking(self, tracking):
        """ Set whether tracking is enabled for the slider.

        Parameters
        ----------
        tracking : bool
            True if tracking should be enabled, False otherwise.

        """
        self._tracking = tracking


class WxSlider(WxControl):
    """ A Wx implementation of an Enaml Slider.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying wxProperSlider widget.

        """
        return wxProperSlider(parent)

    def create(self, tree):
        """ Create and initialize the slider control.

        """
        # NOTE: The tick interval must be set *after* the tick position
        # or Wx will ignore the tick interval. grrr...
        super(WxSlider, self).create(tree)
        # Initialize the value after the minimum and maximum to avoid
        # the potential for premature internal clipping of the value.
        self.set_minimum(tree['minimum'])
        self.set_maximum(tree['maximum'])
        self.set_value(tree['value'])
        self.set_orientation(tree['orientation'])
        self.set_page_step(tree['page_step'])
        self.set_single_step(tree['single_step'])
        self.set_tick_position(tree['tick_position'])
        self.set_tick_interval(tree['tick_interval'])
        self.set_tracking(tree['tracking'])
        self.widget().Bind(EVT_SLIDER, self.on_value_changed)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_value(self, content):
        """ Handle the 'set_value' action from the Enaml widget.

        """
        self.set_value(content['value'])

    def on_action_set_maximum(self, content):
        """ Handle the 'set_maximum' action from the Enaml widget.

        """
        self.set_maximum(content['maximum'])

    def on_action_set_minimum(self, content):
        """ Handle the 'set_minimum' action from the Enaml widget.

        """
        self.set_minimum(content['minimum'])

    def on_action_set_orientation(self, content):
        """ Handle the 'set_orientation' action from the Enaml widget.

        """
        self.set_orientation(content['orientation'])

    def on_action_set_page_step(self, content):
        """ Handle the 'set_page_step' action from the Enaml widget.

        """
        self.set_page_step(content['page_step'])

    def on_action_set_single_step(self, content):
        """ Handle the 'set_single_step' action from the Enaml widget.

        """
        self.set_single_step(content['single_step'])

    def on_action_set_tick_interval(self, content):
        """ Handle the 'set_tick_interval' action from the Enaml widget.

        """
        self.set_tick_interval(content['tick_interval'])

    def on_action_set_tick_position(self, content):
        """ Handle the 'set_tick_position' action from the Enaml widget.

        """
        self.set_tick_position(content['tick_position'])

    def on_action_set_tracking(self, content):
        """ Handle the 'set_tracking' action from the Enaml widget.

        """
        self.set_tracking(content['tracking'])

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_value_changed(self, event):
        """ Send the 'value_changed' action to the Enaml widget when the
        slider value has changed.

        """
        content = {'value': self.widget().GetValue()}
        self.send_action('value_changed', content)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_value(self, value):
        """ Set the value of the underlying widget.

        """
        self.widget().SetValue(value)

    def set_maximum(self, maximum):
        """ Set the maximum value of the underlying widget.

        """
        widget = self.widget()
        minimum, _ = widget.GetRange()
        widget.SetRange(minimum, maximum)

    def set_minimum(self, minimum):
        """ Set the minimum value of the underlying widget.

        """
        widget = self.widget()
        _, maximum = widget.GetRange()
        widget.SetRange(minimum, maximum)

    def set_orientation(self, orientation):
        """ Set the orientation of the underlying widget.

        """
        widget = self.widget()
        style = widget.GetWindowStyle()
        style &= ~_ORIENTATION_MASK
        style |= _ORIENTATION_MAP[orientation]
        widget.SetWindowStyle(style)

    def set_page_step(self, page_step):
        """ Set the page step of the underlying widget.

        """
        self.widget().SetPageSize(page_step)

    def set_single_step(self, single_step):
        """ Set the single step of the underlying widget.

        """
        self.widget().SetLineSize(single_step)

    def set_tick_interval(self, interval):
        """ Set the tick interval of the underlying widget.

        """
        self.widget().SetTickFreq(interval)

    def set_tick_position(self, tick_position):
        """ Set the tick position of the underlying widget.

        """
        widget = self.widget()
        style = widget.GetWindowStyle()
        style &= ~_TICK_MASK
        if tick_position != 'no_ticks':
            if style & wx.SL_VERTICAL:
                tick_position = _TICK_ADAPT_MAP['vertical'][tick_position]
            else:
                tick_position = _TICK_ADAPT_MAP['horizontal'][tick_position]
            style |= _TICK_POSITION_MAP[tick_position]
        widget.SetWindowStyle(style)

    def set_tracking(self, tracking):
        """ Set the tracking of the underlying widget.

        """
        self.widget().SetTracking(tracking)

