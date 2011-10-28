#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx
import wx.lib.newevent

from .wx_control import WXControl
from ..spin_box import AbstractTkSpinBox


# The new changed event for the custom spin ctrl.
CustomSpinCtrlEvent, EVT_CUSTOM_SPINCTRL = wx.lib.newevent.NewEvent()


class CustomSpinCtrl(wx.SpinCtrl):
    """ A custom wx spin control that acts more like QSpinBox.

    The standard wx.SpinCtrl doesn't support too many features, and
    the ones it does support are (like wrapping) are limited. So,
    this custom control hard codes the internal range to the maximum
    range of the wx.SpinCtrl and implements wrapping manually.

    For changed events, users should bind to EVT_CUSTOM_SPINCTRL
    rather than EVT_SPINCTRL.

    See the method docstrings for supported functionality.

    """
    def __init__(self, parent, low=0, high=100, step=1, prefix='', suffix='',
                 special_value_text='', to_string=None, from_string=None,
                 wrap=False):
        """ CustomSpinCtrl constructor.

        Arguments
        ---------
        parent : wxWindow
            The parent of the spin ctrl.

        low : int, optional
            The minimum value of spin ctrl. Defaults to 0.

        high : int, optional
            The maximum value of the spin ctrl. Defaults to 100.

        step : int, optional
            The step amount to use for the spin ctrl. Defaults to 1.

        prefix : string, optional
            A prefix to place in front of the value in the ctrl.

        suffix : string, optional
            A suffix to place behind the value in the ctrl.

        special_value_text : string, optional
            The text to display when the control is at its minimum
            value, if different from the normal value.

        to_string : callable, optional
            A function to convert the integer spin value to a string
            for display. Should not include prefix and suffix.

        from_string : callable, optional
            A function to convert a string input by the user into
            an integer spin value.

        wrap : bool, optional
            A flag indicating whether the spin ctrl should wrap
            at the ends.

        """
        # The max range of the wx.SpinCtrl is the range of a signed
        # 32bit integer. We don't care about wx's internal value of
        # the control, since we maintain our own internal counter.
        # and because the internal value of the widget gets reset to
        # the minimum of the range whenever SetValueString is called.
        #
        # XXX - look into using a wx.PyValidator for this
        self._hard_min = -(1 << 31)
        self._hard_max = (1 << 31) - 1
        self._internal_value = low
        self._user_text = ''
        self._low = low
        self._high = high
        self._step = step
        self._prefix = prefix
        self._suffix = suffix
        self._special_value_text = special_value_text
        self._to_string = to_string or str
        self._from_string = from_string or int
        self._wrap = wrap
        self._spin_state = None

        super(CustomSpinCtrl, self).__init__(parent)
        super(CustomSpinCtrl, self).SetRange(self._hard_min, self._hard_max)

        self.Bind(wx.EVT_SPIN_UP, self.OnSpinUp)
        self.Bind(wx.EVT_SPIN_DOWN, self.OnSpinDown)
        self.Bind(wx.EVT_SPINCTRL, self.OnSpinCtrl)
        self.Bind(wx.EVT_TEXT, self.OnText)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)

    def OnKillFocus(self, event):
        """ The spin control doesn't emit a spin event when losing focus
        to process typed input change unless it results in a different
        value, so we have to handle it manually and update the control
        again after the event. And it must be on a CallAfter or it doesn't
        work.

        """
        event.Skip()
        # The lambda fixes a DeadObjectError if the app
        # is closed before the callback executes.
        wx.CallAfter(lambda: self.Update() if self else None)

    def OnText(self, event):
        """ Handles the text event of the spin control to store away the
        user typed text for later conversion.

        """
        self._user_text = event.GetString()
        event.Skip()

    def OnSpinUp(self, event):
        """ The event handler for the spin up event. We veto the spin
        event to prevent the control from changing it's internal value.
        Instead, we maintain complete control of the value.

        """
        event.Veto()
        self._spin_state = 'up'
        self.OnSpinCtrl(event)
        self._spin_state = None

    def OnSpinDown(self, event):
        """ The event handler for the spin down event. We veto the spin
        event to prevent the control from changing it's internal value.
        Instead, we maintain complete control of the value.

        """
        event.Veto()
        self._spin_state = 'down'
        self.OnSpinCtrl(event)
        self._spin_state = None

    def OnSpinCtrl(self, event):
        """ Handles the spin control being changed by user interaction.
        All of the manual stepping and wrapping logic is computed by
        this method.

        """
        last = self._internal_value
        low = self._low
        high = self._high
        step = self._step
        wrap = self._wrap
        spin_state = self._spin_state

        if spin_state == 'down':
            potential = last - step
            if potential < low:
                if not wrap:
                    computed = low
                else:
                    computed = high - (low - potential - 1)
            else:
                computed = potential
        elif spin_state == 'up':
            potential = last + step
            if potential > high:
                if not wrap:
                    computed = high
                else:
                    computed = (potential - high - 1) + low
            else:
                computed = potential
        else:
            # The user typed a value, and we need to convert the
            # stored text into an int. Bailing to the last value
            # if conversion fails.
            try:
                potential = self._from_string(self._user_text)
            except Exception:
                potential = last
            finally:
                self._user_text = ''
            if low <= potential <= high:
                computed = potential
            else:
                computed = last

        self.SetValue(computed)

    def GetLow(self):
        """ Returns the minimum value of the control.

        """
        return self._low

    def GetMin(self):
        """ Equivalent to GetLow().

        """
        return self._low

    def SetLow(self, low):
        """ Sets the minimum value of the control and changes the
        value to the min if the current value would be out of range.

        """
        if low < self._hard_min:
            raise ValueError('%s too low for CustomSpinCtrl.' % low)
        self._low = low
        if self.GetValue() < low:
            self.SetValue(low)

    def GetHigh(self):
        """ Returns the maximum value of the control.

        """
        return self._high

    def GetMax(self):
        """ Equivalent to GetHigh().

        """
        return self._high

    def SetHigh(self, high):
        """ Sets the maximum value of the control and changes the
        value to the max if the current value would be out of range.

        """
        if high > self._hard_max:
            raise ValueError('%s too high for CustomSpinCtrl.' % high)
        self._high = high
        if self.GetValue() > high:
            self.SetValue(high)

    def SetRange(self, low, high):
        """ Sets the low and high values of the control.

        """
        self.SetLow(low)
        self.SetHigh(high)

    def GetStep(self):
        """ Returns the step size of the control.

        """
        return self._step

    def SetStep(self, step):
        """ Sets the step size of the control.

        """
        self._step = step

    def GetPrefix(self):
        """ Returns the prefix of the control.

        """
        return self._prefix

    def SetPrefix(self, prefix):
        """ Sets the prefix of the control.

        """
        self._prefix = prefix
        self.Update()

    def GetSuffix(self):
        """ Returns the suffix of the control.

        """
        return self._suffix

    def SetSuffix(self, suffix):
        """ Sets the suffix of the control.

        """
        self._suffix = suffix
        self.Update()

    def GetSpecialValueText(self):
        """ Returns the special value text of the control.

        """
        return self._special_value_text

    def SetSpecialValueText(self, text):
        """ Sets the special value text of the control.

        """
        self._special_value_text = text
        self.Update()

    def GetToString(self):
        """ Returns the to_string converter of the control.

        """
        return self._to_string

    def SetToString(self, to_string):
        """ Sets the to_string converter of the control.

        """
        self._to_string = to_string
        self.Update()

    def GetFromString(self):
        """ Returns the from_string converter of the control.

        """
        return self._from_string

    def SetFromString(self, from_string):
        """ Sets the from_string converter of the control.

        """
        self._from_string = from_string
        self.Update()

    def GetWrap(self):
        """ Gets the wrap flag of the control.

        """
        return self._wrap

    def SetWrap(self, wrap):
        """ Sets the wrap flag of the control.

        """
        self._wrap = wrap

    def GetValue(self):
        """ Returns the internal integer value of the control.

        """
        return self._internal_value

    def SetValue(self, value):
        """ Sets the value of the control to the given value, provided
        that the value is within the range of the control. If the
        given value is within range, and is different from the current
        value of the control, an EVT_CUSTOM_SPINCTRL will be emitted.

        """
        if self._low <= value <= self._high:
            if self._internal_value != value:
                self._internal_value = value
                self.Update()
                evt = CustomSpinCtrlEvent()
                wx.PostEvent(self, evt)

    def Update(self):
        """ Trigger an update of the displayed string value. Should not
        need to be called directly by the user.

        """
        self.SetValueString(self.ComputeValueString(self.GetValue()))

    def ComputeValueString(self, value):
        """ Computes the string that will be displayed in the control
        for the given value.

        """
        if value == self._low and self._special_value_text:
            res = self._special_value_text
        else:
            res = self._prefix + self._to_string(value) + self._suffix
        return res


