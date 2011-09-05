import wx
import wx.lib.newevent

from traits.api import implements, Bool, Callable, Int, Str, Range

from .wx_element import WXElement

from ..i_spin_box import ISpinBox


import wx

class CustomSpinCtrl(wx.SpinCtrl):
    def __init__(self, parent, step=1, wrap=False, *args, **kwargs):
        super(CustomSpinCtrl, self).__init__(parent, 
                style=(wx.SP_WRAP | wx.SP_ARROW_KEYS), *args, **kwargs)
        self._step = step
        self._wrap = wrap
        self._last = self.GetValue()
        self.Bind(wx.EVT_SPIN_UP, self._on_spin)
        self.Bind(wx.EVT_SPIN_DOWN, self._on_spin)

    def _on_spin(self, event):
        old_val = self._last
        new_val = event.GetInt()
        delta = new_val - old_val
        low = self.GetMin()
        high = self.GetMax()

        if delta < 0:
            step = -self._step
        elif delta > 0:
            step = self._step
        else:
            raise ValueError

        plan = old_val + step
        value = plan - delta

        print old_val, new_val, delta, plan, value

        if self._wrap:
            if plan < low:
                value = low
                plan = high
            elif plan > high:
                value = high
                plan = low
        else:
            if not low <= plan <= high:
                plan = old_val
                value = old_val - delta

        self.SetValue(value)
        self._last = plan
    
    def _on_set_focus(self, event):
        text = self._special_text

    def SetLow(self, low):
        self.SetRange(low, self.GetMax())
    
    def SetHigh(self, high):
        self.SetRange(self.GetMin(), high)

    def SetStep(self, step):
        self._step = step
    
    def SetWrap(self, should_wrap):
        self._wrap = should_wrap
    
    def SetValue(self, value):
        self._last = value
        super(CustomSpinCtrl, self).SetValue(value)

