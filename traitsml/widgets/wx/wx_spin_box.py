import sys

import wx
import wx.lib.newevent

from traits.api import implements, Bool, Callable, Int, Str, Range

from .wx_element import WXElement

from ..i_spin_box import ISpinBox


CustomSpinCtrlEvent, EVT_CUSTOM_SPINCTRL = wx.lib.newevent.NewEvent()


class CustomSpinCtrl(wx.SpinCtrl):
    """ A Custom spin control to enable the features of WXSpinBox.

    The standard wx.SpinCtrl doesn't support too many features,
    and the ones it does support are (like wrapping) are limited.
    So, this custom control hard codes the internal range to 
    +- sys.maxint and implements wrapping manually.

    Users should bind to EVT_CUSTOM_SPINCTRL rather than EVT_SPINCTRL.

    XXX - document me better.

    """
    def __init__(self, parent, low=0, high=100, step=1, prefix='', suffix='', 
                 special_value_text='', to_string=None, from_string=None, 
                 wrap=False, **kwargs):
   
        super(CustomSpinCtrl, self).__init__(parent, **kwargs)
        
        self._hard_min = -sys.maxint
        self._hard_max = sys.maxint
        self._last = low
        self._low = low
        self._high = high
        self._step = step
        self._prefix = prefix
        self._suffix = suffix
        self._special_value_text = special_value_text
        self._to_string = to_string or str
        self._from_string = from_string or int
        self._wrap = wrap

        super(CustomSpinCtrl, self).SetRange(self._hard_min, self._hard_max)

        self.Bind(wx.EVT_SPINCTRL, self.OnSpinCtrl)
        
    def GetLow(self):
        return self._low
    
    def GetMin(self):
        return self._low

    def SetLow(self, low):
        if low < self._hard_min:
            raise ValueError('%s too low for CustomSpinCtrl.' % low)
        self._low = low
        if self.GetValue() < low:
            self.SetValue(low)

    def GetHigh(self):
        return self._high
    
    def GetMax(self):
        return self._high

    def SetHigh(self, high):
        if high > self._hard_max:
            raise ValueError('%s too high for CustomSpinCtrl.' % high)
        self._high = high
        if self.GetValue() > high:
            self.SetValue(high)

    def SetRange(self, low, high):
        self.SetLow(low)
        self.SetHigh(high)

    def GetStep(self):
        return self._step

    def SetStep(self, step):
        self._step = step

    def GetPrefix(self):
        return self._prefix

    def SetPrefix(self, prefix):
        self._prefix = prefix

    def GetSuffix(self):
        return self._suffix

    def SetSuffix(self, suffix):
        self._suffix = suffix
    
    def GetSpecialValueText(self):
        return self._special_value_text

    def SetSpecialValueText(self, text):
        self._special_value_text = text

    def GetToString(self):
        return self._to_string

    def SetToString(self, to_string):
        self._to_string = to_string
    
    def GetFromString(self):
        return self._from_string

    def SetFromString(self, from_string):
        self._from_string = from_string
    
    def GetWrap(self):
        return self._wrap
            
    def SetWrap(self, wrap):
        self._wrap = wrap

    def SetValue(self, value):
        if value >= self._low and value <= self._high:
            changed = value != self.GetValue()
            super(CustomSpinCtrl, self).SetValue(value)
            self._last = value
            self.SetValueString(self.ComputeValueString(value))
            if changed:
                evt = CustomSpinCtrlEvent()
                wx.PostEvent(self, evt)

    def ComputeValueString(self, value):
        if value == self._low and self._special_value_text:
            res = self._special_value_text
        else:
            res = self._prefix + self._to_string(value) + self._suffix
        return res

    def OnSpinCtrl(self, event):
        last = self._last
        curr = self.GetValue()
        low = self._low
        high = self._high
        step = self._step
        wrap = self._wrap

        # Compute the proper next value based on wrapping and step.
        # The substraction by one accounts for wraparound.
        if curr < last:
            potential = last - step
            if potential < low:
                if not wrap:
                    computed = low
                else:
                    computed = high - (low - potential - 1) 
            else:
                computed = potential
        elif curr > last:
            potential = last + step
            if potential > high:
                if not wrap:
                    computed = high
                else:
                    computed = (potential - high - 1) + low 
            else:
                computed = potential
        else:
            pass

        self.SetValue(computed)


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

    value = Range('low', 'high')

    prefix = Str

    suffix = Str

    special_value_text = Str

    to_string = Callable(lambda val: str(val))

    from_string = Callable(lambda val: int(val))

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
        widget.Bind(EVT_CUSTOM_SPINCTRL, self._on_custom_spin_ctrl)
        self.widget = widget

    def init_attributes(self):
        """ Intializes the widget with the attributes of this instance.
        
        This method is called by the 'layout' method of WXElement.
        It is not meant for public consumption.

        """
        self.set_spin_low(self.low)
        self.set_spin_high(self.high)
        self.set_spin_step(self.step)
        self.set_spin_prefix(self.prefix)
        self.set_spin_suffix(self.suffix)
        self.set_spin_special_value_text(self.special_value_text)
        self.set_spin_to_string(self.to_string)
        self.set_spin_from_string(self.from_string)
        self.set_spin_wrap(self.wrap)
        self.set_spin_value(self.value)

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
        """ The change handler for the 'value' attribute.

        """
        self.set_spin_value(value)

    def _low_changed(self, low):
        """ The change handler for the 'low' attribute.

        """
        self.set_spin_low(low)

    def _high_changed(self, high):
        """ The change handler for the 'high' attribute.
        
        """
        self.set_spin_high(high)
    
    def _step_changed(self, step):
        """ The change handler for the 'step' attribute.
        
        """
        self.set_spin_step(step)
    
    def _prefix_changed(self, prefix):
        """ The change handler for the 'prefix' attribute.
        
        """
        self.set_spin_prefix(prefix)
    
    def _suffix_changed(self, suffix):
        """ The change handler for the 'suffix' attribute.
        
        """
        self.set_spin_suffix(suffix)
    
    def _special_value_text_changed(self, text):
        """ The change handler for the 'special_value_text' attribute.
        
        """
        self.set_spin_special_value_text(text)
    
    def _to_string_changed(self, to_string):
        """ The change handler for the 'to_string' attribute.
        
        """
        self.set_spin_to_string(to_string)
    
    def _from_string_changed(self, from_string):
        """ The change handler for the 'from_string' attribute.
        
        """
        self.set_spin_from_string(from_string)
    
    def _wrap_changed(self, wrap):
        """ The change handler for the 'wrap' attribute.
        
        """
        self.set_spin_wrap(wrap)

    #---------------------------------------------------------------------------
    # Event handling
    #---------------------------------------------------------------------------
    def _on_custom_spin_ctrl(self, event):
        """ The event handler for the widget's spin event.

        """
        self.value = self.widget.GetValue()
        event.Skip()

    #---------------------------------------------------------------------------
    # Widget Update
    #---------------------------------------------------------------------------
    def set_spin_value(self, value):
        """ Updates the widget with the given value.

        """
        self.widget.SetValue(value)

    def set_spin_low(self, low):
        """ Updates the low limit of the spin box.

        """
        self.widget.SetLow(low)
    
    def set_spin_high(self, high):
        """ Updates the high limit of the spin box.

        """
        self.widget.SetHigh(high)
    
    def set_spin_step(self, step):
        """ Updates the step of the spin box.

        """
        self.widget.SetStep(step)
    
    def set_spin_prefix(self, prefix):
        """ Updates the prefix of the spin box.

        """
        self.widget.SetPrefix(prefix)

    def set_spin_suffix(self, suffix):
        """ Updates the suffix of the spin box.

        """
        self.widget.SetSuffix(suffix)

    def set_spin_special_value_text(self, text):
        """ Updates the special value text of the spin box.

        """
        self.widget.SetSpecialValueText(text)
    
    def set_spin_to_string(self, to_string):
        """ Updates the to_string function of the spin box.

        """
        self.widget.SetToString(to_string)
    
    def set_spin_from_string(self, from_string):
        """ Updates the from_string function of the spin box.

        """
        self.widget.SetFromString(from_string)
    
    def set_spin_wrap(self, wrap):
        """ Updates the wrap value of the spin box.

        """
        self.widget.SetWrap(wrap)