class WXSpinBox(WXControl, AbstractTkSpinBox):
    """ A wxPython implementation of SpinBox.

    WXSpinBox uses a custom subclass of wx.SpinCtrl that behaves more
    like Qt's QSpinBox.

    See Also
    --------
    SpinBox

    """
    def create(self):
        """ Creates the underlying custom spin control.

        """
        self.widget = widget = CustomSpinCtrl(self.parent_widget())
        widget.SetDoubleBuffered(True)

    def initialize(self):
        """ Intializes the widget with the attributes of this instance.

        """
        super(WXSpinBox, self).initialize()
        shell = self.shell_obj
        self.set_spin_low(shell.low)
        self.set_spin_high(shell.high)
        self.set_spin_step(shell.step)
        self.set_spin_prefix(shell.prefix)
        self.set_spin_suffix(shell.suffix)
        self.set_spin_special_value_text(shell.special_value_text)
        self.set_spin_converter(shell.converter)
        self.set_spin_wrap(shell.wrap)
        self.set_spin_value(shell.value)

    def bind(self):
        """ Binds the event handlers for the spin control.

        """
        super(WXSpinBox, self).bind()
        self.widget.Bind(EVT_CUSTOM_SPINCTRL, self.on_custom_spin_ctrl)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def shell_value_changed(self, value):
        """ The change handler for the 'value' attribute.

        """
        self.set_spin_value(value)

    def shell_low_changed(self, low):
        """ The change handler for the 'low' attribute.

        """
        self.set_spin_low(low)

    def shell_high_changed(self, high):
        """ The change handler for the 'high' attribute.

        """
        self.set_spin_high(high)

    def shell_step_changed(self, step):
        """ The change handler for the 'step' attribute.

        """
        self.set_spin_step(step)

    def shell_prefix_changed(self, prefix):
        """ The change handler for the 'prefix' attribute.

        """
        self.set_spin_prefix(prefix)

    def shell_suffix_changed(self, suffix):
        """ The change handler for the 'suffix' attribute.

        """
        self.set_spin_suffix(suffix)

    def shell_special_value_text_changed(self, text):
        """ The change handler for the 'special_value_text' attribute.
        Not meant for public consumption.

        """
        self.set_spin_special_value_text(text)

    def shell_converter_changed(self, converter):
        """ The change handler for the 'converter' attribute.

        """
        self.set_spin_converter(converter)

    def shell_wrap_changed(self, wrap):
        """ The change handler for the 'wrap' attribute.

        """
        self.set_spin_wrap(wrap)

    def on_custom_spin_ctrl(self, event):
        """ The event handler for the widget's spin event.

        """
        self.shell_obj.value = self.widget.GetValue()
        event.Skip()

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

    def set_spin_converter(self, converter):
        """ Updates the 'to_string' and 'from_string' functions of the
        spin box. Not meant for public consumption.

        """
        self.widget.SetFromString(converter.from_component)
        self.widget.SetToString(converter.to_component)

    def set_spin_wrap(self, wrap):
        """ Updates the wrap value of the spin box.

        """
        self.widget.SetWrap(wrap)