class WXSpinBox(WXElement):
    """ A wxPython implementation of ISpinBox.

    WXSpinBox uses a custom subclass of wx.SpinCtrl that behaves more
    like Qt's QSpinBox.

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

    value = Range('low', 'high')

    prefix = Str

    suffix = Str

    special_value_text = Str

    to_string = Callable(str)

    from_string = Callable(int)

    wrap = Bool

    #===========================================================================
    # Implementation
    #===========================================================================

    #---------------------------------------------------------------------------
    # Initialization
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates and binds a wx.SpinCtrl.

        This method is called by the 'layout' method of WXElement.
        It is not meant for public consumption.

        """
        widget = CustomSpinCtrl(self.parent_widget())
        widget.Bind(wx.EVT_SPINCTRL, self._on_spin_ctrl)
        widget.Bind(wx.EVT_SET_FOCUS, self._on_set_focus)
        widget.Bind(wx.EVT_KILL_FOCUS, self._on_kill_focus)
        self.widget = widget

    def init_attributes(self):
        """ Intializes the widget with the attributes of this instance.
        
        This method is called by the 'layout' method of WXElement.
        It is not meant for public consumption.

        """
        value = self.value
        self.set_spin_low(self.low)
        self.set_spin_high(self.high)
        self.set_spin_step(self.step)
        self.set_spin_prefix(self.prefix)
        self.set_spin_suffix(self.suffix)
        self.set_spin_wrap(self.wrap)
        self.set_spin_value(self.value)
        self.set_spin_special_value_text(self.special_value_text)
        self.set_spin_value(value)

    def init_meta_handlers(self):
        """ Initializes any meta handlers for this widget.

        This method is called by the 'layout' method of WXElement.
        It is not meant for public consumption.

        """
        pass

    #---------------------------------------------------------------------------
    # Notification
    #---------------------------------------------------------------------------
    def _value_changed(self, value):
        """ The change handler for the 'value' attribute. Not meant
        for public consumption.

        """
        self.set_spin_value(value)

    def _low_changed(self, low):
        """ The change handler for the 'low' attribute. Not meant
        for public consumption.

        """
        self.set_spin_low(low)

    def _high_changed(self, high):
        """ The change handler for the 'high' attribute. Not meant
        for public consumption.
        
        """
        self.set_spin_high(high)
    
    def _step_changed(self, step):
        """ The change handler for the 'step' attribute. Not meant
        for public consumption.
        
        """
        self.set_spin_step(step)
    
    def _prefix_changed(self, prefix):
        """ The change handler for the 'prefix' attribute. Not meant
        for public consumption.
        
        """
        self.set_spin_prefix(prefix)
    
    def _suffix_changed(self, suffix):
        """ The change handler for the 'suffix' attribute. Not meant
        for public consumption.

        """
        self.set_spin_suffix(suffix)
    
    def _special_value_text_changed(self, text):
        """ The change handler for the 'special_value_text' attribute.
        Not meant for public consumption.
        
        """
        self.set_spin_special_value_text(text)
    
    def _to_string_changed(self, to_string):
        """ The change handler for the 'to_string' attribute. Not meant
        for public consumption.
        
        """
        self._update_display()
    
    def _from_string_changed(self, from_string):
        """ The change handler for the 'from_string' attribute. Not meant 
        for public consumption.
        
        """
        self.value = self.from_string(self.widget.GetValue())
    
    def _wrap_changed(self, wrap):
        """ The change handler for the 'wrap' attribute. Not meant for
        public consumption.
        
        """
        self.set_spin_wrap(wrap)

    #---------------------------------------------------------------------------
    # Event handling
    #---------------------------------------------------------------------------
    def _on_spin_ctrl(self, event):
        """ The event handler for the widget's spin event. Not meant
        for public consumption.

        """
        value = self.widget.GetValue()
        self._update_display()
        self.value = self.from_string(value)
    
    def _update_display(self):
        text = self.to_string(self.widget.GetValue())
        self.widget.SetValueString(self.prefix + text + self.suffix)

    def _on_set_focus(self, event):
        self._update_display()

    def _on_kill_focus(self, event):
        self.show_special_text()

    def show_special_text(self):
        widget = self.widget
        if self.value == widget.GetMin():
            text = self.special_value_text
            if text:
                widget.SetValueString(text)

    #---------------------------------------------------------------------------
    # Widget Update
    #---------------------------------------------------------------------------
    def set_spin_value(self, value):
        """ Updates the widget with the given value. Not meant for 
        public consumption.

        """
        self.widget.SetValue(value)
        self._update_display()

    def set_spin_low(self, low):
        """ Updates the low limit of the spin box. Not meant for 
        public consumption.

        """
        self.widget.SetLow(low)
        self.set_spin_value(self.widget.GetValue())
    
    def set_spin_high(self, high):
        """ Updates the high limit of the spin box. Not meant for 
        public consumption.

        """
        self.widget.SetHigh(high)
        self.set_spin_value(self.widget.GetValue())
    
    def set_spin_step(self, step):
        """ Updates the step of the spin box. Not meant for public
        consumption.

        """
        self.widget.SetStep(step)
    
    def set_spin_prefix(self, prefix):
        """ Updates the prefix of the spin box. Not meant for public
        consumption.

        """
        self._update_display()

    def set_spin_suffix(self, suffix):
        """ Updates the suffix of the spin box. Not meant for public
        consumption.

        """
        self._update_display()

    def set_spin_special_value_text(self, text):
        """ Updates the special value text of the spin box. Not meant
        for public consumption.

        """
        self.show_special_text()
    
    def set_spin_wrap(self, wrap):
        """ Updates the wrap value of the spin box. Not meant for public
        consumption.

        """
        self.widget.SetWrap(wrap)

    #---------------------------------------------------------------------------
    # Layout helpers
    #---------------------------------------------------------------------------
    def default_sizer_flags(self):
        """ Updates the default flags to have a proportion of 1.

        """
        return super(WXSpinBox, self).default_sizer_flags().Proportion(1)

