import wx

from traits.api import implements, Bool, Callable, Event, Int, Str

from .wx_element import WXElement

from ..i_spin_box import ISpinBox


class WXSpinBox(WXElement):
    """ A wxPython implementation of ISpinBox.

    Attributes
    ----------
    low : Int
        The minimum value for the spin box.

    high : Int
        The maximum value for the spin box.
    
    step : Int
        The amount to increase or decrease the value per click.

    value : Int
        The current value for the spin box.

    prefix : Str
        The prefix string to display in the spin box.

    suffix : Str
        The suffix string to display in the spin box.
    
    special_value_text : Str
        An optional string to display when the user selects the 
        minimum value in the spin box.

    to_string : Callable
        An optional callable that takes one argument to convert the 
        integer value to text to display in the spin box.

    from_string : Callable
        An optional callable that takes one argument to convert the 
        user typed string to an integer value.

    wrapping : Bool
        If True, the spin box will wrap around at its extremes.

    See Also
    --------
    ISpinBox

    """
    implements(ISpinBox)

    #===========================================================================
    # ISpinBox interface
    #===========================================================================
    low = Int(0)

    high = Int(100)

    step = Int(1)

    value = Int(0)

    prefix = Str

    suffix = Str

    special_value_text = Str

    to_string = Callable

    from_string = Callable

    wrapping = Bool

    #===========================================================================
    # Implementation
    #===========================================================================
    def create_widget(self, parent):
        """ Creates and binds a wx.SpinCtrl.

        This method is called by the 'layout' method of WXElement.
        It is not meant for public consumption.

        Every change to a wx.SpinCtrl is indicated by a
        wx.EVT_SPINCTRL event

        Arguments
        ---------
        parent : WXContainer
            The WXContainer instance that is our parent.

        Returns
        -------
        result : None

        """
        widget = wx.SpinCtrl(parent.widget)
        widget.Bind(wx.EVT_SPINCTRL, self._on_spin_event)

        self.widget = widget

    #---------------------------------------------------------------------------
    # Initialization
    #---------------------------------------------------------------------------
    def init_attributes(self):
        """ Intializes the widget with the attributes of this
        instance.
        Step is not supported in WX

        This method is called by the 'layout' method of WXElement.
        It is not meant for public consumption.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        """
        self.widget.SetValue(self.value)
        self.widget.SetRange(self.low, self.high)

    def init_meta_handlers(self):
        """ Initializes any meta handlers for this widget.

        This method is called by the 'layout' method of WXElement.
        It is not meant for public consumption.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        """
        pass

    #---------------------------------------------------------------------------
    # Notification
    #---------------------------------------------------------------------------
    def _value_changed(self, value):
        """ The change handler for the 'value' attribute.

        """
        if value < self.low:
            self.value = self.low
        if value > self.high:
            self.value = self.high
            
        self.widget.SetValue(self.value)


    def _low_changed(self):
        ''' The change handle for the 'low' attribute.
        '''
        self.widget.SetRange(self.low, self.high)

    def _high_changed(self):
        ''' The change handle for the 'high' attribute.
        '''
        self.widget.SetRange(self.low, self.high)

    #---------------------------------------------------------------------------
    # Event handling
    #---------------------------------------------------------------------------
    ## prefix, suffix, special_value_text, to_string, from_string,
    ## wrapping not implemented in WX
    
    def _on_spin_event(self, event):
        """ The event handler for the spin control's up event,
        triggered by a click of the up arrow or a press of the
        keyboard up arrow.
        """
        self.value = self.widget.GetValue()
        event.Skip()
