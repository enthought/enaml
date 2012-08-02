#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx

from .wx_constraints_widget import WxConstraintsWidget


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


class WxSlider(WxConstraintsWidget):
    """ A Wx implementation of an Enaml Slider.

    """
    #: The internal tracking flag, since the wxSlider doesn't support it.
    _tracking = True

    def create(self):
        """ Create the underlying wx.Slider widget.

        """
        self.widget = wx.Slider(self.parent_widget)

    def initialize(self, attrs):
        """ Initialize the widget's attributes.

        """
        super(WxSlider, self).initialize(attrs)
        self.set_value(attrs['value'])
        self.set_maximum(attrs['maximum'])
        self.set_minimum(attrs['minimum'])
        self.set_orientation(attrs['orientation'])
        self.set_page_step(attrs['page_step'])
        self.set_single_step(attrs['single_step'])
        self.set_tick_interval(attrs['tick_interval'])
        self.set_tick_position(attrs['tick_position'])
        self.set_tracking(attrs['tracking'])
        self.widget.Bind(wx.EVT_SCROLL, self.on_value_changed)

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
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_value_changed(self, value):
        """ Send the 'value_changed' action to the Enaml widget when the 
        slider value has changed.

        """
        # wx doesn't support tracking, so we have to fake it.
        if self._tracking:
            content = {'value': self.widget.GetValue()}
            self.send_action('value_changed', content)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_value(self, value):
        """ Set the value of the underlying widget.

        """
        self.widget.SetValue(value)

    def set_maximum(self, maximum):
        """ Set the maximum value of the underlying widget.

        """
        minimum, _ = self.widget.GetRange()
        self.widget.SetRange(minimum, maximum)

    def set_minimum(self, minimum):
        """ Set the minimum value of the underlying widget.

        """
        _, maximum = self.widget.GetRange()
        self.widget.SetRange(minimum, maximum)

    def set_orientation(self, orientation):
        """ Set the orientation of the underlying widget.

        """
        style = self.widget.GetWindowStyle()
        style &= ~_ORIENTATION_MASK
        style |= _ORIENTATION_MAP[orientation]
        self.widget.SetWindowStyle(style)

    def set_page_step(self, page_step):
        """ Set the page step of the underlying widget.

        """
        self.widget.SetPageSize(page_step)

    def set_single_step(self, single_step):
        """ Set the single step of the underlying widget.

        """
        self.widget.SetLineSize(single_step)

    def set_tick_interval(self, interval):
        """ Set the tick interval of the underlying widget.

        """
        return
        self.widget.SetTickFreq(interval)

    def set_tick_position(self, tick_position):
        """ Set the tick position of the underlying widget.

        """
        style = self.widget.GetWindowStyle()
        style &= ~_TICK_MASK
        if style & wx.SL_VERTICAL:
            tick_position = _TICK_ADAPT_MAP['vertical'][tick_position]
        else:
            tick_position = _TICK_ADAPT_MAP['horizontal'][tick_position]
        style |= _TICK_POSITION_MAP[tick_position]
        self.widget.SetWindowStyle(style)

    def set_tracking(self, tracking):
        """ Set the tracking of the underlying widget.

        """
        pass

